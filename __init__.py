from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    # Register blueprints
    from routes import auth_routes, user_routes, wallet_routes, transaction_routes, beneficiary_routes, admin_routes
    
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(user_routes.bp)
    app.register_blueprint(wallet_routes.bp)
    app.register_blueprint(transaction_routes.bp)
    app.register_blueprint(beneficiary_routes.bp)
    app.register_blueprint(admin_routes.bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
        from utils.seed import create_default_admin
        create_default_admin()
    
    return app