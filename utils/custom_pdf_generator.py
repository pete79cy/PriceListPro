import os
from datetime import datetime
import weasyprint
from flask import render_template, url_for
from app import app
from models import Quotation, CompanySettings
from utils.logger import logger

def generate_custom_pdf(quotation, fields=None):
    """
    Generate a PDF for a quotation with customized fields.
    
    Args:
        quotation: The Quotation object to generate PDF for
        fields: List of field names to include in the PDF (if None, all fields are included)
        
    Returns:
        str: Path to the generated PDF file, or None if failed
    """
    try:
        # Default fields if none provided
        if not fields:
            fields = [
                'customer_name', 'quotation_number', 'quotation_date',
                'product_name', 'product_quantity', 'product_price', 'product_total',
                'subtotal', 'vat', 'total',
                'company_name', 'company_address', 'company_phone', 'company_email'
            ]
        
        # Get company settings
        company_settings = CompanySettings.query.first()
        if not company_settings:
            company_settings = CompanySettings()  # Use defaults
        
        # Create a dictionary to hold field visibility
        field_visibility = {}
        for field in fields:
            field_visibility[field] = field in fields
        
        # Define which item fields to show
        item_fields = {
            'product_name': 'product_name' in fields,
            'product_scientific_name': 'product_scientific_name' in fields, 
            'product_pot_size': 'product_pot_size' in fields,
            'product_height': 'product_height' in fields,
            'product_quantity': 'product_quantity' in fields,
            'product_price': 'product_price' in fields,
            'product_total': 'product_total' in fields
        }
        
        # Count the number of visible item columns for layout purposes
        visible_column_count = sum(1 for value in item_fields.values() if value)
        
        # Calculate VAT and totals in Python with precise decimal arithmetic
        from decimal import Decimal, ROUND_HALF_UP
        
        vat_dict = {}
        subtotal = Decimal('0.00')
        
        for item in quotation.items:
            # Use Decimal for precise calculations
            item_subtotal = Decimal(str(item.quantity)) * Decimal(str(item.selling_price))
            subtotal += item_subtotal
            
            # Track VAT amounts by rate with precise calculation
            vat_rate = Decimal(str(item.vat_rate))
            vat_amount = (item_subtotal * vat_rate / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            if vat_rate in vat_dict:
                vat_dict[vat_rate] += vat_amount
            else:
                vat_dict[vat_rate] = vat_amount
        
        # Convert to list for template with proper rounding
        vat_list = [{'rate': float(rate), 'amount': float(amount)} for rate, amount in vat_dict.items()]
        vat_list.sort(key=lambda x: x['rate'])  # Sort by rate
        
        # Calculate grand total with precise arithmetic
        total_vat = sum(vat_dict.values(), Decimal('0.00'))
        grand_total = subtotal + total_vat
        
        # Convert to float for template rendering
        subtotal = float(subtotal)
        grand_total = float(grand_total)
        
        # Generate HTML from template
        with app.app_context():
            html = render_template(
                'pdf/custom_quotation_template.html',
                quotation=quotation,
                customer=quotation.customer,
                company=company_settings,
                fields=field_visibility,
                item_fields=item_fields,
                visible_column_count=visible_column_count,
                calculated_subtotal=subtotal,
                vat_breakdown=vat_list,
                calculated_grand_total=grand_total,
                timestamp=datetime.now().strftime('%Y%m%d_%H%M%S')
            )
        
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.getcwd(), 'static', 'pdf')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate PDF filename
        filename = f"quotation_{quotation.quotation_number.replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(output_dir, filename)
        
        # Convert HTML to PDF
        pdf_bytes = weasyprint.HTML(string=html).write_pdf()
        
        # Save PDF to file
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        # Update quotation with file path
        quotation.file_path = os.path.join('pdf', filename)
        
        # Log success
        logger.info(f"Custom PDF generated for quotation {quotation.quotation_number}")
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error generating custom PDF for quotation {quotation.quotation_number}: {str(e)}")
        return None