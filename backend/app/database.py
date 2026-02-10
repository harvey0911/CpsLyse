import os
from pymongo import MongoClient
from dotenv import load_dotenv

from pathlib import Path

env_path = Path(__file__).resolve().parent.parent.parent / '.env'
if not env_path.exists():
    env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

def get_mongo_uri():
    user = os.getenv("MONGO_USER", "admin")
    password = os.getenv("MONGO_PASSWORD", "password123")
    host = os.getenv("MONGO_HOST", "mongodb")
    port = os.getenv("MONGO_PORT", "27017")
    return f"mongodb://{user}:{password}@{host}:{port}/?authSource=admin"

def get_db():
    client = MongoClient(get_mongo_uri())
    db_name = os.getenv("MONGO_DB", "cpslyse_db")
    return client[db_name]

def init_db():
    print("Initializing MongoDB connection...")
    try:
        client = MongoClient(get_mongo_uri(), serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("MongoDB connection successful.")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")

if __name__ == "__main__":
    init_db()