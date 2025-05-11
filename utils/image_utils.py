
"""
Image utilities for handling logos and other image assets in PDFs
"""
import os
import base64
from typing import Optional, Dict, Any

def get_logo_data(company_settings: Any) -> Optional[Dict[str, str]]:
    """
    Get logo data for PDF generation
    
    Args:
        company_settings: CompanySettings object containing logo path
        
    Returns:
        Optional[Dict[str, str]]: Dictionary with logo data or None
    """
    try:
        # Default logo path
        default_logo = os.path.join('static', 'images', 'pakkoutis_logo_300x100.png')
        
        # Try to get custom logo from company settings first
        logo_path = None
        if company_settings and hasattr(company_settings, 'logo_path'):
            logo_path = company_settings.logo_path
            
        # Fall back to default if no custom logo
        if not logo_path or not os.path.exists(logo_path):
            logo_path = default_logo
            
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                logo_data = base64.b64encode(f.read()).decode('utf-8')
                return {
                    'data': logo_data,
                    'path': logo_path,
                    'mime_type': 'image/png'
                }
    except Exception as e:
        print(f"Error loading logo: {str(e)}")
        return None
