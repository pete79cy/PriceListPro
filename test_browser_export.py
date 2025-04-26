"""
Test script for browser-based bulk export functionality.
This script will test the bulk export button from a browser perspective.
"""

import os
import logging
import time
from app import app, db
from models import User
from werkzeug.security import generate_password_hash
from flask_login import login_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_or_create_test_user():
    """Get an existing test user or create a new one"""
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        if not user:
            logger.info("Creating test user...")
            user = User(
                username='testuser',
                email='test@example.com',
                password_hash=generate_password_hash('testpassword')
            )
            db.session.add(user)
            db.session.commit()
            logger.info(f"Created test user with ID: {user.id}")
        return user

def test_export_endpoint():
    """Test that the bulk export endpoint returns a file"""
    with app.test_client() as client:
        with app.app_context():
            # Get or create a test user
            user = get_or_create_test_user()
            
            # Log in the test user
            client.post('/login', data={
                'username': 'testuser',
                'password': 'testpassword'
            }, follow_redirects=True)
            
            # Request the bulk export endpoint (no filters)
            logger.info("Testing bulk export endpoint...")
            
            response = client.get('/quotations/bulk-export-excel')
            
            # Check the response
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type')
                content_disposition = response.headers.get('Content-Disposition')
                
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Content-Type: {content_type}")
                logger.info(f"Content-Disposition: {content_disposition}")
                
                # Check that it's a zip file
                if 'application/zip' in content_type and 'attachment' in content_disposition:
                    logger.info("✅ Endpoint returns a zip file as expected")
                    
                    # Save the file to verify its contents
                    filename = content_disposition.split('filename=')[1].strip('"')
                    with open(os.path.join('test_exports', filename), 'wb') as f:
                        f.write(response.data)
                    
                    logger.info(f"Saved response to test_exports/{filename}")
                    return True
                else:
                    logger.error(f"❌ Unexpected response type: {content_type}")
                    logger.error(f"Content disposition: {content_disposition}")
                    return False
            else:
                logger.error(f"❌ Endpoint returned status code {response.status_code}")
                logger.error(f"Response: {response.data.decode('utf-8')[:200]}...")
                return False

if __name__ == '__main__':
    logger.info("===== Testing Bulk Export Endpoint =====")
    
    # Create test output directory
    os.makedirs('test_exports', exist_ok=True)
    
    # Test the endpoint
    result = test_export_endpoint()
    
    if result:
        logger.info("✅ Bulk export endpoint test PASSED")
    else:
        logger.error("❌ Bulk export endpoint test FAILED")