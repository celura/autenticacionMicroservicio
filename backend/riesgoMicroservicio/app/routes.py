from flask import Blueprint, request, jsonify
from app.services import register_software_risk, obtener_detalle_riesgo, obtener_evaluaciones_riesgo, get_mitigation_by_risk_id, update_risk_mitigation


riesgo_routes = Blueprint('risk', __name__)

@riesgo_routes.route('/registrar', methods=['POST'])
def register_risk():
    data = request.get_json()
    result, status = register_software_risk(data)
    return jsonify(result), status

@riesgo_routes.route('/evaluaciones/<int:user_id>', methods=['GET'])
def listar_evaluaciones_riesgo(user_id):
    return obtener_evaluaciones_riesgo(user_id)

@riesgo_routes.route('/detalle/<int:risk_id>', methods=['GET'])
def detalle_riesgo(risk_id):
    return obtener_detalle_riesgo(risk_id)


@riesgo_routes.route('/mitigacion/<int:risk_id>', methods=['GET'])
def get_mitigation(risk_id):
    try:
        mitigations = get_mitigation_by_risk_id(risk_id)
        return jsonify({'mitigations': mitigations}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    
@riesgo_routes.route('/actualizar/<int:mitigation_id>', methods=['PUT'])
def update_mitigation(mitigation_id):
    try:
        data = request.get_json()
        updated_mitigation = update_risk_mitigation(mitigation_id, data)
        if not updated_mitigation:
            return jsonify({'error': 'Mitigation not found'}), 404

        return jsonify({
            'id': updated_mitigation.id,
            'phase': updated_mitigation.phase,
            'response_type': updated_mitigation.response_type.name if updated_mitigation.response_type else None,
            'mitigation_plan': updated_mitigation.mitigation_plan
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500