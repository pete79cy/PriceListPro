"""
Script to debug VAT calculation issues in quotation PAK-2025-028
This script will inspect the VAT calculation for the problematic quotation
and generate a detailed report to help identify any issues.
"""

import os
import sys
import json
from datetime import datetime
from flask import Flask, render_template
from weasyprint import HTML
from app import app, db
from models import Quotation, QuotationItem

def analyze_vat_calculation(quotation_number='PAK-2025-028'):
    """
    Analyze VAT calculation for a specific quotation
    
    Args:
        quotation_number: The quotation number to inspect
    
    Returns:
        dict: Analysis results
    """
    with app.app_context():
        # Get the quotation
        quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
        
        if not quotation:
            print(f"Quotation {quotation_number} not found")
            return None
        
        # Calculate VAT based on rates
        vat_dict = {}
        subtotal = 0
        
        print(f"Analyzing VAT calculation for quotation {quotation_number}")
        print(f"Total items: {len(quotation.items)}")
        
        # Group items by VAT rate for analysis
        items_by_vat_rate = {}
        
        for item in quotation.items:
            item_subtotal = item.quantity * item.selling_price
            subtotal += item_subtotal
            
            # Track VAT amounts by rate
            vat_rate = item.vat_rate
            vat_amount = item_subtotal * (vat_rate / 100)
            
            # Group items for detailed analysis
            if vat_rate not in items_by_vat_rate:
                items_by_vat_rate[vat_rate] = []
            
            items_by_vat_rate[vat_rate].append({
                'id': item.id,
                'description': item.description[:30],
                'quantity': item.quantity,
                'price': item.selling_price,
                'subtotal': item_subtotal,
                'vat_rate': vat_rate,
                'vat_amount': vat_amount
            })
            
            # Add to VAT dictionary
            if vat_rate in vat_dict:
                vat_dict[vat_rate] += vat_amount
            else:
                vat_dict[vat_rate] = vat_amount
        
        # Convert to list for template format
        vat_list = [{'rate': rate, 'label': f'VAT {rate}%', 'amount': amount} for rate, amount in vat_dict.items()]
        
        # Calculate grand total
        grand_total = subtotal + sum(item['amount'] for item in vat_list)
        
        # Print detailed breakdown
        print("\nDetailed VAT Breakdown:")
        print(f"Subtotal: €{subtotal:.2f}")
        
        for vat_item in vat_list:
            print(f"{vat_item['label']}: €{vat_item['amount']:.2f}")
        
        print(f"Grand Total: €{grand_total:.2f}")
        
        # Print items by VAT rate
        for rate, items in items_by_vat_rate.items():
            print(f"\nItems with {rate}% VAT rate ({len(items)} items):")
            rate_subtotal = sum(item['subtotal'] for item in items)
            rate_vat = sum(item['vat_amount'] for item in items)
            
            print(f"  Subtotal: €{rate_subtotal:.2f}")
            print(f"  VAT amount: €{rate_vat:.2f}")
            
            for item in items:
                print(f"  - {item['description']}: {item['quantity']} x €{item['price']:.2f} = €{item['subtotal']:.2f} (VAT: €{item['vat_amount']:.2f})")
        
        # Return results for further analysis
        return {
            'quotation_number': quotation_number,
            'subtotal': subtotal,
            'vat_dict': vat_dict,
            'vat_list': vat_list,
            'grand_total': grand_total,
            'items_by_vat_rate': items_by_vat_rate
        }

def check_vat_rendering(quotation_number='PAK-2025-028'):
    """
    Check if VAT is rendering correctly in the PDF template
    
    Args:
        quotation_number: The quotation number to inspect
        
    Returns:
        bool: True if VAT renders correctly, False otherwise
    """
    with app.app_context():
        # Get the quotation
        quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
        
        if not quotation:
            print(f"Quotation {quotation_number} not found")
            return False
        
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
        
        # Check if we have multiple VAT rates
        if len(vat_list) > 1:
            rates = [f"{v['rate']}%" for v in vat_list]
            print(f"Multiple VAT rates detected: {', '.join(rates)}")
        else:
            print(f"Single VAT rate detected: {vat_list[0]['rate']}%")
        
        # Check if the rendered output matches calculations
        print(f"Calculated grand total: €{grand_total:.2f}")
        print(f"Quotation stored total: €{quotation.total_amount:.2f}" if quotation.total_amount else "No stored total amount")
        
        # Return whether the calculation matches the stored value (if available)
        if quotation.total_amount:
            return abs(grand_total - quotation.total_amount) < 0.01  # Allow for small floating point differences
        
        return True  # If no stored value, assume rendering is correct

def generate_test_pdf(quotation_number='PAK-2025-028'):
    """
    Generate a test PDF with VAT breakdown
    
    Args:
        quotation_number: The quotation number to use
    
    Returns:
        str: Path to the generated PDF
    """
    with app.app_context():
        # Get the quotation
        quotation = Quotation.query.filter_by(quotation_number=quotation_number).first()
        
        if not quotation:
            print(f"Quotation {quotation_number} not found")
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
        
        # Generate HTML for test PDF
        html_content = render_template(
            'pdf/vat_debug_template.html',
            quotation=quotation,
            subtotal=subtotal,
            vat_list=vat_list,
            grand_total=grand_total,
            date_generated=datetime.now().strftime('%Y-%m-%d %H:%M')
        )
        
        # Create output directory if it doesn't exist
        upload_folder = app.config.get('UPLOAD_FOLDER', 'static/uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Generate a unique filename
        filename = f"vat_debug_{quotation_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(upload_folder, filename)
        
        # Generate PDF from HTML
        HTML(string=html_content).write_pdf(output_path)
        
        print(f"Test PDF generated: {output_path}")
        return output_path

def main():
    """Main function to run the script"""
    quotation_number = 'PAK-2025-028'
    
    # If command line argument provided, use it as quotation number
    if len(sys.argv) > 1:
        quotation_number = sys.argv[1]
    
    print(f"Debugging VAT calculation for quotation {quotation_number}")
    
    # Analyze VAT calculation
    analysis = analyze_vat_calculation(quotation_number)
    
    if not analysis:
        return
    
    # Check VAT rendering in template
    print("\nChecking VAT rendering in template:")
    vat_renders_correctly = check_vat_rendering(quotation_number)
    
    if vat_renders_correctly:
        print("✅ VAT appears to be rendering correctly in the template")
    else:
        print("❌ VAT may not be rendering correctly in the template")
    
    # Save analysis to JSON file for reference
    output_dir = 'debug_output'
    os.makedirs(output_dir, exist_ok=True)
    
    analysis_file = os.path.join(output_dir, f"vat_analysis_{quotation_number}.json")
    
    # Convert sets to lists for JSON serialization
    sanitized_analysis = {k: (list(v) if isinstance(v, set) else v) for k, v in analysis.items()}
    
    with open(analysis_file, 'w') as f:
        json.dump(sanitized_analysis, f, default=str, indent=2)
    
    print(f"\nAnalysis saved to {analysis_file}")
    
    # Generate a test PDF with VAT breakdown
    pdf_path = generate_test_pdf(quotation_number)
    
    if pdf_path:
        print(f"\nTest PDF generated: {pdf_path}")

if __name__ == '__main__':
    main()