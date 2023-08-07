import json
import certifi
import os

from enum import Enum
from pydantic import BaseModel

from pymongo import MongoClient
from difflib import get_close_matches
from fastapi import FastAPI
from dotenv import load_dotenv
from typing import List

app = FastAPI()

load_dotenv()

class Questions(BaseModel):
    question: str
    answer: str

# class LearnedQuestions(BaseModel):
#     question: str
#     answer: str

# returns a list of question dictionaries with question and answers
def getAllQuestions() -> List[Questions]:
    client = MongoClient(os.getenv('mongo_uri'), tlsCAFile=certifi.where())
    db = client["chatbot"]
    collection = db["questions"]
    # collection.insert_one({"question": "", "answer": ""})
    datas = collection.find()
    data = [question for question in datas]
    client.close()
    return data

# takes a file path string and returns a dictionary of JSON
def load_JSON(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        data: dict = json.load(file)
    return data

# replace json file with new json file that has appended data
def write_JSON(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

# takes the user's question, and a list of questions only and returns the best question string
def find_best_match(user_question: str, questions: List[str]) -> str | None:
    matches: list = get_close_matches(user_question, questions, n=1, cutoff=0.8)
    return matches[0] if matches else None

#takes a question and the entire learned questions dicitonary and returns the answer for that question
def get_answer_for_question(question: str, LearnedQuestions: dict) -> str | None:
    for q in LearnedQuestions["questions"]:
        if q["question"] == question:
            return q["answer"]

# this api route gets all questions in the mongo database
@app.get("/")
def index() -> List[Questions]:
    data = getAllQuestions()
    return data

@app.post("/")
def getResponse(user_msg: str) -> str:
    answer: str = ""
    
    data = getAllQuestions()
    LearnedQuestions: dict = load_JSON('LearnedQuestions.json')
    ChatLog: dict = load_JSON('ChatLog.json')

    best_match: str | None = find_best_match(user_msg, [q['question'] for q in data])
    if best_match == None:
            best_match: str | None = find_best_match(user_msg, [q["question"] for q in LearnedQuestions['questions']])
    prev_msg: dict | None = None
    
    print(best_match)

    if len(ChatLog['user_chatlog']) > 0:
        prev_msg = ChatLog['user_chatlog'][-1]
    
    if best_match:
        answer = get_answer_for_question(best_match, {'questions': data})
        if answer == None:
            answer = get_answer_for_question(best_match, LearnedQuestions)
        ChatLog['user_chatlog'].append({"msg": user_msg, "answered": True})
        write_JSON("ChatLog.json", ChatLog)
    elif prev_msg and prev_msg['answered'] == False:
        answer = "Alright I got it, ask me again"
        ChatLog['user_chatlog'].append({"msg": user_msg, "answered": True})
        write_JSON("ChatLog.json", ChatLog)
        LearnedQuestions["questions"].append({"question": prev_msg['msg'], "answer": user_msg})
        write_JSON("LearnedQuestions.json", LearnedQuestions)
    else:
        answer = "I'm not too sure about this, could you tell me how to answer this?"
        ChatLog['user_chatlog'].append({"msg": user_msg, "answered": False})
        write_JSON("ChatLog.json", ChatLog)

    return answer

# uvicorn main:app --reload to get the server started
# http://127.0.0.1:8000/docs to open fast api testing ui

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
