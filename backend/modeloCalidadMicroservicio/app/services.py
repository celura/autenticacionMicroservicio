from backend.models import db, QualityCharacteristic, Subcharacteristic
from sqlalchemy import func

def create_characteristic_with_subs(name, description, weight_percentage, subcharacteristics):
    suma_actual = db.session.query(func.sum(QualityCharacteristic.weight_percentage))\
                    .scalar() or 0

    nueva_suma = suma_actual + weight_percentage

    if nueva_suma > 100:
        raise ValueError(f"La suma de los pesos supera el 100% ({nueva_suma}%).")

    new_char = QualityCharacteristic(
        name=name,
        description=description,
        weight_percentage=weight_percentage
    )
    db.session.add(new_char)
    db.session.flush()  

    for sub in subcharacteristics:
        sub_name = sub.get('name')
        sub_desc = sub.get('description', '')

        if not sub_name:
            continue
        existing = Subcharacteristic.query.filter_by(name=sub_name).first()
        if existing:
            continue

        new_sub = Subcharacteristic(
            name=sub_name,
            description=sub_desc,
            characteristic_id=new_char.id
        )
        db.session.add(new_sub)
    db.session.commit()
    return new_char

def get_all_characteristics():
    characteristics = QualityCharacteristic.query.all()
    results = []

    for char in characteristics:
        sub_count = Subcharacteristic.query.filter_by(characteristic_id=char.id).count()
        results.append({
            'id': char.id,
            'name': char.name,
            'description': char.description,
            'weight_percentage': float(char.weight_percentage),
            'subcharacteristic_count': sub_count
        })

    return results


def get_characteristic_with_subs(char_id):
    characteristic = QualityCharacteristic.query.get(char_id)
    if not characteristic:
        return None

    subs = Subcharacteristic.query.filter_by(characteristic_id=char_id).all()

    return {
        'id': characteristic.id,
        'name': characteristic.name,
        'description': characteristic.description,
        'weight_percentage': float(characteristic.weight_percentage),
        'subcharacteristics': [
            {
                'id': sub.id,
                'name': sub.name,
                'description': sub.description,
                'max_score': sub.max_score
            } for sub in subs
        ]
    }

def update_characteristic_with_subs(char_id, name, description, weight_percentage, subcharacteristics):
    characteristic = QualityCharacteristic.query.get(char_id)
    if not characteristic:
        return None

    characteristic.name = name
    characteristic.description = description
    characteristic.weight_percentage = weight_percentage

    for sub in subcharacteristics:
        sub_id = sub.get('id')
        sub_name = sub.get('name')
        sub_desc = sub.get('description', '')

        if sub_id:
            existing = Subcharacteristic.query.get(sub_id)
            if existing and existing.characteristic_id == char_id:
                existing.name = sub_name
                existing.description = sub_desc
        else:
            new_sub = Subcharacteristic(
                name=sub_name,
                description=sub_desc,
                characteristic_id=char_id
            )
            db.session.add(new_sub)

    db.session.commit()
    return characteristic

def delete_characteristic(char_id):
    characteristic = QualityCharacteristic.query.get(char_id)
    if not characteristic:
        return False
    db.session.delete(characteristic)
    db.session.commit()
    return True

def delete_subcharacteristic(sub_id):
    sub = Subcharacteristic.query.get(sub_id)
    if not sub:
        return False
    db.session.delete(sub)
    db.session.commit()
    return True


"""def assign_characteristics_to_software(software_id, characteristic_ids):
    from backend.models import Software, QualityCharacteristic

    software = Software.query.get(software_id)
    if not software:
        return {'success': False, 'message': 'Software no encontrado'}

    # Obtener las características ya asignadas
    existing_assignments = QualityCharacteristic.query.filter_by(software_id=software_id).all()
    existing_char_ids = [assign.characteristic_id for assign in existing_assignments]
    
    # Calcular características totales (existentes + nuevas)
    all_char_ids = set(existing_char_ids)
    for cid in characteristic_ids:
        all_char_ids.add(cid)
    
    # Verificar que no exceda el límite de 7 características
    if len(all_char_ids) > 7:
        return {'success': False, 'message': 'Solo se pueden asignar hasta 7 características'}

    # Agregar solo las características que no estén ya asignadas
    for cid in characteristic_ids:
        char = QualityCharacteristic.query.get(cid)
        if not char:
            continue
            
        # Verificar si ya existe esta asignación
        if cid not in existing_char_ids:
            db.session.add(QualityCharacteristic(software_id=software_id, characteristic_id=cid))

    db.session.commit()
    return {'success': True, 'message': 'Características asignadas correctamente'}

def get_items_by_software(software_id):
    from backend.models import SoftwareCharacteristic, QualityCharacteristic

    assignments = SoftwareCharacteristic.query.filter_by(software_id=software_id).all()

    result = []
    for assignment in assignments:
        char = assignment.characteristic
        subcaracs = [
            {
                "id": sub.id,
                "name": sub.name,
                "description": sub.description,
                "max_score": sub.max_score
            }
            for sub in char.subcharacteristics
        ]
        result.append({
            'id': char.id,
            'name': char.name,
            'description': char.description,
            'weight_percentage': float(char.weight_percentage),
            'software_id': software_id,
            'subcharacteristics': subcaracs
        })

    return result
"""
def get_all_characteristics_with_subs():
    characteristics = QualityCharacteristic.query.all()
    result = []

    for char in characteristics:
        subs = Subcharacteristic.query.filter_by(characteristic_id=char.id).all()
        result.append({
            'id': char.id,
            'name': char.name,
            'description': char.description,
            'weight_percentage': float(char.weight_percentage),
            'subcharacteristics': [
                {
                    'id': sub.id,
                    'name': sub.name,
                    'description': sub.description,
                    'max_score': sub.max_score
                }
                for sub in subs
            ]
        })
    return result
