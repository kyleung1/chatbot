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

class Questions(BaseModel):
    question: str
    answer: str

# class LearnedQuestions(BaseModel):
#     question: str
#     answer: str

def getAllQuestions() -> list[Questions]:
    client = MongoClient(os.getenv('mongo_uri'), tlsCAFile=certifi.where())
    db = client["chatbot"]
    collection = db["questions"]
    # collection.insert_one({"question": "", "answer": ""})
    datas = collection.find()
    data = [question for question in datas]
    client.close()
    return data

def load_LearnedQuestions(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        data: dict = json.load(file)
    return data

def find_best_match(user_question: str, questions: list[str]) -> str | None:
    matches: list = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None

def get_answer_for_question(question: str, LearnedQuestions: dict) -> str | None:
    for q in LearnedQuestions["questions"]:
        if q["question"] == question:
            return q["answer"]

@app.get("/")
def index() -> list[Questions]:
    data = getAllQuestions()
    return data

@app.post("/")
def getResponse(user_msg: str, teach: bool) -> str:
    answer: str = ""
    if teach == False:
        LearnedQuestions: dict = load_LearnedQuestions('LearnedQuestions.json')

        best_match: str | None = find_best_match(user_msg, [q["question"] for q in LearnedQuestions])
        

        if best_match:
            answer = get_answer_for_question(best_match, LearnedQuestions)
        else:
            answer = "I'm not too sure about this, could you tell me how to answer this?"
    else:
        LearnedQuestions["questions"].append({"question": user_msg, "answer": ""})
    return answer

# uvicorn main:app --reload to get the server started

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
