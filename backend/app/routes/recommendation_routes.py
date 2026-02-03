from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId

from ..db import get_db
from ..utils.ai import generate_recommendations

recommendation_bp = Blueprint('recommendations', __name__)


@recommendation_bp.get('')
@jwt_required()
def get_recommendations():
    db = get_db()
    uid = ObjectId(get_jwt_identity())

    # Window
    days = request.args.get('days')
    try:
        window_days = int(days) if days else 30
    except Exception:
        window_days = 30

    today = datetime.utcnow().date()
    start_date = (today - timedelta(days=window_days)).strftime('%Y-%m-%d')

    # Profile
    user = db.users.find_one({'_id': uid})
    profile = {
        'id': str(uid),
        'email': user.get('email', '') if user else '',
        'name': user.get('name', '') if user else ''
    }

    # Summary by category
    pipeline = [
        {'$match': {'user_id': uid, 'date': {'$gte': start_date}}},
        {'$group': {
            '_id': '$category',
            'sum': {'$sum': '$emission_kg'}
        }}
    ]
    cat_rows = list(db.activities.aggregate(pipeline))
    by_category = {r['_id']: float(r['sum']) for r in cat_rows}
    summary = {
        'total_kg': float(sum(by_category.values())),
        'by_category': {
            'transport': float(by_category.get('transport', 0)),
            'energy': float(by_category.get('energy', 0)),
            'food': float(by_category.get('food', 0)),
        }
    }

    # Recent activities (limit 50)
    cur = db.activities.find({'user_id': uid, 'date': {'$gte': start_date}}).sort('date', -1).limit(50)
    recent = []
    for d in cur:
        recent.append({
            'date': d.get('date'),
            'type': d.get('type'),
            'category': d.get('category'),
            'emission_kg': float(d.get('emission_kg', 0)),
            'data': d.get('data', {})
        })

    result = generate_recommendations(str(uid), profile, summary, recent)
    return jsonify({
        'window_days': window_days,
        'summary': summary,
        'source': result.get('source', 'unknown'),
        'items': result.get('items', [])
    })
