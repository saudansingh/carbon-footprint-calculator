import os
from datetime import datetime, timedelta
from random import randint, choice
from pymongo import MongoClient
from werkzeug.security import generate_password_hash

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
DB_NAME = os.getenv('MONGO_DB_NAME', 'carbon_app')

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Create sample user
email = 'demo@example.com'
user = db.users.find_one({'email': email})
if not user:
    user = {
        'email': email,
        'name': 'Demo User',
        'password_hash': generate_password_hash('demopassword'),
        'created_at': datetime.utcnow()
    }
    db.users.insert_one(user)
    user = db.users.find_one({'email': email})

uid = user['_id']

# Clear old demo activities
db.activities.delete_many({'user_id': uid})

start_date = (datetime.utcnow().date() - timedelta(days=60))

def add_activity(date_str, a_type, data, emission_kg, category):
    db.activities.insert_one({
        'user_id': uid,
        'date': date_str,
        'type': a_type,
        'category': category,
        'data': data,
        'emission_kg': round(float(emission_kg), 4),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
    })

# Simple factors
CAR = 0.12
FLIGHT = 0.255
ELECTRICITY = 0.5
BEEF = 6.0
VEG = 1.5

for i in range(0, 60):
    d = start_date + timedelta(days=i)
    ds = d.strftime('%Y-%m-%d')

    # Random commute car km 0-30
    km = randint(0, 30)
    if km > 0:
        add_activity(ds, 'car', {'distance_km': km}, km * CAR, 'transport')

    # 1-3 times a week bus or train
    if d.weekday() in [1, 4] and randint(0, 1):
        km2 = randint(5, 25)
        add_activity(ds, choice(['bus', 'train']), {'distance_km': km2}, km2 * (0.089 if randint(0,1) else 0.041), 'transport')

    # Electricity daily 5-20 kWh
    kwh = randint(5, 20)
    add_activity(ds, 'electricity', {'kwh': kwh}, kwh * ELECTRICITY, 'energy')

    # Meals
    if randint(0, 3) == 0:
        add_activity(ds, 'beef_meal', {'quantity': 1}, BEEF, 'food')
    else:
        add_activity(ds, 'vegetarian_meal', {'quantity': 1}, VEG, 'food')

print('Seeded demo user:', email)
print('Password: demopassword')
