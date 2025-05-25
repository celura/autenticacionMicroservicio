from flask import Blueprint, request, jsonify
from app.services import create_software_with_participants
from flask_jwt_extended import jwt_required, get_jwt_identity
software_routes = Blueprint('software_routes', __name__)
from backend.models import Software
from app.services import get_software_detail

@software_routes.route('/register', methods=['POST'])
@jwt_required()
def register():
    user_id = get_jwt_identity()
    data = request.get_json()
    print("🟡 JSON recibido en el backend:", data)
    if not data:
        return jsonify({"error": "No se recibió data"}), 400
    name = data.get('name')
    city = data.get('city')
    general_objective = data.get('general_objective')
    description = data.get('description')
    version = data.get('version')
    user_id=user_id
    participants = data.get('participants', [])

    result = create_software_with_participants(name, city, general_objective, description, version, participants, user_id)
    if result['success']:
        return jsonify({'message': 'Software registrado exitosamente'}), 201
    return jsonify({'message': result['message']}), 400

@software_routes.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_software(user_id):
    current_user_id = get_jwt_identity()

    if user_id != int(current_user_id): 
        return jsonify({"error": "No autorizado"}), 403

    software_list = Software.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        "software": [s.to_dict() for s in software_list]
    }), 200

@software_routes.route('/<int:user_id>/<int:software_id>', methods=['GET'])
@jwt_required()
def get_software_detail_route(user_id, software_id):
    current_user_id = get_jwt_identity()
    if user_id != int(current_user_id):
        return jsonify({"error": "No autorizado"}), 403

    software = get_software_detail(user_id, software_id)
    if not software:
        return jsonify({"error": "Software no encontrado"}), 404
    return jsonify({"software": software}), 200

    
    return jsonify({'software': software}), 200
""" Simplemente es para que no moleste el mio
@software_routes.route('/<int:user_id>', methods=['GET'])
def get_software_by_user_route(user_id):
    try:
        data = get_software_by_user(user_id)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500"""