from app import app
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('plant_pricing_system')

if __name__ == "__main__":
    logger.info("Starting Plant Pricing System backend server")
    app.run(host="0.0.0.0", port=5000, debug=True)
