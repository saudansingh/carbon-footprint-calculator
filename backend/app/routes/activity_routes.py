from datetime import datetime, date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId

from ..db import get_db
from ..utils.emissions import compute_emission_kg, categorize, parse_date_str


activity_bp = Blueprint('activities', __name__)


_DEF_PAGE_SIZE = 50


def _serialize_activity(doc):
    return {
        'id': str(doc['_id']),
        'user_id': str(doc['user_id']),
        'date': doc['date'],
        'type': doc['type'],
        'category': doc['category'],
        'data': doc.get('data', {}),
        'emission_kg': doc.get('emission_kg', 0.0),
        'created_at': doc.get('created_at'),
        'updated_at': doc.get('updated_at'),
    }


@activity_bp.post('')
@jwt_required()
def create_activity():
    db = get_db()
    uid = get_jwt_identity()
    payload = request.get_json(silent=True) or {}

    a_type = payload.get('type')
    date_str = payload.get('date')
    data = payload.get('data', {})

    if not a_type or not date_str:
        return jsonify({'error': 'type and date are required'}), 400

    try:
        # validate date format
        d = parse_date_str(date_str)
    except Exception:
        return jsonify({'error': 'date must be YYYY-MM-DD'}), 400

    emission, norm = compute_emission_kg({'type': a_type, 'data': data})
    cat = categorize(a_type)

    doc = {
        'user_id': ObjectId(uid),
        'date': date_str,
        'type': a_type,
        'category': cat,
        'data': norm,
        'emission_kg': round(float(emission), 4),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
    }
    res = db.activities.insert_one(doc)
    doc['_id'] = res.inserted_id
    return jsonify(_serialize_activity(doc)), 201


@activity_bp.get('')
@jwt_required()
def list_activities():
    db = get_db()
    uid = get_jwt_identity()
    q = {'user_id': ObjectId(uid)}

    start = request.args.get('start')
    end = request.args.get('end')
    date_eq = request.args.get('date')
    a_type = request.args.get('type')

    if date_eq:
        q['date'] = date_eq
    else:
        if start:
            q['date'] = q.get('date', {})
            q['date']['$gte'] = start
        if end:
            q['date'] = q.get('date', {})
            q['date']['$lte'] = end

    if a_type:
        q['type'] = a_type

    page_size = int(request.args.get('limit', _DEF_PAGE_SIZE))
    cursor = db.activities.find(q).sort('date', 1).limit(page_size)
    items = [_serialize_activity(d) for d in cursor]
    return jsonify({'items': items})


@activity_bp.put('/<aid>')
@jwt_required()
def update_activity(aid):
    db = get_db()
    uid = get_jwt_identity()
    try:
        oid = ObjectId(aid)
    except Exception:
        return jsonify({'error': 'invalid id'}), 400

    payload = request.get_json(silent=True) or {}

    updates = {}
    if 'date' in payload:
        try:
            _ = parse_date_str(payload['date'])
            updates['date'] = payload['date']
        except Exception:
            return jsonify({'error': 'date must be YYYY-MM-DD'}), 400

    # If type or data changes, recompute emission
    type_changed = False
    data_changed = False
    if 'type' in payload:
        type_changed = True
        updates['type'] = payload['type']
        updates['category'] = categorize(payload['type'])
    if 'data' in payload:
        data_changed = True
        updates['data'] = payload['data']

    if type_changed or data_changed:
        a_type = updates.get('type')
        if not a_type:
            # need current type
            existing = db.activities.find_one({'_id': oid, 'user_id': ObjectId(uid)})
            if not existing:
                return jsonify({'error': 'not found'}), 404
            a_type = existing['type']
        data = updates.get('data')
        if data is None:
            existing = db.activities.find_one({'_id': oid, 'user_id': ObjectId(uid)})
            if not existing:
                return jsonify({'error': 'not found'}), 404
            data = existing.get('data', {})
        emission, norm = compute_emission_kg({'type': a_type, 'data': data})
        updates['data'] = norm
        updates['emission_kg'] = round(float(emission), 4)

    if not updates:
        return jsonify({'error': 'nothing to update'}), 400

    updates['updated_at'] = datetime.utcnow()

    res = db.activities.update_one({'_id': oid, 'user_id': ObjectId(uid)}, {'$set': updates})
    if res.matched_count == 0:
        return jsonify({'error': 'not found'}), 404
    doc = db.activities.find_one({'_id': oid})
    return jsonify(_serialize_activity(doc))


@activity_bp.delete('/<aid>')
@jwt_required()
def delete_activity(aid):
    db = get_db()
    uid = get_jwt_identity()
    try:
        oid = ObjectId(aid)
    except Exception:
        return jsonify({'error': 'invalid id'}), 400

    res = db.activities.delete_one({'_id': oid, 'user_id': ObjectId(uid)})
    if res.deleted_count == 0:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'status': 'deleted'})
