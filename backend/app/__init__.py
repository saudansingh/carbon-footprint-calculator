import os
from datetime import timedelta
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import load_config
from .db import init_db_indexes

jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    # Load config from env
    cfg = load_config()
    app.config['JWT_SECRET_KEY'] = cfg['JWT_SECRET']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=12)

    # Extensions
    cors_val = cfg['CORS_ORIGINS']
    if isinstance(cors_val, str) and cors_val != '*':
        origins = [o.strip() for o in cors_val.split(',') if o.strip()]
    else:
        origins = cors_val
    CORS(app, resources={r"/api/*": {"origins": origins}})
    jwt.init_app(app)

    # Initialize DB indexes
    init_db_indexes()

    # Blueprints
    from .routes.auth_routes import auth_bp
    from .routes.activity_routes import activity_bp
    from .routes.analytics_routes import analytics_bp
    from .routes.recommendation_routes import recommendation_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(activity_bp, url_prefix='/api/activities')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(recommendation_bp, url_prefix='/api/recommendations')

    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({"status": "ok"}), 200

    return app
