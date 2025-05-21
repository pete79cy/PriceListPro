"""
Fixed PDF generator that properly handles multiple VAT rates.
This module specifically addresses the issue with VAT calculation display in quotations
that have items with different VAT rates (like 19% and 5%).
"""

import os
import uuid
import logging
from datetime import datetime
from flask import render_template
from weasyprint import HTML, CSS
from models import CompanySettings
from utils.image_utils import get_logo_data

# Configure logger
logger = logging.getLogger(__name__)

def generate_fixed_quotation_pdf(quotation, upload_folder, use_modern_template=True, debug=False):
    """
    Fixed version of quotation PDF generator that resolves VAT calculation display issues.
    
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
        vat_dict = {}
        subtotal = 0
        
        # Count items to verify data
        item_count = len(quotation.items) if quotation.items else 0
        logger.info(f"Generating fixed VAT PDF for quotation {quotation.quotation_number} with {item_count} items")
        
        # Create a sorted list of items by position to ensure proper ordering
        sorted_items = list(quotation.items)
        sorted_items.sort(key=lambda x: x.position if hasattr(x, 'position') and x.position is not None else 0)
        
        # Log info about all items for debugging
        if debug:
            for i, item in enumerate(sorted_items, 1):
                logger.info(f"Item #{i}: ID={getattr(item, 'id', 'unknown')}, "
                            f"Position={getattr(item, 'position', 'unknown')}, "
                            f"Description={getattr(item, 'description', 'unknown')[:30]}")
        
        # Calculate financial totals for each item
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
        
        # Convert to sorted list for template to ensure consistent order
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
        
        # Use modern template
        template_name = 'pdf/modern_quotation_template.html'
        
        # Generate HTML content from the template
        html_content = render_template(
            template_name,
            quotation=quotation,
            customer=quotation.customer,
            items=sorted_items,  # Use our explicitly sorted items
            subtotal=subtotal,
            vat_list=vat_list,  # This is now sorted by VAT rate
            grand_total=grand_total,
            currency=quotation.currency,
            date_generated=datetime.now().strftime('%Y-%m-%d %H:%M'),
            company=company,
            logo_data=logo_data,
            orientation=orientation
        )
        
        # Save the HTML for inspection if in debug mode
        if debug:
            debug_html_path = os.path.join(upload_folder, f"debug_{quotation.quotation_number}.html")
            with open(debug_html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"Debug HTML saved to: {debug_html_path}")
        
        # Generate a unique filename
        prefix = "vat_fixed_"
        filename = f"{prefix}quotation_{quotation.quotation_number}_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(upload_folder, filename)
        
        # Define enhanced CSS to fix VAT display and other layout issues
        css_string = """
        @page { 
            margin: 1.5cm;
        }
        table { 
            page-break-inside: auto;
            box-sizing: border-box;
        }
        thead { 
            display: table-header-group;
        }
        tr { 
            page-break-inside: avoid !important;
            break-inside: avoid !important;
        }
        .summary-block {
            page-break-inside: avoid !important;
        }
        .summary-block .label {
            font-weight: 600;
            text-align: left;
            color: #2c3e50;
        }
        .summary-block .amount {
            font-weight: 600;
            text-align: right;
            color: #2c3e50;
        }
        """
        
        # Generate PDF with enhanced CSS
        HTML(string=html_content).write_pdf(
            output_path, 
            stylesheets=[CSS(string=css_string)]
        )
        
        logger.info(f"Fixed VAT quotation PDF generated: {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error generating fixed VAT quotation PDF: {str(e)}")
        raise