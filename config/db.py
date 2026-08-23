import os
from pymongo import MongoClient

_db_instance = None

def get_db():
    global _db_instance
    if _db_instance is None:
        mongo_uri = os.environ.get("MONGO_URI")
        if not mongo_uri:
            print("Warning: MONGO_URI is not set in environment variables.")
            return None
        
        try:
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            _db_instance = client.get_default_database(default="video_subtitler")
            # Force a ping to ensure connection works (optional, but catches bad URIs faster)
            client.admin.command('ping')
            print("Connected to MongoDB")
        except Exception as e:
            print(f"Failed to connect to MongoDB. Is your MONGO_URI correct? Error: {e}")
            _db_instance = None
    return _db_instance
