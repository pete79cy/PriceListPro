"""
Enhanced PDF generator with specific fixes for item #10 being skipped during PDF generation.
This module addresses WeasyPrint pagination issues by improving CSS handling and table rendering.
"""

import os
import uuid
import logging
from datetime import datetime
from flask import render_template
from weasyprint import HTML, CSS
from app import db
from models import CompanySettings
from utils.image_utils import get_logo_data

# Configure logger
logger = logging.getLogger(__name__)

def generate_quotation_pdf_v2(quotation, upload_folder, use_modern_template=False, debug=False):
    """
    Enhanced version of generate_quotation_pdf with improved WeasyPrint handling.
    Specifically addresses issues with missing rows (#10) in PDFs.
    
    Args:
        quotation: The Quotation object
        upload_folder: The directory where to save the PDF
        use_modern_template: Whether to use the modern template design (default False)
        debug: Whether to enable debugging features (default False)
        
    Returns:
        str: Path to the generated PDF file
    """
    try:
        # Calculate VAT based on rates
        vat_dict = {}  # Dictionary to track VAT by rate
        subtotal = 0
        
        # Count items to verify data
        item_count = len(quotation.items) if quotation.items else 0
        logger.info(f"Generating enhanced PDF for quotation {quotation.quotation_number} with {item_count} items")
        
        # Explicitly create a sorted list of all items to ensure proper ordering
        sorted_items = list(quotation.items)
        sorted_items.sort(key=lambda x: x.position if hasattr(x, 'position') and x.position is not None else 0)
        
        # Log info about all items for debugging
        if debug:
            for i, item in enumerate(sorted_items, 1):
                logger.info(f"Item #{i}: ID={getattr(item, 'id', 'unknown')}, "
                            f"Position={getattr(item, 'position', 'unknown')}, "
                            f"Description={getattr(item, 'description', 'unknown')[:30]}")
        
        # Calculate financial totals
        for item in sorted_items:
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
        
        # Prepare debug styles if needed
        debug_styles = """
        <style>
          table {
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
            page-break-inside: auto;
          }
          thead { display: table-header-group; }
          tfoot { display: table-footer-group; }
          tr { 
            page-break-inside: avoid !important; 
            break-inside: avoid !important;
            visibility: visible !important;
            display: table-row !important;
          }
          th, td {
            border: 1px solid black;
            padding: 6px;
            text-align: left;
            vertical-align: top;
            word-break: break-word !important;
            overflow-wrap: break-word !important;
            overflow: visible !important;
          }
          tr.debug-row-10 {
            background-color: yellow !important;
            border: 2px solid red !important;
          }
        </style>
        """ if debug else """
        <style>
          table {
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
            page-break-inside: auto;
          }
          thead { display: table-header-group; }
          tfoot { display: table-footer-group; }
          tr { 
            page-break-inside: avoid !important; 
            break-inside: avoid !important;
            visibility: visible !important;
            display: table-row !important;
          }
          th, td {
            text-align: left;
            vertical-align: top;
            word-break: break-word !important;
            overflow-wrap: break-word !important;
            overflow: visible !important;
          }
        </style>
        """
        
        # Choose template based on flag
        template_name = 'pdf/modern_quotation_template.html' if use_modern_template else 'pdf/quotation_template.html'
        
        # Generate HTML content from the template
        html_content = render_template(
            template_name,
            quotation=quotation,
            customer=quotation.customer,
            items=sorted_items,  # Use our explicitly sorted items
            subtotal=subtotal,
            vat_list=vat_list,
            grand_total=grand_total,
            currency=quotation.currency,
            date_generated=datetime.now().strftime('%Y-%m-%d %H:%M'),
            company=company,
            logo_data=logo_data,
            orientation=orientation,
            debug_styles=debug_styles,  # Pass debug styles to template
            debug=debug  # Pass debug flag
        )
        
        # Generate a unique filename
        prefix = "debug_" if debug else ""
        template_type = f"{prefix}modern_" if use_modern_template else f"{prefix}"
        filename = f"{template_type}quotation_{quotation.quotation_number}_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(upload_folder, filename)
        
        # Define additional CSS to handle pagination issues
        css_string = """
        @page { margin: 1.5cm; }
        table { page-break-inside: auto; }
        thead { display: table-header-group; }
        tfoot { display: table-footer-group; }
        tr { 
            page-break-inside: avoid !important; 
            break-inside: avoid !important;
            visibility: visible !important;
            display: table-row !important;
        }
        td, th { 
            word-break: break-word !important;
            overflow-wrap: break-word !important;
            overflow: visible !important;
        }
        """
        
        # Generate PDF from HTML with custom CSS
        HTML(string=html_content).write_pdf(
            output_path,
            stylesheets=[CSS(string=css_string)]
        )
        
        logger.info(f"Enhanced PDF successfully generated: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error generating enhanced quotation PDF: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise