"""
PDF Generator for delivery notes and other documents
Uses WeasyPrint to generate PDFs from HTML templates
"""
import os
from datetime import datetime
from flask import render_template, current_app
from weasyprint import HTML, CSS
import logging

def generate_delivery_note(order, language='en'):
    """
    Generate a PDF delivery note for an order
    
    Args:
        order: The order object to generate the delivery note for
        language (str): Language code for translations ('en', 'el', 'ar')
        
    Returns:
        bytes: The PDF file as bytes
    """
    try:
        # Render the HTML template
        html_content = render_template(
            'pdfs/delivery_note.html',
            order=order,
            language=language,
            _=lambda x: x  # Placeholder for translation function
        )
        
        # Create a temporary HTML file
        temp_html_path = os.path.join(current_app.static_folder, 'temp_delivery_note.html')
        
        with open(temp_html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Define CSS to improve PDF appearance
        css = CSS(string='''
            @page {
                size: A4;
                margin: 1cm;
            }
            body {
                font-family: Arial, sans-serif;
            }
        ''')
        
        # Generate PDF from HTML
        html = HTML(filename=temp_html_path)
        pdf_content = html.write_pdf(stylesheets=[css])
        
        # Remove the temporary file
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)
        
        return pdf_content
        
    except Exception as e:
        current_app.logger.error(f"Error generating delivery note PDF: {str(e)}")
        return None