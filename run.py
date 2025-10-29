# Add this to your app.py or main Flask file
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

# CORS Configuration - Allow requests from your frontend
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:5173",  # Vite default dev server
            "http://localhost:3000",  # Alternative React dev port
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
            # Add your production frontend URL here
            # "https://your-frontend-domain.com"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Initialize JWT
jwt = JWTManager(app)

# Import your routes/blueprints here
# from routes.auth import auth_bp
# from routes.users import users_bp
# etc...

from routes.admin_routes import bp as admins_bp
from routes.auth_routes import bp as auth_bp
from routes.beneficiary_routes import bp as beneficiary_bp
from routes.transaction_routes import bp as trans_bp
from routes.user_routes import bp as users_bp
from routes.wallet_routes import bp as wallet_bp

# Register blueprints
# app.register_blueprint(auth_bp, url_prefix='/api/auth')
# app.register_blueprint(users_bp, url_prefix='/api/users')
# etc...

app.register_blueprint(admins_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(beneficiary_bp)
app.register_blueprint(trans_bp)
app.register_blueprint(users_bp)
app.register_blueprint(wallet_bp)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )