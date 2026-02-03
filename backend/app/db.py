from pymongo import MongoClient, ASCENDING, IndexModel
from bson.objectid import ObjectId
from .config import load_config

_cfg = load_config()
_client = MongoClient(_cfg['MONGO_URI'])
_db = _client[_cfg['MONGO_DB_NAME']]


def get_db():
    return _db


def init_db_indexes():
    users = _db["users"]
    activities = _db["activities"]

    users.create_indexes([
        IndexModel([("email", ASCENDING)], unique=True, name="uniq_email")
    ])

    activities.create_indexes([
        IndexModel([("user_id", ASCENDING), ("date", ASCENDING)], name="user_date_idx"),
        IndexModel([("category", ASCENDING)], name="category_idx"),
    ])


def oid(value):
    if isinstance(value, ObjectId):
        return value
    return ObjectId(str(value))
