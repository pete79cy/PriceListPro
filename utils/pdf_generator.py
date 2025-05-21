"""
PDF Generator for delivery notes and other documents
Uses WeasyPrint to generate PDFs from HTML templates
"""
import os
import io
from datetime import datetime
from flask import render_template, current_app
from weasyprint import HTML, CSS

from utils.translations import translate_to_language, translate_status

def generate_delivery_note_pdf(order, language='en'):
    """
    Generate a PDF delivery note for an order
    
    Args:
        order: The order object to generate the delivery note for
        language (str): Language code for translations ('en', 'el', 'ar')
        
    Returns:
        bytes: The PDF file as bytes
    """
    # Create a function to translate keys in the template
    def translate(key):
        return translate_to_language(key, language)
    
    # Handle status translation
    def translate_order_status(status_value):
        return translate_status(status_value, language)
    
    # Get current date/time
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # Calculate order totals
    subtotal = sum(item.quantity * item.price for item in order.items)
    vat_rate = 0.24  # 24% VAT rate (can be configurable)
    vat_amount = subtotal * vat_rate
    total = subtotal + vat_amount
    
    # Determine text direction based on language (for Arabic)
    rtl = language == 'ar'
    
    # Generate HTML content
    html_content = render_template(
        'pdfs/delivery_note.html',
        order=order,
        current_date=current_date,
        subtotal=subtotal,
        vat_rate=vat_rate,
        vat_amount=vat_amount,
        total=total,
        translate=translate,
        translate_status=translate_order_status,
        rtl=rtl,
        language=language
    )
    
    # Custom CSS for PDF styling
    css_content = """
        @page {
            size: A4;
            margin: 1.5cm;
            @top-right {
                content: counter(page) " / " counter(pages);
                font-size: 9pt;
            }
        }
        body {
            font-family: 'DejaVu Sans', Arial, sans-serif;
            font-size: 10pt;
            line-height: 1.3;
        }
        /* Direction for Arabic */
        .rtl {
            direction: rtl;
            text-align: right;
        }
        /* Header styles */
        .header {
            border-bottom: 1px solid #555;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .logo {
            max-height: 70px;
            max-width: 200px;
        }
        /* Order info styles */
        .order-info {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        .order-info-item {
            margin-bottom: 5px;
        }
        /* Table styles */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        th {
            background-color: #f2f2f2;
            border-bottom: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .rtl th {
            text-align: right;
        }
        td {
            border-bottom: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .rtl td {
            text-align: right;
        }
        .number-cell {
            text-align: right;
        }
        .rtl .number-cell {
            text-align: left;
        }
        /* Summary styles */
        .summary {
            margin-top: 20px;
            display: flex;
            justify-content: flex-end;
        }
        .summary-table {
            width: 250px;
        }
        /* Status indicator */
        .status {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
            color: white;
        }
        .status-new {
            background-color: #FF9800;
        }
        .status-preparing {
            background-color: #2196F3;
        }
        .status-ready {
            background-color: #4CAF50;
        }
        .status-delivered {
            background-color: #9E9E9E;
        }
        .status-cancelled {
            background-color: #F44336;
        }
        /* Signature section */
        .signatures {
            display: flex;
            justify-content: space-between;
            margin-top: 80px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }
        .signature-box {
            width: 45%;
        }
        .signature-line {
            border-top: 1px solid #555;
            margin-top: 40px;
            padding-top: 5px;
        }
    """
    
    # Create a BytesIO object to store the PDF
    pdf_buffer = io.BytesIO()
    
    # Generate PDF using WeasyPrint
    html = HTML(string=html_content)
    css = CSS(string=css_content)
    html.write_pdf(pdf_buffer, stylesheets=[css])
    
    # Reset buffer position
    pdf_buffer.seek(0)
    
    # Return PDF as bytes
    return pdf_buffer.getvalue()