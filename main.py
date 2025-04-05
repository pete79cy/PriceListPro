from app import app
from utils.version_tracker import get_current_version, log_deployment
from utils.logger import logger

if __name__ == "__main__":
    version = get_current_version()
    logger.info(f"Starting application version {version}")
    log_deployment()
    app.run(host="0.0.0.0", port=5000, debug=True)
