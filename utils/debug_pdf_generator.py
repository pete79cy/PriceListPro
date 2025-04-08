"""
Debug version of the PDF generator to diagnose missing item issues.
This version adds detailed logging during PDF generation.
"""

import os
import io
import uuid
import base64
import logging
from datetime import datetime
from flask import render_template, current_app
from weasyprint import HTML, CSS
from utils.logger import logger
from models import CompanySettings, QuotationItem

# Setup specific logger for this module
debug_logger = logging.getLogger("pdf_debug")
debug_logger.setLevel(logging.DEBUG)
if not debug_logger.handlers:
    # Add console handler if none exists
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    debug_logger.addHandler(ch)
    
    # Add file handler
    fh = logging.FileHandler('pdf_debug.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    debug_logger.addHandler(fh)

def get_logo_data(company):
    """
    Helper function to get company logo data in base64 format
    """
    # Import the original function to maintain functionality
    from utils.pdf_generator import get_logo_data as original_get_logo_data
    return original_get_logo_data(company)

def debug_quotation_pdf(quotation, upload_folder, use_modern_template=False, save_html=True):
    """
    Debugging version of generate_quotation_pdf that logs detailed information
    to diagnose the missing item #14 issue.
    
    Args:
        quotation: The Quotation object
        upload_folder: The directory where to save the PDF
        use_modern_template: Whether to use the modern template design (default False)
        save_html: Save the generated HTML to a file for inspection (default True)
        
    Returns:
        str: Path to the generated PDF file
    """
    try:
        debug_logger.info("-" * 80)
        debug_logger.info(f"Starting PDF generation for quotation {quotation.quotation_number}")
        debug_logger.info(f"Using {'modern' if use_modern_template else 'standard'} template")
        
        # Log item count and details before processing
        items_count = len(quotation.items) if quotation.items else 0
        debug_logger.info(f"Quotation has {items_count} items")
        
        # Log each item's basic info to identify issues
        for idx, item in enumerate(quotation.items, 1):
            debug_logger.info(f"Item #{idx}: ID={item.id}, Position={item.position}, "
                             f"Description='{item.description[:30]}{'...' if len(item.description) > 30 else ''}'")
        
        # Calculate VAT based on rates (same as original function)
        vat_dict = {}  # Dictionary to track VAT by rate
        subtotal = 0
        
        for item in quotation.items:
            item_subtotal = item.quantity * item.selling_price
            subtotal += item_subtotal
            
            # Track VAT amounts by rate
            vat_rate = item.vat_rate
            vat_amount = item_subtotal * (vat_rate / 100)
            
            if vat_rate in vat_dict:
                vat_dict[vat_rate] += vat_amount
            else:
                vat_dict[vat_rate] = vat_amount
        
        # Convert to list for template
        vat_list = [{'rate': rate, 'label': f'VAT {rate}%', 'amount': amount} for rate, amount in vat_dict.items()]
        
        # Calculate grand total
        grand_total = subtotal + sum(item['amount'] for item in vat_list)
        
        # Get company settings
        company = CompanySettings.query.first()
        if not company:
            company = CompanySettings()  # Use default values if no settings exist
        
        # Get logo data
        logo_data = get_logo_data(company)
        
        # Set the orientation based on company settings
        orientation = company.pdf_orientation  # 'portrait' or 'landscape'
        
        # Choose template based on flag
        template_name = 'pdf/modern_quotation_template.html' if use_modern_template else 'pdf/quotation_template.html'
        debug_logger.info(f"Using template: {template_name}")
        
        # Prepare a sorted list of items by position for direct use in template
        sorted_items = sorted(quotation.items, key=lambda x: x.position if x.position is not None else 0)
        debug_logger.info(f"Sorted items count: {len(sorted_items)}")
        for idx, item in enumerate(sorted_items, 1):
            debug_logger.info(f"Sorted Item #{idx}: ID={item.id}, Position={item.position}")
        
        # Generate HTML content from the selected template
        debug_logger.info("Generating HTML content from template")
        html_content = render_template(
            template_name,
            quotation=quotation,
            customer=quotation.customer,
            items=sorted_items,  # Use the explicitly sorted items
            subtotal=subtotal,
            vat_list=vat_list,
            grand_total=grand_total,
            currency=quotation.currency,
            date_generated=datetime.now().strftime('%Y-%m-%d %H:%M'),
            company=company,
            logo_data=logo_data,
            orientation=orientation
        )
        
        # Optionally save HTML for debugging
        if save_html:
            html_filename = f"debug_{quotation.quotation_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            html_path = os.path.join(upload_folder, html_filename)
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            debug_logger.info(f"Saved HTML for debugging to: {html_path}")
        
        # Generate a unique filename
        template_type = "debug_" if use_modern_template else "debug_standard_"
        filename = f"{template_type}quotation_{quotation.quotation_number}_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(upload_folder, filename)
        
        # Add fixed row styles to ensure no items are skipped
        debug_logger.info("Generating PDF with custom CSS for row handling")
        css_string = """
        @page { margin: 1.5cm; }
        table tr { page-break-inside: avoid !important; }
        td { overflow-wrap: break-word; word-break: break-word; }
        """
        
        # Generate PDF from HTML with custom CSS
        HTML(string=html_content).write_pdf(
            output_path,
            stylesheets=[CSS(string=css_string)]
        )
        
        debug_logger.info(f"PDF generation completed successfully: {output_path}")
        
        return output_path
    
    except Exception as e:
        debug_logger.error(f"Error generating debug quotation PDF: {str(e)}")
        import traceback
        debug_logger.error(traceback.format_exc())
        raise