import os
from dotenv import load_dotenv

load_dotenv()


def load_config():
    return {
        'MONGO_URI': os.getenv('MONGO_URI', 'mongodb://localhost:27017'),
        'MONGO_DB_NAME': os.getenv('MONGO_DB_NAME', 'carbon_app'),
        'JWT_SECRET': os.getenv('JWT_SECRET', 'change-this-secret'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
        'AI_MODEL': os.getenv('AI_MODEL', 'gpt-4o-mini'),
        'CORS_ORIGINS': os.getenv('CORS_ORIGINS', '*'),
        'RECOMMENDATION_WINDOW_DAYS': int(os.getenv('RECOMMENDATION_WINDOW_DAYS', '30')),
        'AI_RATE_LIMIT_SECONDS': int(os.getenv('AI_RATE_LIMIT_SECONDS', '30')),
    }
