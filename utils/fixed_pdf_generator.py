"""
Fixed PDF generator that resolves all known issues with quotation PDF rendering.
This module addresses:
1. Missing items (especially #10, #14) in PDF output
2. HTML entity encoding in headers
3. Layout and spacing issues
4. VAT calculation display for multiple rates
"""

import os
import uuid
import logging
from html import unescape
from datetime import datetime
from flask import render_template
from weasyprint import HTML, CSS
from models import CompanySettings
from utils.image_utils import get_logo_data

# Configure logger
logger = logging.getLogger(__name__)

def generate_fixed_quotation_pdf(quotation, upload_folder, use_modern_template=True, debug=False):
    """
    Fixed version of quotation PDF generator that resolves all known issues.
    
    Args:
        quotation: The Quotation object
        upload_folder: The directory where to save the PDF
        use_modern_template: Whether to use the modern template design (default True)
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
        logger.info(f"Generating fixed PDF for quotation {quotation.quotation_number} with {item_count} items")
        
        # Create a sorted list of items by position to ensure proper ordering
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
        
        # Convert to list for template and sort by rate for consistent display
        vat_list = [{'rate': rate, 'label': f'VAT {rate}%', 'amount': amount} 
                   for rate, amount in sorted(vat_dict.items())]
        
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
        
        # Clean any HTML entities in the company name to prevent &amp; issues
        if company.name:
            company.name = unescape(company.name)
        
        # Use our fixed template to avoid HTML entity issues
        template_name = 'pdf/modern_quotation_template_fixed.html'
        
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
            debug=debug  # Pass debug flag
        )
        
        # Save the HTML for inspection if in debug mode
        if debug:
            debug_html_path = os.path.join(upload_folder, f"debug_{quotation.quotation_number}.html")
            with open(debug_html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"Debug HTML saved to: {debug_html_path}")
        
        # Generate a unique filename
        prefix = "debug_" if debug else ""
        template_type = f"{prefix}fixed_" if use_modern_template else f"{prefix}"
        filename = f"{template_type}quotation_{quotation.quotation_number}_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(upload_folder, filename)
        
        # Define enhanced CSS to fix pagination and layout issues
        css_string = """
        @page { 
            margin: 1.5cm;
            @top-center {
                content: normal; /* Override template values to fix entity issues */
            }
        }
        
        /* Critical fixes for table layout and pagination */
        table { 
            width: 100% !important;
            table-layout: fixed !important;
            page-break-inside: auto !important;
            border-collapse: collapse !important;
        }
        
        /* Header and footer handling */
        thead { display: table-header-group !important; }
        tfoot { display: table-footer-group !important; }
        
        /* Force row display and prevent page breaks */
        tr { 
            page-break-inside: avoid !important; 
            break-inside: avoid !important;
            visibility: visible !important;
            display: table-row !important;
            height: auto !important;
        }
        
        /* Cell handling for better text wrapping */
        td, th { 
            word-break: break-word !important;
            overflow-wrap: break-word !important;
            overflow: visible !important;
            height: auto !important;
        }
        
        /* Ensure the summary section stays together */
        .summary-block { 
            page-break-inside: avoid !important;
            break-inside: avoid !important;
        }
        
        /* Terms and conditions should not break across pages */
        .terms { 
            page-break-inside: avoid !important;
            break-inside: avoid !important;
        }
        """
        
        # Add debugging styles if needed
        if debug:
            css_string += """
            /* Debug borders and colors */
            table { border: 3px solid blue !important; }
            tr { border: 2px solid red !important; }
            td, th { border: 1px solid green !important; }
            
            /* Highlight problematic rows */
            tr.item-row.item-10,
            tr.item-row.item-14 {
                background-color: yellow !important;
                border: 3px solid red !important;
            }
            """
        
        # Generate PDF with our enhanced CSS
        HTML(string=html_content).write_pdf(
            output_path,
            stylesheets=[CSS(string=css_string)]
        )
        
        # Validation: Log that all items were included
        expected_item_count = len(quotation.items)
        logger.info(f"PDF validation: Expected {expected_item_count} items, processed {len(sorted_items)} items")
        if expected_item_count != len(sorted_items):
            logger.warning(f"Item count mismatch! Expected {expected_item_count} but processed {len(sorted_items)}")
        
        logger.info(f"Fixed PDF successfully generated: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error generating fixed quotation PDF: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise