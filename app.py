import os
import logging
import traceback

from flask import Flask, request, jsonify
from markupsafe import Markup
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import current_user
from flask_wtf.csrf import CSRFProtect, CSRFError

# Set up logging - this will be replaced by the custom logger
logging.basicConfig(level=logging.DEBUG)

# Create a fallback logger that always exists
logger = logging.getLogger("pricelistpro")
logger.setLevel(logging.INFO)

# Import our custom logger (if available)
try:
    from utils.logger import logger as custom_logger
    logger = custom_logger
    logger.info("App module loaded")
except ImportError as e:
    logger.warning(f"Using fallback logger: {e}")

def register_error_handlers(app):
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        user_id = current_user.id if current_user.is_authenticated else 'anonymous'
        referrer = request.headers.get('Referer', 'unknown')
        logger.warning(f"CSRF Error: {e.description}")
        logger.warning(f"  Route: {request.path} | Method: {request.method}")
        logger.warning(f"  User ID: {user_id} | Referrer: {referrer}")
        logger.warning(f"  User-Agent: {request.headers.get('User-Agent', 'unknown')[:100]}")
        
        if request.headers.get('Accept', '').find('application/json') >= 0 or \
           request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'error': 'CSRF token missing or invalid',
                'message': 'Your session may have expired. Please refresh the page and try again.'
            }), 400
        
        from flask import flash, redirect
        try:
            flash('Η συνεδρία σας έληξε. Παρακαλώ δοκιμάστε ξανά.', 'warning')
        except Exception:
            pass
        if referrer and referrer != 'unknown':
            from urllib.parse import urlparse
            back_url = urlparse(referrer).path or '/'
        elif request.method == 'GET':
            back_url = request.path or '/'
        else:
            back_url = '/'
        return redirect(back_url)
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 Internal Server Error: {str(error)}")
        logger.error(f"Request path: {request.path}")
        logger.error(f"Request method: {request.method}")
        logger.error(f"Request data: {request.get_data()}")
        db.session.rollback()  # Roll back any failed database transactions
        return "Internal Server Error", 500

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        logger.error(f"Unhandled Exception: {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        db.session.rollback()
        return "Internal Server Error", 500

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,  # Recycle connections after 5 minutes
    "pool_pre_ping": True,  # Verify connection before use to prevent stale connections
    "pool_size": 10,  # Maximum number of persistent connections
    "max_overflow": 20,  # Maximum number of connections above pool_size
    "pool_timeout": 30,  # Seconds to wait for a connection from the pool
    "connect_args": {
        "client_encoding": "utf8",
        "options": "-c client_encoding=utf8 -c standard_conforming_strings=on",
        "connect_timeout": 10,  # Connection timeout in seconds
        "keepalives": 1,  # Enable keepalives
        "keepalives_idle": 60,  # Seconds between keepalives
        "keepalives_interval": 10,  # Seconds between keepalive probes
        "keepalives_count": 3  # Number of keepalive probes before considering connection dead
    },
}

# Configure BUILD_ID for PWA cache busting
app.config["BUILD_ID"] = os.environ.get("BUILD_ID", "dev")

app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_NAME'] = 'pricelistpro_session'

from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['PREFERRED_URL_SCHEME'] = 'https'

app.config['WTF_CSRF_TIME_LIMIT'] = 28800

# Configure file uploads
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['TEMPLATES_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates/sample_files')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['TEMPLATES_FOLDER'], exist_ok=True)

# Initialize the app with the extension
db.init_app(app)

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Add custom Jinja2 filters
def nl2br(value):
    """Convert newlines to <br> tags for display in HTML"""
    if not value:
        return ""
    # Convert newlines to <br> and mark as safe HTML
    result = value.replace('\n', '<br>\n')
    return Markup(result)

app.jinja_env.filters['nl2br'] = nl2br

with app.app_context():
    # Import models here so tables are created
    import models
    db.create_all()
    
    # Default admin user creation is handled separately to avoid circular imports
    
    # Import necessary modules
    from flask import request
    import traceback
    
    # Register error handlers
    register_error_handlers(app)
    
    # Check OpenAI API health
    try:
        from services.openai_utils import openai_health_check
        if not openai_health_check():
            logger.warning("⚠️ OpenAI API is not healthy.")
        else:
            logger.info("✅ OpenAI API check successful.")
    except ImportError as e:
        logger.warning(f"OpenAI health check could not be performed: {str(e)}")
    
    # Register Replit Auth blueprint
    from replit_auth import make_replit_blueprint
    app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")
    
    # Import and register routes
    from routes import register_routes
    register_routes(app)
    
    # Import and register Viber integration if available
    try:
        from viber_integration import register_viber_integration
        register_viber_integration(app)
        logger.info("Viber integration registered successfully")
    except (ImportError, Exception) as e:
        logger.warning(f"Viber integration could not be registered: {str(e)}")
        pass
        
    # Register blueprints
    try:
        from blueprints.customer import customer_bp
        from blueprints.quotation import quotation_bp
        from blueprints.orders import orders
        
        app.register_blueprint(customer_bp)
        app.register_blueprint(quotation_bp)
        app.register_blueprint(orders)
        logger.info("Customer, Quotation, and Orders blueprints registered successfully")
        
        # Register Invoice Addenda blueprint
        try:
            from addenda import addenda_bp
            app.register_blueprint(addenda_bp)
            logger.info("Invoice Addenda blueprint registered successfully")
        except (ImportError, Exception) as e:
            logger.warning(f"Invoice Addenda blueprint could not be registered: {str(e)}")
        
        # Register backup blueprint
        try:
            from blueprints.backup import backup_bp
            app.register_blueprint(backup_bp)
            logger.info("Database backup blueprint registered successfully")
        except (ImportError, Exception) as e:
            logger.warning(f"Backup blueprint could not be registered: {str(e)}")
            
        # Register API blueprint
        try:
            from blueprints.routes_api import api
            # Add API token to app config - require token in production, no insecure default
            api_token = os.environ.get("API_TOKEN")
            if not api_token and not app.debug:
                logger.warning("API_TOKEN is not set. API endpoints will be disabled in production.")
                app.config["API_TOKEN"] = None
            else:
                app.config["API_TOKEN"] = api_token
            # Exempt API from CSRF (uses token-based authentication)
            csrf.exempt(api)
            app.register_blueprint(api)
            logger.info("API blueprint registered successfully")
        except (ImportError, Exception) as e:
            logger.warning(f"API blueprint could not be registered: {str(e)}")
            
        # Register Delivery Adjustments blueprint
        try:
            from blueprints.delivery_adjustments import delivery_adjustments
            app.register_blueprint(delivery_adjustments)
            logger.info("Delivery Adjustments blueprint registered successfully")
        except (ImportError, Exception) as e:
            logger.warning(f"Delivery Adjustments blueprint could not be registered: {str(e)}")
    except (ImportError, Exception) as e:
        logger.warning(f"Blueprints could not be registered: {str(e)}")
        pass
