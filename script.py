import json
import certifi
from pymongo import MongoClient
from difflib import get_close_matches

client = MongoClient("", tlsCAFile=certifi.where())
db = client["chatbot"]
collection = db["questions"]

collection.insert_one({"question": "", "answer": ""})
client.close()