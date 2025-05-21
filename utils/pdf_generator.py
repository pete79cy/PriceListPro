"""
PDF Generator Utility

This module provides functions to generate PDF documents from HTML templates,
with proper handling of pagination, styles, and special characters.
"""
import os
import logging
from datetime import datetime
from io import BytesIO

from flask import render_template
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration

# Configure logging
logger = logging.getLogger(__name__)

# Font configuration
font_config = FontConfiguration()

def generate_pdf(html_content, stylesheets=None):
    """
    Generate a PDF document from HTML content.
    
    Args:
        html_content: The HTML content to convert to PDF
        stylesheets: Optional list of CSS stylesheets to apply
        
    Returns:
        bytes: The generated PDF as bytes
    """
    try:
        # Create a BytesIO buffer to store the PDF
        pdf_buffer = BytesIO()
        
        # Default stylesheets if none provided
        if stylesheets is None:
            stylesheets = []
        
        # Create HTML object
        html = HTML(string=html_content)
        
        # Generate PDF
        html.write_pdf(
            pdf_buffer,
            stylesheets=stylesheets,
            font_config=font_config
        )
        
        # Reset buffer position
        pdf_buffer.seek(0)
        
        # Return the PDF content as bytes
        return pdf_buffer.getvalue()
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise
    
def render_pdf_template(template_path, **context):
    """
    Render a template and convert it to PDF.
    
    Args:
        template_path: Path to the template file
        **context: Context variables to pass to the template
        
    Returns:
        bytes: The generated PDF as bytes
    """
    try:
        # Render the template with the provided context
        html_content = render_template(template_path, **context)
        
        # Generate PDF from the rendered HTML
        pdf_content = generate_pdf(html_content)
        
        return pdf_content
    except Exception as e:
        logger.error(f"Error rendering PDF template {template_path}: {str(e)}")
        raise

def generate_delivery_note_pdf(order, language='en'):
    """
    Generate a delivery note PDF for an order.
    
    Args:
        order: The Order object
        language: Language code for translations (en, el, ar)
        
    Returns:
        bytes: The generated PDF as bytes
    """
    from utils.translations import get_translations
    
    # Get translations for the specified language
    translations = get_translations(language)
    
    # Render the delivery note template with translations
    html_content = render_template(
        'pdfs/delivery_note.html',
        order=order,
        language=language,
        _=translations.gettext  # Translation function
    )
    
    # Generate PDF from the rendered HTML
    pdf_content = generate_pdf(html_content)
    
    return pdf_content