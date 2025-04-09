"""
Flexible PDF Generator for Quotations

This module provides a new approach to generating quotation PDFs with the following features:
- Field selection: Choose which fields to display in the quotation
- Robust layout: Ensures correct pagination and display of all data
- Modern design: Clean, professional appearance with consistent styling
- Error handling: Comprehensive error handling and logging

Dependencies:
- WeasyPrint for PDF generation
- Flask for rendering templates
- HTML/CSS for layout
"""

import os
import uuid
import logging
from datetime import datetime
from html import unescape
from flask import render_template, current_app
from weasyprint import HTML, CSS
from models import CompanySettings

# Configure logger
logger = logging.getLogger(__name__)

# Default field configurations
DEFAULT_ITEM_FIELDS = [
    {'name': 'position', 'label': '#', 'width': '3%', 'align': 'center'},
    {'name': 'description', 'label': 'Description', 'width': '25%', 'align': 'left'},
    {'name': 'scientific_name', 'label': 'Scientific Name', 'width': '22%', 'align': 'left'},
    {'name': 'pot_size', 'label': 'Act. Size', 'width': '8%', 'align': 'left'},
    {'name': 'height', 'label': 'Cust. Spec.', 'width': '8%', 'align': 'left'},
    {'name': 'quantity', 'label': 'Qty', 'width': '7%', 'align': 'center', 'type': 'numeric'},
    {'name': 'selling_price', 'label': 'Unit Price', 'width': '12%', 'align': 'right', 'type': 'currency'},
    {'name': 'total', 'label': 'Total', 'width': '15%', 'align': 'right', 'type': 'currency', 'calculated': True}
]

# Additional available fields that can be selected
AVAILABLE_ITEM_FIELDS = [
    {'name': 'supplier', 'label': 'Supplier', 'width': '15%', 'align': 'left'},
    {'name': 'notes', 'label': 'Notes', 'width': '20%', 'align': 'left'},
    {'name': 'part_number', 'label': 'Part #', 'width': '10%', 'align': 'left'},
    {'name': 'reference', 'label': 'Reference', 'width': '15%', 'align': 'left'},
    {'name': 'cost_price', 'label': 'Cost', 'width': '10%', 'align': 'right', 'type': 'currency', 'admin_only': True},
    {'name': 'margin', 'label': 'Margin', 'width': '8%', 'align': 'right', 'type': 'percentage', 'calculated': True, 'admin_only': True}
]

def get_logo_data(company):
    """
    Helper function to get company logo data in base64 format.
    
    Args:
        company: The CompanySettings object
        
    Returns:
        str: Base64 encoded logo data or None
    """
    try:
        # Import the original function to maintain functionality
        from utils.image_utils import get_logo_data as original_get_logo_data
        return original_get_logo_data(company)
    except (ImportError, Exception) as e:
        logger.warning(f"Could not get logo data: {str(e)}")
        return None

