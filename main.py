from fastapi import FastAPI, Query
import ollama
# from langchain_ollama import OllamaEmbeddings
import pymongo
import urllib.parse
# from llama_index.core import VectorStoreIndex
# from langchain_nomic.embeddings import NomicEmbeddings
import requests
from langchain_community.document_loaders.mongodb import MongodbLoader
import os
import json
from typing import Optional
import os
import json
import requests
from bs4 import BeautifulSoup
import re
import uuid
from dotenv import load_dotenv



load_dotenv()  # Loads environment variables from .env file

#my credientials for mongodb atlas
username = os.environ.get("MONGODB_USERNAME")
password = os.environ.get("MONGODB_PASSWORD")

#The URL for my mongodb database
url= f"mongodb+srv://{username}:{password}@cluster0.yy5c5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

#creating the database session
myclient = pymongo.MongoClient(url)
db = myclient["RAG_AI_APPLICATION"]  # Database name
collection = db["SNOWFLAKE_DOC"]  # Collection name

app = FastAPI()

#scraper code start
def fetch_snowflake_docs(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_links(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if href.startswith('/en/') and 'docs.snowflake.com' not in href:
            links.add(base_url + href)
    return links

def sanitize_filename(name):
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', name).strip('_')[:100]
    sanitized_again = re.sub('[¶]', '', sanitized)
    return sanitized_again

def parse_docs(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    title_tag = soup.find('h1')
    page_title = title_tag.get_text().strip() if title_tag else "Untitled"
    sanitized_title = sanitize_filename(page_title)

    sections = []
    current_section = {"section": page_title, "sectionId": str(uuid.uuid4()), "paragraphs": []}

    for element in soup.find_all(['h1', 'h2', 'h3', 'p']):
        if element.name in ['h1', 'h2', 'h3']:
            if current_section["paragraphs"]:
                sections.append(current_section)
            current_section = {
                "section": element.get_text().strip(),
                "sectionId": str(uuid.uuid4()),
                "paragraphs": []
            }
        elif element.name == 'p' and element.get_text().strip():
            current_section["paragraphs"].append(element.get_text().strip())

    if current_section["paragraphs"]:
        sections.append(current_section)

    return {
        "guid": str(uuid.uuid4()),
        "title": page_title,
        "path": f"docs/{sanitized_title}.md",
        "fullText": "\n".join([" ".join(sec["paragraphs"]) for sec in sections]),
        "headers": [[h.name, h.get_text().strip()] for h in soup.find_all(['h1', 'h2', 'h3'])],
        "sections": sections,
        "url": url,
        "tags": generate_tags(page_title)
    }

def generate_tags(title):
    keywords = title.lower().split()
    common_tags = ["sql", "syntax", "query", "commands", "functions"]
    return list(set([word.capitalize() for word in keywords if word in common_tags]))

def save_page(page_data, output_dir="snowflake_docs"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filename = f"{output_dir}/{sanitize_filename(page_data['title'])}.json"
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(page_data, file, indent=4)
    print(f"Saved: {filename}")

def scrape_all_docs(start_url: str):
    base_url = "https://docs.snowflake.com"
    visited = set()
    to_visit = {start_url}

    while to_visit:
        current_url = to_visit.pop()
        if current_url in visited:
            continue
        print(f"Scraping: {current_url}")
        html = fetch_snowflake_docs(current_url)
        if html:
            try:
                visited.add(current_url)
                page_data = parse_docs(html, current_url)
                save_page(page_data)
                to_visit.update(extract_links(html, base_url))
            except Exception as e:
                print(f"Error processing {current_url}: {e}")
                continue

# scraper code end

#rag cod start

def sendQuery(query, myclient):

#Embedding the question
 res = ollama.embeddings(
  prompt = query,
  model = 'nomic-embed-text'
 )
# creating the pipeline or "query"
 pipeline = [{
  "$vectorSearch": {
    "exact": False,
    "index": "vector_index",
    "limit": 5,
    "numCandidates": 4800,
    "path": "embedding",
    "queryVector": res["embedding"]
   }
  },      
    {
     "$project": {
       "_id": 0, 
       "plot": 1, 
       "title": 1,
       "page_content":1,
       "score": {
         '$meta': 'vectorSearchScore'
        }
       }
    }  
 ]

 result = myclient['RAG_AI_APPLICATION']['SNOWFLAKE_DOC'].aggregate(pipeline=pipeline)

 text_arr=''
 response_arr =[]
 counter = 0

 for i in result:
  response_arr.append(i)
  text_arr = text_arr + str(i['page_content'])

 res = str(response_arr)
 print("This is a paragraph from the snowflake documentation that may answer your question while the LLM learns relevant documentation data: "+ '\n' + text_arr)

 def chat_funct(response_arr, query):
   context_statement = f'this is context for the prompt: {response_arr}, can you answer this question? {query}'
   stream = ollama.chat(
    model='llama3.2',
    messages=[{'role':'user','content':context_statement}],
    stream=True
   )

   string =''
   print("Loading........")
   for chunk in stream:
     string += chunk["message"]["content"]
   return string
 
 
 return chat_funct(response_arr=res,query=query)
#rag code end

@app.post('/question')
async def question(query):
   if query is None:
     return "This endpoint recieved an empty query"
   # if response.status_code != 200:
   #   response.status_code = 422
   #   return {"message":"There is something wrong with your query", "response.status_code":response.status_code}
   response = sendQuery(query=query, myclient=myclient)
   return str(response)

@app.delete('/delete')
async def delete():
  collection.delete_many({}) 

@app.get('/load_data')
async def load_data():
  loader = MongodbLoader(
    connection_string=url,
    db_name='RAG_AI_APPLICATION',
    collection_name='SNOWFLAKE_DOC',
    filter_criteria={},
  )
  docs = loader.load()

  DB_NAME = myclient["RAG_AI_APPLICATION"]
  COLLECTION_NAME = DB_NAME["SNOWFLAKE_DOC"]
  ATLAS_VECTOR_SEARCH_INDEX_NAME = "vector_index"

  base_dir ='./snowflake_docs/'
  docs_to_be_loaded = []
  errors = []
  section_count = 0
  page_count = 0

  for file in os.listdir(base_dir):
    print(file)
    json_path = os.path.join(base_dir, file)
    f = open('snowflake_docs/'+file, encoding="utf8")
    json_data = json.load(f)
    uuid = json_data['guid']
    title =json_data['title']
    full_text = json_data['fullText']
    sections = json_data['sections']
    page_count = page_count + 1
    print("page_count :    " + str(page_count))

    data={"model":"nomic-embed-text","prompt":full_text}
    data_json = json.dumps(data)

    res = requests.post("http://localhost:11434/api/embeddings", data=data_json)

    embedding = res.json()
    if  embedding == False:
      embedding = {"embedding":[]}

    try:
        doc ={          
        # "uuid" : section_id,
        "page_content":full_text,
        # "title" : section_name,
        "embedding":  embedding["embedding"],
        "page_count":page_count,
        # "section_count":section_count,
        "metadata":{
        "source":"SNOWFLAKE DOCUMENTATION",
        "page_count":page_count,
        }
        }
        myclient["RAG_AI_APPLICATION"]["SNOWFLAKE_DOC"].insert_one(document=doc)
    except:
        err_obj = json.dumps({"error":"unable to create doc","page":page_count})
        errors.append(err_obj)
    finally:
      continue

@app.get('/scrape')
async def scrape_docs(start_url: Optional[str] = Query("https://docs.snowflake.com", description="Start URL for scraping")):
    scrape_all_docs(start_url)
    return {"message": "Scraping completed", "start_url": start_url}    

@app.get("/")
async def root():
    return {"message": "Hello World"}





