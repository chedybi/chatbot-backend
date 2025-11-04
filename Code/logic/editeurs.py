# logic/editeurs.py

from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["chatbotEvent"]
editeurs_collection = db["editeurs_foire"]

def get_publishers_info():
    return list(editeurs_collection.find({}, {"_id": 0}))
