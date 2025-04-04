import os
import logging

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_cors import CORS

# Set up logging - this will be replaced by the custom logger
logging.basicConfig(level=logging.DEBUG)

# Import our custom logger
try:
    from utils.logger import logger
    logger.info("App module loaded")
except ImportError:
    # This can happen on first load before utils directory exists
    pass

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

def create_app():
    """Create and configure an instance of the Flask application."""
    # Create the app
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

    # Enable CORS for all routes, allowing frontend to make API requests
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Configure the database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "connect_args": {
            "client_encoding": "utf8",
            "options": "-c client_encoding=utf8 -c standard_conforming_strings=on"
        },
    }

    # Configure file uploads
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
    app.config['TEMPLATES_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates/sample_files')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['TEMPLATES_FOLDER'], exist_ok=True)

    # Initialize the extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'  # Route for login page

    # Import frontend routes before registering blueprints
    from backend.serve_frontend import frontend_bp, register_frontend_routes
    
    with app.app_context():
        # Import models to ensure they're registered
        from backend import models
        
        # Create all tables
        db.create_all()
        
        # Create a default admin user if no users exist
        if models.User.query.count() == 0:
            admin_user = models.User(username='admin', is_admin=True)
            admin_user.set_password('admin123')  # Default password - should be changed after first login
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created")
        
        # Import and register routes
        from backend.routes import register_routes
        register_routes(app)
        
        # Import and register API routes
        from backend.api_routes import register_api_routes
        register_api_routes(app)
        
        # Register frontend serving routes
        register_frontend_routes(app)
    
    return app

# Create the application instance
app = create_app()

@login_manager.user_loader
def load_user(user_id):
    from backend.models import User
    return User.query.get(int(user_id))
