from backend.models import db, Software, SoftwareParticipant

def create_software_with_participants(name, city, general_objective, description, version, participants, user_id):
    existing_software = Software.query.filter_by(name=name, user_id=user_id).first()
    if existing_software:
        return {'success': False, 'message': 'Ya tienes un software con este nombre'}
    
    new_software = Software(
        name=name,
        city=city,
        general_objective=general_objective,
        description=description,
        version=version,
        user_id=user_id
    )
    db.session.add(new_software)
    db.session.flush()  

    for p in participants:
        existing_participant = SoftwareParticipant.query.filter_by(name=p.get('name')).first()
        if existing_participant:
            continue  

        new_participant = SoftwareParticipant(
            name=p.get('name'),
            role=p.get('role'),
            software_id=new_software.id
        )
        db.session.add(new_participant)

    db.session.commit()
    return {'success': True, 'message': 'Software registrado', 'software': new_software.to_dict()}

def get_software_detail(user_id, software_id):
    software = Software.query.filter_by(id=software_id, user_id=user_id).first()
    if not software:
        return None
    return software.to_dict()


"""
def get_software_by_user(user_id):
    softwares = Software.query.filter_by(user_id=user_id).options(
        joinedload(Software.evaluations)
    ).all()

    result = []
    for software in softwares:
        
        evaluation = None
        if software.evaluations:
            latest_eval = max(software.evaluations, key=lambda e: e.date or datetime.min)
            evaluation = {
                'id': latest_eval.id,
                'date': latest_eval.date.isoformat() if latest_eval.date else None,
                'global_score_percentage': float(latest_eval.global_score_percentage) if latest_eval.global_score_percentage is not None else None,
            }

        result.append({
            'id': software.id,
            'name': software.name,
            'city': software.city,
            'general_objective': software.general_objective,
            'description': software.description,
            'version': software.version,
            'registered_at': software.registered_at.isoformat(),
            'evaluation': evaluation
        })

    return result"""