def generate_flexible_quotation_pdf(quotation, selected_fields=None, upload_folder=None, 
                                   template_name=None, orientation=None, debug=False,
                                   include_admin_fields=False, use_modern_style=True):
    """
    Generate a PDF quotation with flexible field selection.
    
    Args:
        quotation: The Quotation object from the database
        selected_fields: List of field names to include (defaults to standard fields)
        upload_folder: Directory to save the PDF (defaults to app's UPLOAD_FOLDER)
        template_name: Name of the template to use
        orientation: 'portrait' or 'landscape'
        debug: Whether to enable debugging features
        include_admin_fields: Whether to include admin-only fields
        use_modern_style: Whether to use modern styling
        
    Returns:
        str: Path to the generated PDF file
    """
    try:
        # Set defaults if not provided
        if upload_folder is None:
            upload_folder = current_app.config.get('UPLOAD_FOLDER', '/tmp/uploads')
            os.makedirs(upload_folder, exist_ok=True)
            
        if orientation is None:
            orientation = 'portrait'  # Default orientation
            
        if template_name is None:
            template_name = 'pdf/flexible_quotation_template.html'
            
        # Determine which fields to include
        field_dict = {field['name']: field for field in DEFAULT_ITEM_FIELDS + AVAILABLE_ITEM_FIELDS}
        
        # Process selected fields or use defaults
        if selected_fields is None:
            # Use default fields
            fields_to_include = DEFAULT_ITEM_FIELDS
        else:
            # Filter fields based on selection
            fields_to_include = []
            for field_name in selected_fields:
                if field_name in field_dict:
                    field = field_dict[field_name]
                    # Skip admin fields if not requested
                    if not include_admin_fields and field.get('admin_only', False):
                        continue
                    fields_to_include.append(field)
                    
            # Always ensure the position field is included
            if not any(f['name'] == 'position' for f in fields_to_include):
                fields_to_include.insert(0, field_dict['position'])
                
            # Always include quantity and price if total is included
            if any(f['name'] == 'total' for f in fields_to_include):
                if not any(f['name'] == 'quantity' for f in fields_to_include):
                    fields_to_include.append(field_dict['quantity'])
                if not any(f['name'] == 'selling_price' for f in fields_to_include):
                    fields_to_include.append(field_dict['selling_price'])
                    
        # Ensure we have at least description, quantity, and price
        if not fields_to_include:
            fields_to_include = [
                field_dict['position'],
                field_dict['description'],
                field_dict['quantity'],
                field_dict['selling_price'],
                field_dict['total']
            ]
            
        # Calculate VAT and totals
        vat_dict = {}  # Dictionary to track VAT by rate
        subtotal = 0
        
        # Count items to verify data
        item_count = len(quotation.items) if quotation.items else 0
        logger.info(f"Generating flexible PDF for quotation {quotation.quotation_number} with {item_count} items")
        
        # Create a sorted list of items by position
        sorted_items = list(quotation.items)
        sorted_items.sort(key=lambda x: x.position if hasattr(x, 'position') and x.position is not None else 0)
        
        # Process the items
        processed_items = []
        for item in sorted_items:
            # Create a processed item with all required fields
            processed_item = {
                'original': item,  # Keep reference to original
                'id': getattr(item, 'id', None),
                'position': getattr(item, 'position', 0),
            }
            
            # Copy regular fields
            for field in fields_to_include:
                field_name = field['name']
                # Handle calculated fields
                if field.get('calculated', False):
                    if field_name == 'total':
                        value = getattr(item, 'quantity', 0) * getattr(item, 'selling_price', 0)
                    elif field_name == 'margin':
                        selling_price = getattr(item, 'selling_price', 0)
                        cost_price = getattr(item, 'cost_price', 0)
                        value = (selling_price - cost_price) / selling_price * 100 if selling_price > 0 else 0
                    else:
                        value = None
                else:
                    # Get the value directly from the item
                    value = getattr(item, field_name, None)
                    
                processed_item[field_name] = value
                
            # Add the processed item to our list
            processed_items.append(processed_item)
            
            # Calculate financials
            item_subtotal = getattr(item, 'quantity', 0) * getattr(item, 'selling_price', 0)
            subtotal += item_subtotal
            
            # Track VAT amounts by rate
            vat_rate = getattr(item, 'vat_rate', 0)
            vat_amount = item_subtotal * (vat_rate / 100)
            
            if vat_rate in vat_dict:
                vat_dict[vat_rate] += vat_amount
            else:
                vat_dict[vat_rate] = vat_amount
            
        # Convert to list for template and sort by rate
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
        
        # Clean any HTML entities in the company name
        if company.name:
            company.name = unescape(company.name)
            
        # Generate HTML content from the template
        html_content = render_template(
            template_name,
            quotation=quotation,
            customer=quotation.customer,
            items=processed_items,
            fields=fields_to_include,
            subtotal=subtotal,
            vat_list=vat_list,
            grand_total=grand_total,
            currency=quotation.currency,
            date_generated=datetime.now().strftime('%Y-%m-%d %H:%M'),
            company=company,
            logo_data=logo_data,
            orientation=orientation,
            debug=debug,
            modern_style=use_modern_style
        )
        
        # Save the HTML for inspection if in debug mode
        if debug:
            debug_html_path = os.path.join(upload_folder, f"debug_flexible_{quotation.quotation_number}.html")
            with open(debug_html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"Debug HTML saved to: {debug_html_path}")
        
        # Generate a unique filename
        prefix = "debug_" if debug else ""
        style_type = "modern_" if use_modern_style else "classic_"
        filename = f"{prefix}{style_type}quotation_{quotation.quotation_number}_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(upload_folder, filename)
        
        # Prepare CSS to handle pagination and layout
        css_string = """
        @page { 
            margin: 1.5cm;
            @top-center {
                content: normal; /* Avoid header entity issues */
            }
        }
        
        /* Critical fixes for table layout and pagination */
        table.quotation-items { 
            width: 100% !important;
            table-layout: fixed !important;
            page-break-inside: auto !important;
            border-collapse: collapse !important;
            margin-bottom: 1.5cm;
        }
        
        /* Force header rows to repeat on each page */
        table.quotation-items thead { 
            display: table-header-group !important; 
        }
        
        /* Force table body to break between rows */
        table.quotation-items tbody { 
            display: table-row-group !important;
        }
        
        /* Keep rows together */
        table.quotation-items tr { 
            page-break-inside: avoid !important; 
            break-inside: avoid !important;
            visibility: visible !important;
            display: table-row !important;
            height: auto !important;
        }
        
        /* Cell handling for better text wrapping */
        table.quotation-items td, 
        table.quotation-items th { 
            word-break: break-word !important;
            overflow-wrap: break-word !important;
            overflow: visible !important;
            height: auto !important;
        }
        
        /* Keep summary section together */
        .summary-block { 
            page-break-inside: avoid !important;
            break-inside: avoid !important;
        }
        
        /* Keep terms section together */
        .terms { 
            page-break-inside: avoid !important;
            break-inside: avoid !important;
        }
        
        /* Ensure footer stays at the bottom */
        .footer {
            margin-top: 2cm;
            page-break-inside: avoid !important;
        }
        """
        
        # Add debugging styles if needed
        if debug:
            css_string += """
            /* Debug borders and colors */
            table.quotation-items { border: 3px solid blue !important; }
            table.quotation-items tr { border: 2px solid red !important; }
            table.quotation-items td, 
            table.quotation-items th { border: 1px solid green !important; }
            
            /* Highlight specific rows */
            table.quotation-items tr:nth-child(10),
            table.quotation-items tr:nth-child(14) {
                background-color: yellow !important;
                border: 3px solid red !important;
            }
            """
        
        # Generate PDF with our CSS
        HTML(string=html_content).write_pdf(
            output_path,
            stylesheets=[CSS(string=css_string)]
        )
        
        # Validation: Log that all items were included
        expected_item_count = len(quotation.items)
        logger.info(f"PDF validation: Expected {expected_item_count} items, processed {len(processed_items)} items")
        if expected_item_count != len(processed_items):
            logger.warning(f"Item count mismatch! Expected {expected_item_count} but processed {len(processed_items)}")
        
        logger.info(f"Flexible PDF successfully generated: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error generating flexible quotation PDF: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise