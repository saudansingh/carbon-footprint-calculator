from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId

from ..db import get_db

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.get('/summary')
@jwt_required()
def summary():
    db = get_db()
    uid = ObjectId(get_jwt_identity())

    start = request.args.get('start')
    end = request.args.get('end')

    match = {'user_id': uid}
    if start or end:
        match['date'] = {}
        if start:
            match['date']['$gte'] = start
        if end:
            match['date']['$lte'] = end

    pipeline = [
        {'$match': match},
        {'$group': {
            '_id': None,
            'total_kg': {'$sum': '$emission_kg'},
            'by_category': {
                '$push': {'k': '$category', 'v': '$emission_kg'}
            }
        }},
        {'$set': {
            'by_category': {
                '$arrayToObject': {
                    '$map': {
                        'input': {
                            '$setUnion': ['$by_category.k', []]
                        },
                        'as': 'cat',
                        'in': {
                            'k': '$$cat',
                            'v': {
                                '$sum': {
                                    '$map': {
                                        'input': '$by_category',
                                        'as': 'x',
                                        'in': {
                                            '$cond': [
                                                {'$eq': ['$$x.k', '$$cat']},
                                                '$$x.v',
                                                0
                                            ]
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }},
        {'$project': {'_id': 0}}
    ]

    agg = list(db.activities.aggregate(pipeline))
    if not agg:
        return jsonify({'total_kg': 0, 'by_category': {'transport': 0, 'energy': 0, 'food': 0}})

    res = agg[0]
    # Ensure missing keys are present
    for k in ['transport', 'energy', 'food']:
        res['by_category'][k] = float(res['by_category'].get(k, 0))
    res['total_kg'] = float(res.get('total_kg', 0))
    return jsonify(res)


@analytics_bp.get('/trend')
@jwt_required()
def trend():
    db = get_db()
    uid = ObjectId(get_jwt_identity())

    start = request.args.get('start')
    end = request.args.get('end')

    match = {'user_id': uid}
    if start or end:
        match['date'] = {}
        if start:
            match['date']['$gte'] = start
        if end:
            match['date']['$lte'] = end

    pipeline = [
        {'$match': match},
        {'$group': {
            '_id': '$date',
            'total_kg': {'$sum': '$emission_kg'},
            'transport': {'$sum': {'$cond': [{'$eq': ['$category', 'transport']}, '$emission_kg', 0]}},
            'energy': {'$sum': {'$cond': [{'$eq': ['$category', 'energy']}, '$emission_kg', 0]}},
            'food': {'$sum': {'$cond': [{'$eq': ['$category', 'food']}, '$emission_kg', 0]}},
        }},
        {'$sort': {'_id': 1}},
        {'$project': {'date': '$_id', '_id': 0, 'total_kg': 1, 'transport': 1, 'energy': 1, 'food': 1}}
    ]

    data = list(db.activities.aggregate(pipeline))
    # Cast float values and ensure order
    out = []
    for d in data:
        out.append({
            'date': d['date'],
            'total_kg': float(d.get('total_kg', 0)),
            'transport': float(d.get('transport', 0)),
            'energy': float(d.get('energy', 0)),
            'food': float(d.get('food', 0)),
        })
    return jsonify({'items': out})


@analytics_bp.get('/comparison')
@jwt_required()
def comparison():
    """Compare current period with previous period.
    period: 'week' or 'month'. Defaults to month.
    """
    db = get_db()
    uid = ObjectId(get_jwt_identity())
    period = (request.args.get('period') or 'month').lower()

    today = datetime.utcnow().date()

    if period == 'week':
        cur_start = (today - timedelta(days=today.weekday()))
        prev_start = cur_start - timedelta(days=7)
        prev_end = cur_start - timedelta(days=1)
    else:  # month
        cur_start = today.replace(day=1)
        prev_end = cur_start - timedelta(days=1)
        prev_start = prev_end.replace(day=1)

    def _sum_between(start_d, end_d):
        s = start_d.strftime('%Y-%m-%d')
        e = end_d.strftime('%Y-%m-%d')
        pipe = [
            {'$match': {'user_id': uid, 'date': {'$gte': s, '$lte': e}}},
            {'$group': {'_id': None, 'total': {'$sum': '$emission_kg'}}}
        ]
        r = list(db.activities.aggregate(pipe))
        return float(r[0]['total']) if r else 0.0

    current_total = _sum_between(cur_start, today)
    previous_total = _sum_between(prev_start, prev_end)

    change = None
    if previous_total > 0:
        change = ((current_total - previous_total) / previous_total) * 100.0

    return jsonify({
        'period': period,
        'current_total_kg': current_total,
        'previous_total_kg': previous_total,
        'percent_change': change
    })
