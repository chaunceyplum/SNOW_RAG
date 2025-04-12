import os
from langchain_community.document_loaders.mongodb import MongodbLoader
import urllib.parse
import pymongo
import ollama
import json
import requests
## CONNECTION TO MONGODB
username 
password 
url= f"mongodb+srv://{username}:{password}@cluster0.yy5c5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
myclient = pymongo.MongoClient(url)

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
  f =open('snowflake_docs/'+file, encoding="utf8")
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