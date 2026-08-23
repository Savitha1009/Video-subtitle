from config.db import get_db
import bcrypt
import datetime
import uuid

class User:
    @staticmethod
    def get_collection():
        db = get_db()
        return db['users'] if db is not None else None

    @staticmethod
    def create_user(name, email, password):
        collection = User.get_collection()
        if collection is None:
            return None
        
        # Check if user already exists
        if collection.find_one({"email": email}):
            return None
            
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user_doc = {
            "userId": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "passwordHash": hashed_password.decode('utf-8'),
            "createdAt": datetime.datetime.utcnow()
        }
        
        collection.insert_one(user_doc)
        return user_doc

    @staticmethod
    def verify_password(email, password):
        collection = User.get_collection()
        if collection is None:
            return False, None
            
        user = collection.find_one({"email": email})
        if not user:
            return False, None
            
        if bcrypt.checkpw(password.encode('utf-8'), user['passwordHash'].encode('utf-8')):
            return True, user
        return False, None
    
    @staticmethod
    def get_user_by_id(user_id):
        collection = User.get_collection()
        if collection is None:
            return None
        return collection.find_one({"userId": user_id})
