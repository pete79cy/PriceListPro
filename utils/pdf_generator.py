"""
PDF Generator for various documents in the Plant Pricing System.

This module handles the generation of PDF reports including:
- Quotation PDFs
- Supplier reports
- Delivery notes
"""
import os
import uuid
from datetime import datetime
from flask import current_app, render_template
from weasyprint import HTML, CSS
import logging

from models import Quotation, Supplier, Order

logger = logging.getLogger(__name__)

# Ensure PDF output directory exists
def ensure_pdf_dir_exists():
    """Ensure the PDF output directory exists"""
    output_dir = os.path.join(current_app.root_path, 'static', 'pdfs')
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def generate_quotation_pdf(quotation_id):
    """Generate a PDF for a quotation"""
    try:
        # Implementation for quotation PDF (existing functionality)
        pass
    except Exception as e:
        logger.error(f"Error generating quotation PDF: {str(e)}")
        return None

def generate_supplier_pdf_report(supplier_id, template='supplier_report.html'):
    """Generate a PDF report for a supplier"""
    try:
        # Implementation for supplier report (existing functionality)
        pass
    except Exception as e:
        logger.error(f"Error generating supplier PDF report: {str(e)}")
        return None
        
def generate_supplier_products_pdf(supplier_id):
    """Generate a PDF of supplier products"""
    try:
        # Implementation for supplier products PDF (existing functionality)
        pass
    except Exception as e:
        logger.error(f"Error generating supplier products PDF: {str(e)}")
        return None
        
def generate_supplier_catalog_pdf(supplier_id):
    """Generate a supplier catalog PDF"""
    try:
        # Implementation for supplier catalog PDF (existing functionality)
        pass
    except Exception as e:
        logger.error(f"Error generating supplier catalog PDF: {str(e)}")
        return None

def generate_delivery_note_pdf(order_or_orders, language='en', batch=False):
    """
    Generate a PDF delivery note for a single order or multiple orders.
    
    Args:
        order_or_orders: A single Order object or a list of Order objects
        language: Language code for the delivery note ('en', 'el', or 'ar')
        batch: Whether this is a batch delivery note
        
    Returns:
        str: Path to the generated PDF
    """
    try:
        # Ensure we have an output directory
        output_dir = ensure_pdf_dir_exists()
        
        # Set up the template based on language
        if language == 'el':
            template = 'delivery_note_greek.html'
        elif language == 'ar':
            template = 'delivery_note_arabic.html'
        else:
            template = 'delivery_note.html'
        
        # Prepare context for the template
        if batch:
            # Batch delivery note (multiple orders)
            if not isinstance(order_or_orders, list):
                order_or_orders = [order_or_orders]
                
            # Group orders by customer for better organization
            orders_by_customer = {}
            for order in order_or_orders:
                if order.customer_id not in orders_by_customer:
                    orders_by_customer[order.customer_id] = {
                        'customer': order.customer,
                        'orders': []
                    }
                orders_by_customer[order.customer_id]['orders'].append(order)
            
            # Generate a unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'batch_delivery_note_{timestamp}.pdf'
            output_path = os.path.join(output_dir, filename)
            
            # Render the template
            html = render_template(
                f'pdfs/{template}',
                orders_by_customer=orders_by_customer,
                batch=True,
                generation_date=datetime.now(),
                language=language
            )
        else:
            # Single order delivery note
            order = order_or_orders
            # Generate a unique filename
            filename = f'delivery_note_{order.order_number}.pdf'
            output_path = os.path.join(output_dir, filename)
            
            # Render the template
            html = render_template(
                f'pdfs/{template}',
                order=order,
                batch=False,
                generation_date=datetime.now(),
                language=language
            )
        
        # Convert HTML to PDF
        HTML(string=html).write_pdf(
            output_path,
            stylesheets=[
                CSS(string='@page { margin: 1cm; size: a4 portrait; }')
            ]
        )
        
        # Check if file was created
        if os.path.exists(output_path):
            logger.info(f"Delivery note PDF generated: {output_path}")
            return output_path
        else:
            logger.error("Delivery note PDF generation failed: Output file not found")
            return None
            
    except Exception as e:
        logger.error(f"Error generating delivery note PDF: {str(e)}")
        return None