import os

from app import app, db
from utils.version_tracker import get_current_version, log_deployment
from utils.logger import logger
from admin import init_admin_views  # Import the admin initialization function
# The orders blueprint is already registered in app.py

# Initialize Flask-Admin with the app and db
with app.app_context():
    init_admin_views(app, db)

if __name__ == "__main__":
    version = get_current_version()
    logger.info(f"Starting application version {version}")
    log_deployment()
    logger.info("Flask-Admin is enabled")
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}
    app.run(host="0.0.0.0", port=port, debug=debug)
