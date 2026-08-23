from functools import wraps
from flask import request, jsonify
import jwt
import os
from models.user import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'token' in request.cookies:
            token = request.cookies.get('token')
                
        if not token:
            return jsonify({"error": "Token is missing"}), 401
            
        try:
            from flask import current_app
            secret_key = current_app.config.get('JWT_SECRET_KEY', 'default_secret_key')
            data = jwt.decode(token, secret_key, algorithms=['HS256'])
            current_user = User.get_user_by_id(data['userId'])
            if not current_user:
                raise Exception("User not found")
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except Exception as e:
            return jsonify({"error": "Token is invalid"}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated
