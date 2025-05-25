from flask import jsonify
from backend.models import (
    db, Software, SoftwareRisk, RiskOwnership, RiskClassification,
    RiskEvaluation, RiskControl, LikelihoodEnum, ImpactEnum, RiskMitigation
)

def register_software_risk(data):
    try:
        risk = SoftwareRisk(
            software_id=data["software_id"],
            risk_code=data["risk_code"],
            identified_at=data["identified_at"],
            title=data["title"],
            description=data.get("description", ""),
            causes=data.get("causes", ""),
            affects_critical_infrastructure=data.get("affects_critical_infrastructure", False),
            process=data.get("process", "")
        )
        db.session.add(risk)
        db.session.flush()

        ownership = data.get("ownership")
        if ownership:
            risk_owner = RiskOwnership(
                risk_id=risk.id,
                owner_name=ownership["owner_name"],
                owner_role=ownership["owner_role"]
            )
            db.session.add(risk_owner)
            db.session.flush()

        classification = data.get("classification")
        if classification:
            risk_type = classification["risk_type"]

            if risk_type in ["Fisico", "Logico", "Locativo"]:
                impact_type = "Continuidad Operativa"
            elif risk_type == "Legal":
                impact_type = "Legal"
            elif risk_type == "Reputacional":
                impact_type = "Imagen"
            else:
                impact_type = "Financiero" 
                
            risk_class = RiskClassification(
                risk_id=risk.id,
                risk_type=classification["risk_type"],
                confidentiality=classification["confidentiality"],
                integrity=classification["integrity"],
                availability=classification["availability"],
                impact_type=impact_type
            )
            db.session.add(risk_class)

        evaluation = data.get("evaluation")
        if evaluation:
            likelihood_name = evaluation["likelihood"]
            impact_name = evaluation["impact"]

            try:
                likelihood_enum = LikelihoodEnum[likelihood_name]
                impact_enum = ImpactEnum[impact_name]
                likelihood_value = likelihood_enum.value 
                impact_value = impact_enum.value 
            except KeyError as e:
                print(f"Error con enum: {e}")
                return {"error": f"Valor de enum inválido: {e}"}, 400
            
            valor_riesgo = likelihood_value * impact_value

            if valor_riesgo <= 3:
                risk_zone = "BAJA"
                acceptance = "Si"
            elif 4 <= valor_riesgo <= 6:
                risk_zone = "MODERADA"
                acceptance = "Si"
            elif 7 <= valor_riesgo <= 12:
                risk_zone = "ALTA"
                acceptance = "No"
            else:
                risk_zone = "EXTREMA"
                acceptance = "No"

            risk_eval = RiskEvaluation(
                risk_id=risk.id,
                likelihood=likelihood_enum,  
                impact=impact_enum,          
                risk_zone=risk_zone,
                acceptance=acceptance
            )
            db.session.add(risk_eval)
            db.session.flush()

        controls = data.get("controls")
        if controls:
            control_type = controls["control_type"]

            def puntaje(valor, peso):
                return peso if valor == True else 0

            control_rating = (
                puntaje(controls["has_mechanism"], 15) +
                puntaje(controls["has_manuals"], 15) +
                puntaje(controls["control_effective"], 30) +
                puntaje(controls["responsible_defined"], 15) +
                puntaje(controls["control_frequency_adequate"], 25)
            )

            preventive_controls_avg = control_rating if control_type == "PREVENTIVO" else 0
            corrective_controls_avg = control_rating if control_type == "CORRECTIVO" else 0

            def cuadrante(valor):
                if valor <= 50:
                    return 0
                elif 51 <= valor <= 75:
                    return 1
                elif 76 <= valor <= 100:
                    return 2
                else:
                    return 2  # > 100

            reduce_likelihood_quadrants = cuadrante(preventive_controls_avg)
            reduce_impact_quadrants = cuadrante(corrective_controls_avg)

            control = RiskControl(
                risk_id=risk.id,
                control_type=control_type,
                has_mechanism=controls["has_mechanism"],
                has_manuals=controls["has_manuals"],
                control_effective=controls["control_effective"],
                responsible_defined=controls["responsible_defined"],
                control_frequency_adequate=controls["control_frequency_adequate"],
                control_rating=control_rating,
                preventive_controls_avg=preventive_controls_avg,
                reduce_likelihood_quadrants=reduce_likelihood_quadrants,
                corrective_controls_avg=corrective_controls_avg,
                reduce_impact_quadrants=reduce_impact_quadrants
            )
            db.session.add(control)

            mitigation = RiskMitigation(
                risk_id=risk.id,
                evaluation_id=risk_eval.id if evaluation else None,
                ownership_id=risk_owner.id if ownership else None,
                risk_code=risk.risk_code,
                risk_zone=risk_zone,
                risk_description=risk.description,
                responsible=risk_owner.owner_name if ownership else "No asignado",
                phase=None,
                response_type=None,
                mitigation_plan=None
            )
            db.session.add(mitigation)

        db.session.commit()
        return {"message": "Riesgo registrado correctamente", "risk_id": risk.id}, 201

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 400
    
def obtener_evaluaciones_riesgo(user_id):
    try:
        riesgos = (
            db.session.query(SoftwareRisk, Software, RiskEvaluation)
            .join(Software, SoftwareRisk.software_id == Software.id)
            .join(RiskEvaluation, SoftwareRisk.id == RiskEvaluation.risk_id)
            .filter(Software.user_id == user_id)
            .all()
        )

        data = []
        for riesgo, software, evaluation in riesgos:
            likelihood_value = 1
            impact_value = 1

            # Procesar likelihood
            if evaluation.likelihood:
                if hasattr(evaluation.likelihood, 'value'):
                    likelihood_value = evaluation.likelihood.value
                elif isinstance(evaluation.likelihood, str):
                    try:
                        likelihood_value = LikelihoodEnum[evaluation.likelihood].value
                    except KeyError:
                        likelihood_value = 1
                else:
                    likelihood_value = int(evaluation.likelihood)

            if evaluation.impact:
                if hasattr(evaluation.impact, 'value'):
                    impact_value = evaluation.impact.value
                elif isinstance(evaluation.impact, str):
                    try:
                        impact_value = ImpactEnum[evaluation.impact].value
                    except KeyError:
                        impact_value = 1
                else:
                    impact_value = int(evaluation.impact)

            valor_riesgo = likelihood_value * impact_value
            evaluation_date = riesgo.identified_at.strftime("%Y-%m-%d") if riesgo.identified_at else "N/A"

            data.append({
                "risk_id": riesgo.id,
                "software_id": riesgo.software_id,
                "software_name": software.name,
                "risk_code": riesgo.risk_code or "N/A",
                "zona_riesgo": evaluation.risk_zone or "N/A",
                "valor_riesgo": valor_riesgo,
                "evaluation_date": evaluation_date,
                "acceptance": evaluation.acceptance or "N/A",
            })

        return jsonify(data), 200

    except Exception as e:
        print(f"Error en obtener_evaluaciones_riesgo: {str(e)}")
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500


def obtener_detalle_riesgo(risk_id):
    try:
        risk = SoftwareRisk.query.get_or_404(risk_id)
        software = Software.query.get_or_404(risk.software_id)

        response = {
            "software": {
                "id": software.id,
                "name": software.name,
                "version": software.version,
            },
            "risk": {
                "id": risk.id,
                "risk_code": risk.risk_code,
                "title": risk.title,
                "identified_at": risk.identified_at.strftime("%Y-%m-%d"),
                "description": risk.description,
                "causes": risk.causes,
                "affects_critical_infrastructure": risk.affects_critical_infrastructure,
                "process": risk.process
            },
            "classification": {
                "risk_type": risk.classification.risk_type.value if risk.classification else None,
                "confidentiality": risk.classification.confidentiality,
                "integrity": risk.classification.integrity,
                "availability": risk.classification.availability,
                "impact_type": risk.classification.impact_type
            } if risk.classification else {},
            "evaluation": {
                "likelihood": risk.evaluation.likelihood.name,
                "impact": risk.evaluation.impact.name,
                "risk_zone": risk.evaluation.risk_zone,
                "acceptance": risk.evaluation.acceptance,
                "valor_riesgo": LikelihoodEnum[risk.evaluation.likelihood.name].value * ImpactEnum[risk.evaluation.impact.name].value
            } if risk.evaluation else {},
            "controls": {
                "control_type": risk.controls.control_type,
                "has_mechanism": risk.controls.has_mechanism,
                "has_manuals": risk.controls.has_manuals,
                "control_effective": risk.controls.control_effective,
                "responsible_defined": risk.controls.responsible_defined,
                "control_frequency_adequate": risk.controls.control_frequency_adequate,
                "control_rating": float(risk.controls.control_rating),
                "reduce_likelihood_quadrants": risk.controls.reduce_likelihood_quadrants,
                "reduce_impact_quadrants": risk.controls.reduce_impact_quadrants,
            } if risk.controls else {},
            "mitigation": {
                "responsible": risk.mitigations[0].responsible if risk.mitigations else "No asignado",
                "risk_zone": risk.mitigations[0].risk_zone if risk.mitigations else None
            }
        }

        return jsonify(response), 200

    except Exception as e:
        print("Error en obtener_detalle_riesgo:", str(e))
        return jsonify({"error": "Error al obtener detalle del riesgo"}), 500
    
def get_mitigation_by_risk_id(risk_id):
    mitigations = RiskMitigation.query.filter_by(risk_id=risk_id).all()

    def serialize_mitigation(m):
        return {
            'id': m.id,
            'risk_id': m.risk_id,
            'evaluation_id': m.evaluation_id,
            'ownership_id': m.ownership_id,
            'risk_code': m.risk_code,
            'risk_description': m.risk_description,
            'risk_zone': m.risk_zone,
            'responsible': m.responsible,
            'phase': m.phase,
            'response_type': m.response_type.value if m.response_type else None,
            'mitigation_plan': m.mitigation_plan,
            'registered_at': m.registered_at.isoformat() if m.registered_at else None
        }

    return [serialize_mitigation(m) for m in mitigations]

def update_risk_mitigation(risk_mitigation_id, data):
    mitigation = RiskMitigation.query.get(risk_mitigation_id)
    if not mitigation:
        return None

    if 'phase' in data:
        mitigation.phase = data['phase']
    if 'response_type' in data:
        mitigation.response_type = data['response_type']
    if 'mitigation_plan' in data:
        mitigation.mitigation_plan = data['mitigation_plan']

    db.session.commit()
    return mitigation