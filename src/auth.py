import validator

from src.database import User, db
from src.schemas import UserSchema


from flask import request, jsonify
from flask_smorest import Blueprint
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth.post("/register")
@auth.response(201, UserSchema)
def register():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    if len(password)<6:
        return jsonify({"error": "Password is too short"})
    
    #email validation, email is taken, username is taken

    pwd_hash=generate_password_hash(password)

    user=User(username=username, password=pwd_hash, email=email)
    db.session.add(user)
    db.session.commit()
    return jsonify({
        'message': "User created",
        "user": {
            "username": username, "email": email
        }
    })


@auth.post('/login')
@auth.response(201, UserSchema)
def login():
    email = request.json.get('email', '')
    password = request.json.get('password', '')

    user = User.query.filter_by(email=email).first()

    if user:
        is_pass_correct = check_password_hash(user.password, password)

        if is_pass_correct:
            refresh= create_refresh_token(identity=user.id)
            access = create_access_token(identity=user.id)
        
        return jsonify({
            "user": {
                "refresh": refresh,
                "access": access,
                "username": user.username,
                "email": user.email
            }
        })
    
    return jsonify({"error": "Wrong credentials"})



@auth.get("/me")
@jwt_required()
def me():
    return {"user": "me"}