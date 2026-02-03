import time
from typing import List, Dict
from ..config import load_config
from ..db import get_db

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


def _rate_limited(uid: str) -> bool:
    cfg = load_config()
    db = get_db()
    now = int(time.time())
    window = int(cfg['AI_RATE_LIMIT_SECONDS'])
    doc = db.ai_usage.find_one({'user_id': uid})
    if doc and now - int(doc.get('last_ts', 0)) < window:
        return True
    db.ai_usage.update_one({'user_id': uid}, {'$set': {'last_ts': now}}, upsert=True)
    return False


def _heuristic_recommendations(summary: Dict, recent: List[Dict]) -> List[Dict]:
    out = []
    transport = float(summary.get('by_category', {}).get('transport', 0))
    energy = float(summary.get('by_category', {}).get('energy', 0))
    food = float(summary.get('by_category', {}).get('food', 0))

    if transport > energy and transport > food:
        out.append({'category': 'transport', 'advice': 'Use public transit or carpool twice a week to cut commute emissions.'})
        out.append({'category': 'transport', 'advice': 'Batch errands to reduce short car trips that have cold-engine penalties.'})
    if energy >= max(transport, food):
        out.append({'category': 'energy', 'advice': 'Shift to LED lighting and turn off idle electronics to reduce kWh consumption.'})
        out.append({'category': 'energy', 'advice': 'Set AC to 24°C and use fans to reduce cooling load.'})
    if food >= max(transport, energy):
        out.append({'category': 'food', 'advice': 'Swap two beef meals per week with plant-based alternatives.'})
        out.append({'category': 'food', 'advice': 'Plan meals to reduce food waste and choose seasonal produce.'})

    if not out:
        out.append({'category': 'general', 'advice': 'Track activities daily and target one category each week for improvement.'})
    return out[:6]


def generate_recommendations(uid: str, profile: Dict, summary: Dict, recent: List[Dict]) -> Dict:
    cfg = load_config()
    if _rate_limited(uid):
        return {'source': 'rate_limit', 'items': _heuristic_recommendations(summary, recent)}

    api_key = cfg.get('OPENAI_API_KEY')
    model = cfg.get('AI_MODEL', 'gpt-4o-mini')

    sys_prompt = (
        "You are a sustainability coach. Analyze the user’s recent carbon emissions and provide 6 concise, high-impact, personalized recommendations. "
        "Tailor advice across transport, energy, and food. Each item must be a single sentence. Output JSON with an array 'items', each having keys 'category' and 'advice'. Categories must be one of: transport, energy, food, general."
    )

    user_payload = {
        'profile': {
            'name': profile.get('name', ''),
            'email': profile.get('email', '')
        },
        'summary': summary,
        'recent': recent[:50]
    }

    if not api_key or OpenAI is None:
        return {'source': 'heuristic', 'items': _heuristic_recommendations(summary, recent)}

    try:
        client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": str(user_payload)}
            ],
            temperature=0.4,
            max_tokens=400
        )
        text = completion.choices[0].message.content
        import json
        data = None
        try:
            data = json.loads(text)
        except Exception:
            # try to extract json
            import re
            m = re.search(r"\{[\s\S]*\}", text)
            if m:
                data = json.loads(m.group(0))
        if isinstance(data, dict) and isinstance(data.get('items'), list):
            items = []
            for it in data['items']:
                cat = str(it.get('category', 'general')).lower()
                if cat not in ['transport', 'energy', 'food', 'general']:
                    cat = 'general'
                advice = str(it.get('advice', '')).strip()
                if advice:
                    items.append({'category': cat, 'advice': advice})
            if items:
                return {'source': 'openai', 'items': items[:10]}
    except Exception:
        pass

    return {'source': 'fallback', 'items': _heuristic_recommendations(summary, recent)}
