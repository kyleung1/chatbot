import json
import certifi
import os
from pymongo import MongoClient
from difflib import get_close_matches
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv('mongo_uri'), tlsCAFile=certifi.where())
db = client["chatbot"]
collection = db["questions"]

# collection.insert_one({"question": "", "answer": ""})
collection.insert_one({"question": "how old are you", "answer": "I was born in 2001"})
client.close()