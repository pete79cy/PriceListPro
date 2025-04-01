import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

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

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") + "?charset=utf8"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "connect_args": {"client_encoding": "utf8"},
}

# Configure file uploads
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models here so tables are created
    import models
    db.create_all()

    # Import and register routes
    from routes import register_routes
    register_routes(app)