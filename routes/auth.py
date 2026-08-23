from flask import Blueprint, request, jsonify, current_app
from models.user import User
import jwt
import datetime

auth_bp = Blueprint('auth', __name__)

def generate_token(user_id):
    secret_key = current_app.config.get('JWT_SECRET_KEY', 'default_secret_key')
    payload = {
        'userId': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request"}), 400
        
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not name or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400
        
    user = User.create_user(name, email, password)
    if not user:
        return jsonify({"error": "User already exists or failed to create"}), 409
        
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request"}), 400
        
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400
        
    success, user = User.verify_password(email, password)
    if not success:
        return jsonify({"error": "Invalid credentials"}), 401
        
    token = generate_token(user['userId'])
    response = jsonify({
        "message": "Login successful",
        "userId": user['userId'],
        "name": user['name']
    })
    
    # Set HTTP-only cookie
    response.set_cookie('token', token, httponly=True, samesite='Lax')
    
    return response, 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    response = jsonify({"message": "Logout successful"})
    response.set_cookie('token', '', expires=0)
    return response, 200
