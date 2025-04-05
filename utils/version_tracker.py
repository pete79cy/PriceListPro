
import json
from datetime import datetime
from utils.logger import logger

VERSION_FILE = 'version.json'

def get_current_version():
    try:
        with open(VERSION_FILE, 'r') as f:
            data = json.load(f)
            return data.get('version', '0.0.1')
    except FileNotFoundError:
        return '0.0.1'

def increment_version(version_str, increment_type='patch'):
    """Increment semantic version number"""
    major, minor, patch = map(int, version_str.split('.'))
    if increment_type == 'major':
        major += 1
        minor = patch = 0
    elif increment_type == 'minor':
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    return f"{major}.{minor}.{patch}"

def log_deployment(version=None, notes=None, increment_type='patch'):
    try:
        # Read existing data or create new
        try:
            with open(VERSION_FILE, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {
                'version': '0.0.1',
                'deployments': []
            }
        
        # Update version
        current_version = data['version']
        if version:
            new_version = version
        else:
            new_version = increment_version(current_version, increment_type)
        data['version'] = new_version
            
        # Add deployment record
        deployment = {
            'timestamp': datetime.utcnow().isoformat(),
            'version': version or data['version'],
            'notes': notes
        }
        data['deployments'].append(deployment)
        
        # Save updated data
        with open(VERSION_FILE, 'w') as f:
            json.dump(data, f, indent=2)
            
        logger.info(f"Deployment logged - Version: {deployment['version']}")
        return True
    except Exception as e:
        logger.error(f"Error logging deployment: {str(e)}")
        return False
