import json
import certifi
import os

from enum import Enum
from pydantic import BaseModel

from pymongo import MongoClient
from difflib import get_close_matches
from fastapi import FastAPI
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()

@app.get("/")
def getAllQuestions() -> dict[str]:
    print(os.getenv('mongo_uri'))
    client = MongoClient(os.getenv('mongo_uri'), tlsCAFile=certifi.where())
    db = client["chatbot"]
    collection = db["questions"]
    # collection.insert_one({"question": "", "answer": ""})
    datas = collection.find()
    # print(datas)
    # data = [question for question in datas]
    # print(data)
    client.close()
    return datas