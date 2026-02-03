from datetime import datetime
import re
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from ..db import get_db


auth_bp = Blueprint('auth', __name__)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _normalize_email(email: str) -> str:
    return (email or '').strip().lower()


@auth_bp.post('/register')
def register():
    db = get_db()
    payload = request.get_json(silent=True) or {}
    email = _normalize_email(payload.get('email'))
    password = payload.get('password', '')
    name = (payload.get('name') or '').strip() or email.split('@')[0]

    if not EMAIL_REGEX.match(email):
        return jsonify({"error": "Invalid email"}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    if db.users.find_one({'email': email}):
        return jsonify({"error": "Email already registered"}), 409

    user_doc = {
        'email': email,
        'password_hash': generate_password_hash(password),
        'name': name,
        'created_at': datetime.utcnow(),
    }
    res = db.users.insert_one(user_doc)
    user_id = str(res.inserted_id)

    token = create_access_token(identity=user_id)
    return jsonify({
        'token': token,
        'user': {
            'id': user_id,
            'email': user_doc['email'],
            'name': user_doc['name']
        }
    }), 201


@auth_bp.post('/login')
def login():
    db = get_db()
    payload = request.get_json(silent=True) or {}
    email = _normalize_email(payload.get('email'))
    password = payload.get('password', '')

    user = db.users.find_one({'email': email})
    if not user or not check_password_hash(user.get('password_hash', ''), password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=str(user['_id']))
    return jsonify({
        'token': token,
        'user': {
            'id': str(user['_id']),
            'email': user['email'],
            'name': user.get('name', '')
        }
    }), 200


@auth_bp.get('/me')
@jwt_required()
def me():
    db = get_db()
    uid = get_jwt_identity()
    from bson.objectid import ObjectId
    user = db.users.find_one({'_id': ObjectId(uid)})

    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        'id': str(user['_id']),
        'email': user['email'],
        'name': user.get('name', '')
    })


@auth_bp.put('/me')
@jwt_required()
def update_me():
    db = get_db()
    uid = get_jwt_identity()
    payload = request.get_json(silent=True) or {}

    updates = {}
    if 'name' in payload:
        updates['name'] = (payload.get('name') or '').strip()

    if 'password' in payload:
        pwd = payload.get('password') or ''
        if len(pwd) < 8:
            return jsonify({"error": "Password must be at least 8 characters"}), 400
        updates['password_hash'] = generate_password_hash(pwd)

    if not updates:
        return jsonify({"error": "Nothing to update"}), 400

    from bson.objectid import ObjectId
    db.users.update_one({'_id': ObjectId(uid)}, {'$set': updates})

    user = db.users.find_one({'_id': ObjectId(uid)})
    return jsonify({
        'id': str(user['_id']),
        'email': user['email'],
        'name': user.get('name', '')
    })
