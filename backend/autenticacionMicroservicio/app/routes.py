from flask import Blueprint, request, jsonify
from app.services import create_user, authenticate_user

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    user = create_user(username, password, email)
    if user:
        return jsonify({'message': 'Usuario creado exitosamente'}), 201
    return jsonify({'message': 'El usuario ya existe'}), 400

@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    token_data = authenticate_user(data.get('email'), data.get('password'))
    if token_data:
        return jsonify(token_data), 200
    return jsonify({'message': 'Credenciales inválidas'}), 401