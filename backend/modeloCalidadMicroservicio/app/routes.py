from flask import Blueprint, request, jsonify
from backend.models import db
from app.services import (
    get_characteristic_with_subs,
    create_characteristic_with_subs,
    get_all_characteristics,
    update_characteristic_with_subs,
    delete_characteristic,
    delete_subcharacteristic,
    get_all_characteristics_with_subs
)


modelo_routes = Blueprint('modelo_routes', __name__)

@modelo_routes.route('/caracteristica', methods=['POST'])
def create_characteristic():
    data = request.get_json()
    
    name = data.get('name')
    description = data.get('description')
    weight_percentage = data.get('weight_percentage')
    subcharacteristics = data.get('subcharacteristics', [])

    if not name or not isinstance(subcharacteristics, list):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    try:
        new_char = create_characteristic_with_subs(name, description, weight_percentage, subcharacteristics)
        return jsonify({
            "message": "Característica creada exitosamente",
            "characteristic_id": new_char.id
        }), 201        
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@modelo_routes.route('/caracteristica', methods=['GET'])
def get_all():
    characteristics = get_all_characteristics()
    return jsonify(characteristics), 200

@modelo_routes.route('/caracteristica/<int:char_id>', methods=['GET'])
def get_characteristic_with_subs_route(char_id):
    result = get_characteristic_with_subs(char_id)
    if not result:
        return jsonify({'message': 'Caracteristica no encontrada'}), 404
    return jsonify(result), 200


@modelo_routes.route('/caracteristica/<int:char_id>', methods=['PUT'])
def updateCharacteristicWithSubs(char_id):
    data = request.get_json()

    name = data.get('name')
    description = data.get('description')
    weight_percentage = data.get('weight_percentage')
    subcharacteristics = data.get('subcharacteristics', [])

    result = update_characteristic_with_subs(
        char_id,
        name,
        description,
        weight_percentage,
        subcharacteristics
    )

    if result:
        return jsonify({'message': 'Caracteristica y subcaracteristicas actualizadas correctamente'}), 200
    else:
        return jsonify({'message': 'Caracteristica no encontrada'}), 404

@modelo_routes.route('/caracteristica/<int:id>', methods=['DELETE'])
def delete_char(id):
    success = delete_characteristic(id)
    if not success:
        return jsonify({'message': 'No encontrada'}), 404
    return jsonify({'message': 'Eliminada exitosamente'}), 200

@modelo_routes.route('/subcaracteristica/<int:id>', methods=['DELETE'])
def delete_sub(id):
    success = delete_subcharacteristic(id)
    if not success:
        return jsonify({'message': 'No encontrada'}), 404
    return jsonify({'message': 'Eliminada exitosamente'}), 200


"""
@modelo_routes.route('/asignar_item', methods=['POST'])
def asignar_item_a_software():
    data = request.get_json()
    software_id = data.get('software_id')
    characteristic_ids = data.get('characteristics')  # lista de IDs

    if not software_id or not isinstance(characteristic_ids, list):
        return jsonify({'error': 'Datos incompletos'}), 400

    result = assign_characteristics_to_software(software_id, characteristic_ids)
    status_code = 200 if result['success'] else 400
    return jsonify(result), status_code
"""


@modelo_routes.route('/caracteristicas-con-subcaracteristicas', methods=['GET'])
def get_all_with_subs():
    data = get_all_characteristics_with_subs()
    return jsonify(data), 200