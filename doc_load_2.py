import os
import json
from pymongo import MongoClient

# MongoDB Connection
client = MongoClient("mongodb+srv://username:password@cluster0.yy5c5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # Replace with your MongoDB URI
db = client["RAG_AI_APPLICATION"]  # Database name
collection = db["SNOWFLAKE_DOC"]  # Collection name


collection.delete_many({}) 

# # Folder containing JSON files
# json_folder = "snowflake_docs"

# # Collect all JSON documents
# documents = []

# for filename in os.listdir(json_folder):
#     if filename.endswith(".json"):
#         file_path = os.path.join(json_folder, filename)
#         with open(file_path, "r", encoding="utf-8") as file:
#             try:
#                 data = json.load(file)
#                 documents.append(data)
#             except Exception as e:
#                 print(f"Error reading {filename}: {e}")

# # Batch insert
# if documents:
#     try:
#         collection.insert_many(documents, ordered=False)  # 'ordered=False' allows it to continue on errors
#         print(f"Inserted {len(documents)} documents successfully!")
#     except Exception as e:
#         print(f"Error inserting documents: {e}")
