"""
Serve Frontend Module
--------------------
This module handles serving the React frontend from the Flask application.
"""

import os
from flask import Blueprint, send_from_directory, current_app

# Create a blueprint for serving the frontend
frontend_bp = Blueprint('frontend', __name__)

def register_frontend_routes(app):
    """Register the frontend routes with the app"""
    app.register_blueprint(frontend_bp)
    
    # Define the directory where the built frontend assets are
    app.frontend_dir = os.path.join(os.path.dirname(app.root_path), 'frontend', 'dist')
    
    # Register routes to serve frontend
    @frontend_bp.route('/', defaults={'path': ''})
    @frontend_bp.route('/<path:path>')
    def serve_frontend(path):
        """Serve the built React frontend"""
        # If the path corresponds to an API route, let Flask handle it
        if path.startswith('api/'):
            return current_app.handle_http_exception(404)
        
        # If the path includes a file extension, try to serve it as a static file
        if '.' in path:
            # Get the requested file's path
            file_path = os.path.join(app.frontend_dir, path)
            
            # Check if the file exists
            if os.path.isfile(file_path):
                directory, filename = os.path.split(file_path)
                return send_from_directory(directory, filename)
        
        # For all other routes, serve the index.html file
        # This handles React Router's client-side routing
        return send_from_directory(app.frontend_dir, 'index.html')