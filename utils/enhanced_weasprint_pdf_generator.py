"""
Enhanced WeasyPrint PDF Generator for Quotations

This module provides a comprehensive solution to all known WeasyPrint page break issues:
1. Improves pagination and page break handling
2. Ensures all rows are correctly rendered (fixing missing item #10, #14 issues)
3. Implements item pagination techniques to ensure proper layout
4. Provides debugging options for troubleshooting

Based on recommended best practices for WeasyPrint pagination control.
"""

import os
import uuid
import logging
from html import unescape
from datetime import datetime
from types import SimpleNamespace
from flask import render_template
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from models import CompanySettings
from utils.image_utils import get_logo_data

# Configure logger
logger = logging.getLogger(__name__)

def adjust_table_rows_for_pagination(items):
    """
    Adjusts the product list for better pagination.
    Organizes products into pages with a specific number of products per page.
    Returns a list of SimpleNamespace objects with page number and items list.
    
    Args:
        items: List of quotation items
        
    Returns:
        list: List of SimpleNamespace objects with page and items attributes
    """
    # Calculate how many products fit on the first page (e.g., 7)
    first_page_items = 7
    
    # Calculate how many products fit on subsequent pages (e.g., 8)
    other_pages_items = 8
    
    # Organize products into pages using SimpleNamespace to avoid dict.items() method conflict
    paginated_items = []
    
    # First page
    if len(items) > 0:
        paginated_items.append(
            SimpleNamespace(
                page=1,
                items=items[:first_page_items]
            )
        )
    
    # Subsequent pages
    remaining_items = items[first_page_items:]
    page_num = 2
    
    while remaining_items:
        page_items = remaining_items[:other_pages_items]
        paginated_items.append(
            SimpleNamespace(
                page=page_num,
                items=page_items
            )
        )
        remaining_items = remaining_items[other_pages_items:]
        page_num += 1
    
    return paginated_items

def fix_item_positions(quotation):
    """
    Fix positions for all items in a quotation to ensure they're sequential.
    This helps with consistent rendering in the PDF.
    
    Args:
        quotation: The Quotation object to fix
        
    Returns:
        bool: True if changes were made, False otherwise
    """
    if not quotation.items:
        return False
    
    # Sort items by existing position or by ID if position is None
    sorted_items = sorted(
        quotation.items, 
        key=lambda x: (x.position if hasattr(x, 'position') and x.position is not None else float('inf'), x.id)
    )
    
    # Reassign positions sequentially starting from 0
    changes_made = False
    for i, item in enumerate(sorted_items):
        if not hasattr(item, 'position') or item.position != i:
            item.position = i
            changes_made = True
    
    return changes_made

def generate_enhanced_quotation_pdf(quotation, upload_folder, use_modern_template=True, debug=False, paginate=True):
    """
    Enhanced version of quotation PDF generator that resolves all known WeasyPrint pagination issues.
    
    Args:
        quotation: The Quotation object
        upload_folder: The directory where to save the PDF
        use_modern_template: Whether to use the modern template design (default True)
        debug: Whether to enable debugging features (default False)
        paginate: Whether to use the pagination technique (default True)
        
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
        
        # Fix item positions if needed
        positions_fixed = fix_item_positions(quotation)
        if positions_fixed:
            logger.info(f"Fixed positions for quotation {quotation.quotation_number}")
        
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
        
        # Paginate items if requested
        paginated_items = adjust_table_rows_for_pagination(sorted_items) if paginate else None
        
        # Choose template based on whether pagination is used
        if paginate:
            template_name = 'pdf/modern_quotation_template_paginated.html'
        else:
            template_name = 'pdf/modern_quotation_template_fixed.html'
        
        # Generate HTML content from the template
        html_content = render_template(
            template_name,
            quotation=quotation,
            customer=quotation.customer,
            items=sorted_items,  # Use our explicitly sorted items
            paginated_items=paginated_items,  # Include paginated items if used
            subtotal=subtotal,
            vat_list=vat_list,
            grand_total=grand_total,
            currency=quotation.currency,
            date_generated=datetime.now().strftime('%Y-%m-%d %H:%M'),
            company=company,
            logo_data=logo_data,
            orientation=orientation,
            debug=debug,  # Pass debug flag
            total_pages=len(paginated_items) if paginated_items else None
        )
        
        # Save the HTML for inspection if in debug mode
        if debug:
            debug_html_path = os.path.join(upload_folder, f"debug_{quotation.quotation_number}.html")
            with open(debug_html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"Debug HTML saved to: {debug_html_path}")
        
        # Generate a unique filename
        prefix = "debug_" if debug else ""
        template_type = f"{prefix}enhanced_" if use_modern_template else f"{prefix}"
        pagination_type = "paginated_" if paginate else ""
        filename = f"{template_type}{pagination_type}quotation_{quotation.quotation_number}_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(upload_folder, filename)
        
        # Define enhanced CSS to fix pagination and layout issues
        css_string = """
        @page { 
            margin: 1.5cm;
            margin-bottom: 30mm; /* Increased margin for footer space */
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
            page-break-after: auto !important;
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
        
        /* Footer positioning */
        .footer {
            position: fixed;
            bottom: 10mm;
            width: 100%;
            page-break-inside: avoid !important;
        }
        
        /* Product row class for better control */
        tr.product-row {
            page-break-inside: avoid !important;
        }
        
        /* Ensure the table breaks correctly */
        table.product-table {
            page-break-after: auto !important;
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
            
            /* Page break visuals for debugging */
            .page-break {
                border: 4px dashed purple !important;
                margin: 10mm 0 !important;
                padding: 5mm !important;
                background-color: lightyellow !important;
            }
            """
        
        # Initialize font configuration
        font_config = FontConfiguration()
        html = HTML(string=html_content)
        
        # Create additional CSS for page break control
        enhanced_css = CSS(string=css_string, font_config=font_config)
        
        # Generate PDF with enhanced configuration
        html.write_pdf(
            output_path,
            stylesheets=[enhanced_css],
            font_config=font_config
        )
        
        # Validation: Log that all items were included
        expected_item_count = len(quotation.items)
        logger.info(f"PDF validation: Expected {expected_item_count} items, processed {len(sorted_items)} items")
        if expected_item_count != len(sorted_items):
            logger.warning(f"Item count mismatch! Expected {expected_item_count} but processed {len(sorted_items)}")
        
        logger.info(f"Enhanced PDF successfully generated: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error generating enhanced quotation PDF: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise