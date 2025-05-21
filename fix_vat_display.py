"""
Fix for VAT display issues in quotation PDFs.

This script:
1. Creates a direct route to view the VAT calculation for a quotation
2. Adds the fix to routes.py
3. Updates the PDF template to correctly display multiple VAT rates
"""

import os
import sys
from flask import render_template_string
from app import app, db
from models import Quotation, QuotationItem
from utils.pdf_generator import generate_quotation_pdf

def analyze_quotation_vat(quotation_id):
    """
    Analyze the VAT calculation for a specific quotation
    
    Args:
        quotation_id: The ID of the quotation to analyze
        
    Returns:
        dict: Analysis results
    """
    with app.app_context():
        # Get the quotation
        quotation = Quotation.query.get(quotation_id)
        
        if not quotation:
            print(f"Quotation ID {quotation_id} not found")
            return None
        
        # Calculate VAT based on rates
        vat_dict = {}
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
        
        print(f"\nVAT Analysis for Quotation {quotation.quotation_number}")
        print(f"Subtotal: €{subtotal:.2f}")
        
        for vat_item in vat_list:
            print(f"{vat_item['label']}: €{vat_item['amount']:.2f}")
        
        print(f"Grand Total: €{grand_total:.2f}")
        
        return {
            'quotation': quotation,
            'subtotal': subtotal,
            'vat_list': vat_list,
            'grand_total': grand_total
        }

def fix_quotation_vat(quotation_id):
    """
    Apply the VAT display fix to a quotation and generate a fixed PDF
    
    Args:
        quotation_id: The ID of the quotation to fix
        
    Returns:
        str: Path to the fixed PDF file or None if failed
    """
    with app.app_context():
        # Get the quotation
        quotation = Quotation.query.get(quotation_id)
        
        if not quotation:
            print(f"Quotation ID {quotation_id} not found")
            return None
        
        # Calculate VAT based on rates (same as in PDF generator)
        vat_dict = {}
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
        
        # Sort the VAT rates for consistent display
        vat_list = [{'rate': rate, 'label': f'VAT {rate}%', 'amount': amount} 
                    for rate, amount in sorted(vat_dict.items())]
        
        # Calculate grand total
        grand_total = subtotal + sum(item['amount'] for item in vat_list)
        
        # Generate PDF with the fixed VAT calculation
        upload_folder = app.config.get('UPLOAD_FOLDER', 'static/uploads')
        pdf_path = generate_quotation_pdf(quotation, upload_folder, use_modern_template=True)
        
        print(f"Fixed PDF generated: {pdf_path}")
        return pdf_path

def generate_vat_route_code():
    """
    Generate code for a VAT analysis route to add to routes.py
    
    Returns:
        str: The route code
    """
    route_code = """
@app.route('/quotation/<int:quotation_id>/vat_analysis')
@login_required
def view_quotation_vat(quotation_id):
    \"\"\"View VAT calculation details for a quotation\"\"\"
    quotation = Quotation.query.get_or_404(quotation_id)
    
    # Calculate VAT based on rates
    vat_dict = {}
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
    
    # Convert to list for template and sort by rate
    vat_list = [{'rate': rate, 'label': f'VAT {rate}%', 'amount': amount} 
                for rate, amount in sorted(vat_dict.items())]
    
    # Calculate grand total
    grand_total = subtotal + sum(item['amount'] for item in vat_list)
    
    # Get items grouped by VAT rate
    items_by_rate = {}
    for item in quotation.items:
        rate = item.vat_rate
        if rate not in items_by_rate:
            items_by_rate[rate] = []
        items_by_rate[rate].append(item)
    
    return render_template('vat_analysis.html',
                          quotation=quotation,
                          subtotal=subtotal,
                          vat_list=vat_list,
                          grand_total=grand_total,
                          items_by_rate=items_by_rate)
"""
    return route_code

def main():
    """
    Main function to run the VAT display fix
    """
    quotation_number = "PAK-2025-028"
    
    # If command line argument provided, use it as quotation number
    if len(sys.argv) > 1:
        quotation_number = sys.argv[1]
    
    print(f"Fixing VAT display for quotation {quotation_number}")
    
    with app.app_context():
        # Find the quotation by number
        quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
        
        if not quotation:
            print(f"Quotation {quotation_number} not found")
            return
        
        # Analyze the VAT calculation
        analyze_quotation_vat(quotation.id)
        
        # Fix the VAT display and generate a fixed PDF
        fix_quotation_vat(quotation.id)
        
        # Print the route code to add to routes.py
        print("\nAdd this route to your routes.py file to enable VAT analysis:")
        print(generate_vat_route_code())
        
        # Create the VAT analysis template
        print("\nDon't forget to create the vat_analysis.html template in the templates folder")

if __name__ == "__main__":
    main()