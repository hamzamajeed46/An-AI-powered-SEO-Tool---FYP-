from pymongo import MongoClient
import os

def get_db():
    client = MongoClient(os.getenv("MONGODB_URI", "mongodb://mongo:27017/"))
    db = client["seo_tool"]
    return db
