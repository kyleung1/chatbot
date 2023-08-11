import json
import certifi
import os
import random

from enum import Enum
from pydantic import BaseModel

from pymongo import MongoClient
from difflib import get_close_matches
from fastapi import FastAPI
from dotenv import load_dotenv
from typing import List
from fastapi.responses import JSONResponse

app = FastAPI()

load_dotenv()

class Questions(BaseModel):
    question: str
    answer: str

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

# takes the session id and returns all the chatlogs of that id in a dictionary
def getChatlogs(session_id: int) -> dict:
    client = MongoClient(os.getenv('mongo_uri'), tlsCAFile=certifi.where())
    db = client["chatbot"]
    collection = db["chatlogs"]
    datas = collection.find_one({"session_id": session_id})
    client.close()
    return datas

# takes a chatlog dictionary and inserts it into the chatlogs collection
def insertChatlog(chatlog: dict):
    client = MongoClient(os.getenv('mongo_uri'), tlsCAFile=certifi.where())
    db = client["chatbot"]
    collection = db["chatlogs"]
    collection.insert_one(chatlog)
    client.close()

# takes the session id and the entire updated chatlog object returned from pymongo and updates it in db
def updateChatlog(session_id: int, new_chatlog: dict):
    client = MongoClient(os.getenv('mongo_uri'), tlsCAFile=certifi.where())
    db = client["chatbot"]
    collection = db["chatlogs"]
    collection.update_one({"session_id": session_id}, {"$set": new_chatlog})
    client.close()

# takes the session id and returns all the learned questions of that id in a dictionary
def getLearnedQuestions(session_id: int) -> dict[dict]:
    client = MongoClient(os.getenv('mongo_uri'), tlsCAFile=certifi.where())
    db = client["chatbot"]
    collection = db["learned_questions"]
    datas = collection.find_one({"session_id": session_id})
    client.close()
    return datas

# takes a learned questions dictionary and inserts it into the learned_questions collection
def insertLearnedQuestions(question: dict):
    client = MongoClient(os.getenv('mongo_uri'), tlsCAFile=certifi.where())
    db = client["chatbot"]
    collection = db["learned_questions"]
    collection.insert_one(question)
    client.close()

# takes the session id and the entire updated learned questions object returned from pymongo and updates
def updateLearnedQuestions(session_id: int, new_question: dict):
    client = MongoClient(os.getenv('mongo_uri'), tlsCAFile=certifi.where())
    db = client["chatbot"]
    collection = db["learned_questions"]
    collection.update_one({"session_id": session_id}, {"$set": new_question})
    client.close()

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

# takes a question and the entire learned questions dicitonary and returns the answer for that question
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
def getResponse(user_msg: str, session: int | None = None) -> str:

    session_json = load_JSON('Session.json')
    if session is None and session not in session_json['session_id']:
        session = random.randint(1,10000)
        session_json['session_id'].append(session)
        write_JSON('Session.json', session_json)
    
    answer: str = ""
    
    data = getAllQuestions()
    LearnedQuestions: dict | None = getLearnedQuestions(session)
    ChatLog: dict | None = getChatlogs(session)

    if LearnedQuestions is None:
        LearnedQuestions = {'session_id': session, 'questions': []}
        insertLearnedQuestions(LearnedQuestions)

    if ChatLog is None:
        ChatLog = {'session_id': session, 'user_chatlog': []}
        insertChatlog(ChatLog)

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
        updateChatlog(session, ChatLog)
    elif prev_msg and prev_msg['answered'] == False:
        answer = "Alright I got it, ask me again"
        ChatLog['user_chatlog'].append({"msg": user_msg, "answered": True})
        updateChatlog(session, ChatLog)
        LearnedQuestions["questions"].append({"question": prev_msg['msg'], "answer": user_msg})
        updateLearnedQuestions(session, LearnedQuestions)
    else:
        answer = "I'm not too sure about this, could you tell me how to answer this?"
        ChatLog['user_chatlog'].append({"msg": user_msg, "answered": False})
        updateChatlog(session, ChatLog)

    return JSONResponse({"answer": answer, "session": session})

# uvicorn main:app --reload to get the server started
# http://127.0.0.1:8000/docs to open fast api testing ui

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
