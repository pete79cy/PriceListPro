import os
import uuid
from datetime import datetime
from flask import render_template
from weasyprint import HTML
from utils.logger import logger

def generate_quotation_pdf(quotation, upload_folder):
    """
    Generate a PDF quotation from a Quotation object
    
    Args:
        quotation: The Quotation object
        upload_folder: The directory where to save the PDF
        
    Returns:
        str: Path to the generated PDF file
    """
    try:
        # Calculate VAT based on rates
        vat_dict = {}  # Dictionary to track VAT by rate
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
        vat_list = [{'rate': rate, 'amount': amount} for rate, amount in vat_dict.items()]
        
        # Calculate grand total
        grand_total = subtotal + sum(item['amount'] for item in vat_list)
        
        # Generate HTML content from the template
        html_content = render_template(
            'pdf/quotation_template.html',
            quotation=quotation,
            customer=quotation.customer,
            items=quotation.items,
            subtotal=subtotal,
            vat_list=vat_list,
            grand_total=grand_total,
            currency=quotation.currency,
            date_generated=datetime.now().strftime('%Y-%m-%d %H:%M')
        )
        
        # Generate a unique filename
        filename = f"quotation_{quotation.quotation_number}_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(upload_folder, filename)
        
        # Generate PDF from HTML
        HTML(string=html_content).write_pdf(output_path)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error generating quotation PDF: {str(e)}")
        raise

def generate_supplier_report(quotation, supplier, upload_folder):
    """
    Generate a PDF supplier report from a Quotation object
    
    Args:
        quotation: The Quotation object
        supplier: The supplier name
        upload_folder: The directory where to save the PDF
        
    Returns:
        str: Path to the generated PDF file, or None if no items for supplier
    """
    try:
        # Filter items by the supplier
        items = [item for item in quotation.items if item.supplier == supplier]
        
        if not items:
            logger.warning(f"No items found for supplier '{supplier}' in quotation {quotation.quotation_number}")
            return None
        
        # Calculate total cost
        total_cost = sum(item.quantity * (item.cost_price or 0) for item in items)
        
        # Generate HTML content from the template
        html_content = render_template(
            'pdf/supplier_report_template.html',
            supplier=supplier,
            quotation=quotation,
            customer=quotation.customer,
            items=items,
            total_cost=total_cost,
            currency=quotation.currency,
            date_generated=datetime.now().strftime('%Y-%m-%d %H:%M')
        )
        
        # Generate a unique filename
        supplier_filename = supplier.replace(' ', '_').replace('/', '_').replace('\\', '_')
        filename = f"supplier_{supplier_filename}_{quotation.quotation_number}_{uuid.uuid4().hex[:8]}.pdf"
        output_path = os.path.join(upload_folder, filename)
        
        # Generate PDF from HTML
        HTML(string=html_content).write_pdf(output_path)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error generating supplier report PDF: {str(e)}")
        raise