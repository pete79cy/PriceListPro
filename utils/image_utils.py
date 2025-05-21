"""
Image utilities for the application.
This module handles image processing, resizing, and conversion to formats suitable
for embedding in PDF documents.
"""

import os
import base64
from flask import url_for

def get_logo_data(company=None):
    """
    Get logo data as a base64 string for embedding in HTML/PDF.
    Uses company logo if available, otherwise falls back to default logo.
    
    Args:
        company: CompanySettings object with logo_path attribute
        
    Returns:
        str: Base64 data URL for the logo
    """
    try:
        # Check if company has a logo
        if company and hasattr(company, 'logo_path') and company.logo_path:
            logo_path = os.path.join('static', company.logo_path)
            
            # Verify file exists
            if os.path.isfile(logo_path):
                with open(logo_path, 'rb') as f:
                    logo_data = f.read()
                    
                # Get file extension
                _, ext = os.path.splitext(logo_path)
                ext = ext.lower().strip('.')
                
                # Default to png if extension is missing
                if not ext:
                    ext = 'png'
                    
                # Create base64 data URL
                return f"data:image/{ext};base64,{base64.b64encode(logo_data).decode('utf-8')}"
        
        # Fallback to default logo from static folder
        default_logo = os.path.join('static', 'img', 'default-logo.png')
        
        if os.path.isfile(default_logo):
            with open(default_logo, 'rb') as f:
                logo_data = f.read()
            return f"data:image/png;base64,{base64.b64encode(logo_data).decode('utf-8')}"
            
        # Ultimate fallback - return None if no logo available
        return None
        
    except Exception as e:
        print(f"Error loading logo: {str(e)}")
        return None