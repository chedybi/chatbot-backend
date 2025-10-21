# logic/locations.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["foire_db"]
collection = db["programmes_foire_2023"]

def get_location_info():
    # Exemple : récupérer tous les lieux uniques
    lieux = collection.distinct("lieu")
    return {"lieux": lieux}
