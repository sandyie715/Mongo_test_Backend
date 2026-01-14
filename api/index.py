import os
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# import uvicorn

from pymongo import MongoClient
from bson import ObjectId

load_dotenv()

app = FastAPI(title= "Mongo Connection Testing")

USER_NAME=os.getenv("USER_NAME")
PASSWORD=os.getenv("PASSWORD")

MONGO_URL=f"mongodb+srv://{USER_NAME}:{PASSWORD}@testing.fyevyj5.mongodb.net/?appName=Testing"


# FRONTEND_URL = os.getenv("FRONTEND_URL")
# MONGO_URL = os.getenv("MONGODB_URL")
DB_NAME = os.getenv("DB_NAME")

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# ======== DB CONNECTION ================
client = MongoClient(MONGO_URL)
db = client[DB_NAME]
notes_collection = db["notes"]

# ======= Models ====================
class Note(BaseModel):
    title: str
    content: str


# ------------ Helpers ------------------
def note_serializer(note):
    return {
        "id" : str(note["_id"]),
        "title": note["title"],
        "content": note["content"],
    }

@app.get("/")
def root():
    return {"Message": "Api is Working"}

# CREATE (POST)
@app.post("/notes")
def create_note(note: Note):
    result = notes_collection.insert_one(note.dict())
    return {"id": str(result.inserted_id)}

@app.get("/notes")
def get_notes():
    notes = notes_collection.find()
    return [note_serializer(n) for n in notes]

@app.put("/notes/{note_id}")
def update_note(note_id: str, note: Note):
    result = notes_collection.update_one(
        {"_id": ObjectId(note_id)},
        {"$set": note.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail= "Note not found")
    return {"Message": "Note updated"}

@app.delete("/notes/{note_id}")
def delete_note(note_id: str):
    result = notes_collection.delete_one({"_id": ObjectId(note_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail= "Note not found")
    return {"message": "Note Deleted"}

# if __name__ == "__main__":
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8000
#     )
    