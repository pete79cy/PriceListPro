import os
import uuid
import base64
from datetime import datetime
from flask import render_template
from weasyprint import HTML
from utils.logger import logger
from models import CompanySettings

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
        
        # Get company settings
        company = CompanySettings.query.first()
        if not company:
            company = CompanySettings()  # Use default values if no settings exist
        
        # Prepare logo data if available
        logo_data = None
        if company.logo_path and os.path.exists(company.logo_path):
            with open(company.logo_path, "rb") as logo_file:
                encoded_logo = base64.b64encode(logo_file.read()).decode('utf-8')
                file_ext = os.path.splitext(company.logo_path)[1].strip('.')
                logo_data = f"data:image/{file_ext};base64,{encoded_logo}"
        
        # Set the orientation based on company settings
        orientation = company.pdf_orientation  # 'portrait' or 'landscape'
        
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
            date_generated=datetime.now().strftime('%Y-%m-%d %H:%M'),
            company=company,
            logo_data=logo_data,
            orientation=orientation
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
        
        # Get company settings
        company = CompanySettings.query.first()
        if not company:
            company = CompanySettings()  # Use default values if no settings exist
        
        # Prepare logo data if available
        logo_data = None
        if company.logo_path and os.path.exists(company.logo_path):
            with open(company.logo_path, "rb") as logo_file:
                encoded_logo = base64.b64encode(logo_file.read()).decode('utf-8')
                file_ext = os.path.splitext(company.logo_path)[1].strip('.')
                logo_data = f"data:image/{file_ext};base64,{encoded_logo}"
        
        # Set the orientation based on company settings
        orientation = company.pdf_orientation  # 'portrait' or 'landscape'
        
        # Generate HTML content from the template
        html_content = render_template(
            'pdf/supplier_report_template.html',
            supplier=supplier,
            quotation=quotation,
            customer=quotation.customer,
            items=items,
            total_cost=total_cost,
            currency=quotation.currency,
            date_generated=datetime.now().strftime('%Y-%m-%d %H:%M'),
            company=company,
            logo_data=logo_data,
            orientation=orientation
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

def generate_supplier_products_pdf(products):
    """
    Generate a PDF report for selected supplier products
    
    Args:
        products: List of SupplierProduct objects
        
    Returns:
        tuple: (PDF content as bytes, filename)
    """
    try:
        # Get company settings
        company = CompanySettings.query.first()
        if not company:
            company = CompanySettings()  # Use default values if no settings exist
        
        # Prepare logo data if available
        logo_data = None
        if company.logo_path and os.path.exists(company.logo_path):
            with open(company.logo_path, "rb") as logo_file:
                encoded_logo = base64.b64encode(logo_file.read()).decode('utf-8')
                file_ext = os.path.splitext(company.logo_path)[1].strip('.')
                logo_data = f"data:image/{file_ext};base64,{encoded_logo}"
        
        # Set the orientation based on company settings
        orientation = company.pdf_orientation  # 'portrait' or 'landscape'
        
        # Group products by supplier for better organization
        suppliers_dict = {}
        for product in products:
            if product.supplier_id not in suppliers_dict:
                suppliers_dict[product.supplier_id] = {
                    'supplier': product.supplier,
                    'products': []
                }
            suppliers_dict[product.supplier_id]['products'].append(product)
        
        # Sort suppliers and products
        suppliers_list = sorted(suppliers_dict.values(), key=lambda x: x['supplier'].name)
        for supplier in suppliers_list:
            supplier['products'].sort(key=lambda x: x.product_name)
        
        # Generate HTML content from the template
        html_content = render_template(
            'pdf/supplier_products_template.html',
            suppliers=suppliers_list,
            products_count=len(products),
            suppliers_count=len(suppliers_list),
            date_generated=datetime.now().strftime('%Y-%m-%d %H:%M'),
            company=company,
            logo_data=logo_data,
            orientation=orientation
        )
        
        # Generate a unique filename
        filename = f"supplier_products_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Generate PDF from HTML
        pdf_content = HTML(string=html_content).write_pdf()
        
        return pdf_content, filename
    
    except Exception as e:
        logger.error(f"Error generating supplier products PDF: {str(e)}")
        raise

def generate_supplier_catalog_pdf(supplier, products):
    """
    Generate a PDF catalog for all products from a specific supplier
    
    Args:
        supplier: Supplier object
        products: List of SupplierProduct objects from this supplier
        
    Returns:
        tuple: (PDF content as bytes, filename)
    """
    try:
        # Get company settings
        company = CompanySettings.query.first()
        if not company:
            company = CompanySettings()  # Use default values if no settings exist
        
        # Prepare logo data if available
        logo_data = None
        if company.logo_path and os.path.exists(company.logo_path):
            with open(company.logo_path, "rb") as logo_file:
                encoded_logo = base64.b64encode(logo_file.read()).decode('utf-8')
                file_ext = os.path.splitext(company.logo_path)[1].strip('.')
                logo_data = f"data:image/{file_ext};base64,{encoded_logo}"
        
        # Set the orientation based on company settings
        orientation = company.pdf_orientation  # 'portrait' or 'landscape'
        
        # Group products by categories (using scientific name for grouping)
        categories = {}
        for product in products:
            category = product.scientific_name or "Uncategorized"
            if category not in categories:
                categories[category] = []
            categories[category].append(product)
        
        # Sort categories and products
        sorted_categories = {}
        for category in sorted(categories.keys()):
            sorted_categories[category] = sorted(categories[category], key=lambda x: x.product_name)
        
        # Generate HTML content from the template
        html_content = render_template(
            'pdf/supplier_catalog_template.html',
            supplier=supplier,
            categories=sorted_categories,
            products_count=len(products),
            categories_count=len(sorted_categories),
            date_generated=datetime.now().strftime('%Y-%m-%d %H:%M'),
            company=company,
            logo_data=logo_data,
            orientation=orientation
        )
        
        # Generate a unique filename
        supplier_name = supplier.name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        filename = f"supplier_catalog_{supplier_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        # Generate PDF from HTML
        pdf_content = HTML(string=html_content).write_pdf()
        
        return pdf_content, filename
    
    except Exception as e:
        logger.error(f"Error generating supplier catalog PDF: {str(e)}")
        raise