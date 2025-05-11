"""
Test script to demonstrate the WeasyPrint PDF pagination fix with SimpleNamespace.

This script:
1. Creates a sample quotation with items
2. Generates a paginated PDF using SimpleNamespace
3. Outputs the PDF to a test directory

Usage:
    python test_fixed_pagination.py
"""

import os
import sys
from types import SimpleNamespace
from datetime import datetime
from flask import Flask, render_template
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

# Create a simple Flask app for template rendering
app = Flask(__name__)

def create_sample_items(count=15):
    """Create a sample list of items for testing"""
    items = []
    for i in range(1, count+1):
        items.append({
            'id': i,
            'description': f'Test plant item #{i}',
            'scientific_name': f'Testus plantus {i}',
            'pot_size': f'{10 + i}cm',
            'height': f'{50 + i*5}cm',
            'quantity': i,
            'selling_price': 10 + i*2,
            'position': i-1
        })
    return items

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

def generate_test_pdf():
    """Generate a test PDF with the fixed pagination approach"""
    # Create sample items
    items = create_sample_items(15)
    
    # Apply pagination
    paginated_items = adjust_table_rows_for_pagination(items)
    
    # Print info about pagination for verification
    print(f"Number of pages: {len(paginated_items)}")
    for i, page in enumerate(paginated_items, 1):
        print(f"  Page {i}: {len(page.items)} items")
        
    # Setup sample data for rendering
    context = {
        'paginated_items': paginated_items,
        'items': items,  # Include the full list for reference
        'orientation': 'portrait',
        'date_generated': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'debug': True,
        'debug_styles': "<style>table { border: 2px solid red !important; }</style>" if True else None,
        'customer': {'name': 'Test Customer', 'address': '123 Test Street', 'phone': '555-123-4567'},
        'quotation': {
            'quotation_number': 'TEST-2025-001',
            'quotation_date': datetime.now(),
            'currency': '€',
            'notes': 'This is a test quotation with pagination'
        },
        'subtotal': sum(item['quantity'] * item['selling_price'] for item in items),
        'vat_list': [{'rate': 19, 'label': 'VAT 19%', 'amount': sum(item['quantity'] * item['selling_price'] * 0.19 for item in items)}],
        'grand_total': sum(item['quantity'] * item['selling_price'] * 1.19 for item in items),
        'company': {
            'name': 'Test Company',
            'address_line1': '456 Company Street',
            'address_line2': 'Test City',
            'phone': '555-987-6543',
            'pdf_orientation': 'portrait'
        },
        'logo_data': None,
        'total_pages': len(paginated_items)
    }
    
    with app.app_context():
        # Render the HTML template with the test data
        html_content = render_template('pdf/modern_quotation_template_paginated.html', **context)
        
        # Create output directory
        output_dir = 'test_output'
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the HTML for inspection
        html_path = os.path.join(output_dir, 'test_paginated.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML saved to: {html_path}")
        
        # Define enhanced CSS for pagination
        css_string = """
        @page { 
            margin: 1.5cm;
            margin-bottom: 30mm; /* Increased margin for footer space */
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
        
        /* Debug styles */
        .page-break {
            border: 4px dashed purple !important;
            margin: 10mm 0 !important;
            padding: 5mm !important;
            background-color: lightyellow !important;
        }
        """
        
        # Initialize font configuration
        font_config = FontConfiguration()
        
        try:
            # Generate PDF with enhanced configuration
            pdf_path = os.path.join(output_dir, 'test_paginated.pdf')
            HTML(string=html_content).write_pdf(
                pdf_path,
                stylesheets=[CSS(string=css_string, font_config=font_config)],
                font_config=font_config
            )
            print(f"PDF generated successfully: {pdf_path}")
            
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False
            
        return True

if __name__ == '__main__':
    success = generate_test_pdf()
    sys.exit(0 if success else 1)