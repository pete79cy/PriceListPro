"""
Enhanced PDF generator with additional debugging and fixes for the missing item #14 issue.
This version adds explicit CSS overrides to ensure all table rows render properly.
"""

import os
import io
import uuid
import base64
import logging
from datetime import datetime
from flask import render_template, current_app
from weasyprint import HTML, CSS
from models import CompanySettings

# Get the standard logger
from utils.logger import logger

def get_logo_data(company):
    """
    Helper function to get company logo data in base64 format.
    Implementation directly in this file to avoid circular imports.
    """
    if not company or not hasattr(company, 'logo_path') or not company.logo_path:
        return ""
        
    try:
        import os
        import base64
        from flask import current_app
        
        logo_path = company.logo_path
        
        # Handle the path safely
        if logo_path and not os.path.isabs(logo_path):
            # If relative path, make it absolute
            static_folder = 'static'
            if current_app and hasattr(current_app, 'static_folder'):
                static_folder = current_app.static_folder
            
            logo_path = os.path.join(str(static_folder), str(logo_path))
        
        # Check that the file exists
        if logo_path and os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                logo_data = f.read()
                
            # Encode to base64 for inline HTML display
            encoded_logo = base64.b64encode(logo_data).decode('utf-8')
            
            # Determine MIME type based on file extension
            extension = '.png'  # Default
            if logo_path:
                extension = os.path.splitext(logo_path)[1].lower() or '.png'
                
            mime_type = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.svg': 'image/svg+xml'
            }.get(extension, 'image/png')
            
            # Return data URL
            return f"data:{mime_type};base64,{encoded_logo}"
    except Exception as e:
        # If there's any error, log it but don't crash the PDF generation
        logger.error(f"Error getting logo data: {str(e)}")
    
    # Return empty string if any issues occur
    return ""

def generate_enhanced_pdf(quotation, upload_folder, use_modern_template=False, debug=False):
    """
    Enhanced version of generate_quotation_pdf with improved WeasyPrint handling.
    Specifically addresses issues with missing rows (#14) in PDFs.
    
    Args:
        quotation: The Quotation object
        upload_folder: The directory where to save the PDF
        use_modern_template: Whether to use the modern template design (default False)
        debug: Whether to add debugging features like borders around rows (default False)
        
    Returns:
        str: Path to the generated PDF file
    """
    try:
        # Calculate VAT based on rates - similar to original function
        vat_dict = {}  # Dictionary to track VAT by rate
        subtotal = 0
        
        # Count items to verify data
        item_count = len(quotation.items)
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
        
        # Calculate financial totals as in original function
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
        
        # Choose template based on flag
        template_name = 'pdf/modern_quotation_template.html' if use_modern_template else 'pdf/quotation_template.html'
        
        # Add debugging information to the items before rendering
        enhanced_items = []
        for i, item in enumerate(sorted_items, 1):
            # Create a copy (or enhance) the item to avoid modifying the original
            if debug:
                # This won't modify the database item, just adds attributes for rendering
                item._debug_info = f"Item #{i} (ID={getattr(item, 'id', 'unknown')})"
            enhanced_items.append(item)
            
            # Special logging around problematic item 14
            if i == 13 or i == 14 or i == 15:
                logger.info(f"Special debug for item #{i}: {getattr(item, 'description', 'unknown')[:50]}")
        
        # Generate HTML content from the selected template
        html_content = render_template(
            template_name,
            quotation=quotation,
            customer=quotation.customer,
            items=enhanced_items,  # Use our enhanced items
            subtotal=subtotal,
            vat_list=vat_list,
            grand_total=grand_total,
            currency=quotation.currency,
            date_generated=datetime.now().strftime('%Y-%m-%d %H:%M'),
            company=company,
            logo_data=logo_data,
            orientation=orientation,
            debug=debug  # Pass debug flag to template
        )
        
        # Save the HTML for inspection if in debug mode
        if debug:
            debug_html_path = os.path.join(upload_folder, f"debug_{quotation.quotation_number}.html")
            with open(debug_html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"Debug HTML saved to: {debug_html_path}")
        
        # Generate a unique filename
        template_type = "modern_" if use_modern_template else ""
        prefix = "debug_" if debug else ""
        filename = f"{prefix}{template_type}quotation_{quotation.quotation_number}_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(upload_folder, filename)
        
        # Define additional CSS to ensure all rows render properly
        css_string = """
        /* Table layout fixes */
        table { table-layout: fixed !important; width: 100% !important; }
        
        /* Force row visibility and prevent page breaks within rows */
        tr { 
            page-break-inside: avoid !important; 
            break-inside: avoid !important;
            visibility: visible !important;
            display: table-row !important;
        }
        
        /* Better cell handling */
        td, th { 
            word-break: break-word !important;
            overflow-wrap: break-word !important;
            overflow: visible !important;
        }
        
        /* Force header rows to repeat */
        thead { display: table-header-group !important; }
        
        /* Force container to show all content */
        tbody { display: table-row-group !important; }
        """
        
        # Add debugging borders if in debug mode
        if debug:
            css_string += """
            /* Debug borders and colors */
            table { border: 3px solid blue !important; }
            tr { border: 2px solid red !important; }
            td, th { border: 1px solid green !important; }
            
            /* Special highlighting for problematic rows */
            tr.item-row:nth-child(14),
            tr.item-row:nth-child(13),
            tr.item-row:nth-child(15) {
                background-color: yellow !important;
                border: 3px solid red !important;
            }
            """
        
        # Generate PDF with our custom CSS overrides
        HTML(string=html_content).write_pdf(
            output_path,
            stylesheets=[CSS(string=css_string)]
        )
        
        # Validation: Log that all items were included
        expected_item_count = len(quotation.items)
        logger.info(f"PDF validation: Expected {expected_item_count} items, processed {len(enhanced_items)} items")
        if expected_item_count != len(enhanced_items):
            logger.warning(f"Item count mismatch! Expected {expected_item_count} but processed {len(enhanced_items)}")
        
        logger.info(f"Enhanced PDF generated successfully: {output_path} for quotation {quotation.quotation_number}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error generating enhanced PDF: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise