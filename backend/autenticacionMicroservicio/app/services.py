from werkzeug.security import generate_password_hash, check_password_hash
from backend.models import db, User
from flask_jwt_extended import create_access_token

def create_user(username, password, email):
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return None

    password_hash = generate_password_hash(password)
    new_user = User(username=username, password_hash=password_hash, email=email)

    db.session.add(new_user)
    db.session.commit()
    return new_user

def authenticate_user(email, password):
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        token = create_access_token(identity=str(user.id))

        return {
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }
    return None