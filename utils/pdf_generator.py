import os
import uuid
import base64
from datetime import datetime
from flask import render_template, current_app
from weasyprint import HTML
from utils.logger import logger
from models import CompanySettings

def get_logo_data(company):
    """
    Get logo data as base64 string for PDF reports
    
    Args:
        company: CompanySettings object with logo path
        
    Returns:
        str: base64 encoded logo data with mime type
    """
    logo_data = None
    
    # First try to use company logo if available
    if company and company.logo_path and os.path.exists(company.logo_path):
        try:
            with open(company.logo_path, "rb") as logo_file:
                encoded_logo = base64.b64encode(logo_file.read()).decode('utf-8')
                file_ext = os.path.splitext(company.logo_path)[1].strip('.').lower()
                if not file_ext:
                    file_ext = 'png'  # Default to PNG if no extension
                logo_data = f"data:image/{file_ext};base64,{encoded_logo}"
            logger.info(f"Using company logo from {company.logo_path}")
        except Exception as e:
            logger.error(f"Error reading company logo: {str(e)}. Will try using default logo.")
    
    # If no company logo or error reading it, use the static logo
    if not logo_data:
        try:
            static_logo_path = os.path.join(current_app.root_path, 'static', 'images', 'pakkoutis_logo_300x100.png')
            if os.path.exists(static_logo_path):
                with open(static_logo_path, "rb") as logo_file:
                    encoded_logo = base64.b64encode(logo_file.read()).decode('utf-8')
                    logo_data = f"data:image/png;base64,{encoded_logo}"
                logger.info(f"Using static Pakkoutis logo from {static_logo_path}")
            else:
                logger.warning(f"Static logo not found at {static_logo_path}")
        except Exception as e:
            logger.error(f"Error reading static logo: {str(e)}")
    
    return logo_data

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
        
        # Get logo data using the helper function (will use static logo if company logo is not available)
        logo_data = get_logo_data(company)
        
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

def generate_supplier_pdf_report(quotation, supplier, upload_folder):
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
        
        # Get logo data using the helper function (will use static logo if company logo is not available)
        logo_data = get_logo_data(company)
        
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
            order_date=quotation.quotation_date,  # Use quotation date as order date
            reference_number=quotation.quotation_number,  # Use quotation number as reference
            subtotal=total_cost,  # Pass the calculated total cost as subtotal
            grand_total=total_cost,  # Without VAT, grand total equals subtotal
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

def generate_supplier_products_pdf(products, fields=None, group_by_supplier=True, include_header=True):
    """
    Generate a customized PDF report for selected supplier products
    
    Args:
        products: List of SupplierProduct objects
        fields: List of field names to include in the report (optional)
        group_by_supplier: Whether to group products by supplier (optional)
        include_header: Whether to include company header (optional)
        
    Returns:
        tuple: (PDF content as bytes, filename)
    """
    try:
        # Set default fields if not provided
        if fields is None:
            fields = ["product_name", "scientific_name", "height", "pot_size", "price", "cost_price", "supplier", "last_updated"]
        
        # Always ensure product_name is included as it's required
        if "product_name" not in fields:
            fields.insert(0, "product_name")
        
        # Get company settings if header should be included
        company = None
        logo_data = None
        
        if include_header:
            company = CompanySettings.query.first()
            if not company:
                company = CompanySettings()  # Use default values if no settings exist
            
            # Get logo data using the helper function (will use static logo if company logo is not available)
            logo_data = get_logo_data(company)
        
        # Set the orientation based on company settings or default to landscape for reports
        orientation = company.pdf_orientation if company else "landscape"
        
        suppliers_list = None
        
        # Group products by supplier if requested
        if group_by_supplier:
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
            
            suppliers_count = len(suppliers_list)
        else:
            # Just sort products by name without grouping
            products.sort(key=lambda x: x.product_name)
            suppliers_count = 0
        
        # Generate HTML content from the template
        html_content = render_template(
            'pdf/supplier_products_template.html',
            suppliers=suppliers_list,
            products=products if not group_by_supplier else None,
            products_count=len(products),
            suppliers_count=suppliers_count,
            fields=fields,
            group_by_supplier=group_by_supplier,
            include_header=include_header,
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
        
        # Get logo data using the helper function (will use static logo if company logo is not available)
        logo_data = get_logo_data(company)
        
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
        
def generate_custom_supplier_report(quotation, selected_suppliers, selected_fields, include_prices=True, 
                                   include_company_header=True, include_terms=True, group_by_supplier=True):
    """
    Generate a custom PDF report for selected suppliers from a quotation
    
    Args:
        quotation: The Quotation object
        selected_suppliers: List of supplier names to include in the report
        selected_fields: List of field names to include in the report
        include_prices: Whether to include price information
        include_company_header: Whether to include company header
        include_terms: Whether to include terms and conditions
        group_by_supplier: Whether to group items by supplier
        
    Returns:
        tuple: (PDF content as bytes, filename)
    """
    try:
        # Get company settings if header should be included
        company = None
        logo_data = None
        
        if include_company_header:
            company = CompanySettings.query.first()
            if not company:
                company = CompanySettings()  # Use default values if no settings exist
            
            # Get logo data using the helper function (will use static logo if company logo is not available)
            logo_data = get_logo_data(company)
        
        # Set the orientation based on company settings or default to landscape for reports
        orientation = company.pdf_orientation if company else "landscape"
        
        # Group items by supplier
        grouped_items = {}
        supplier_totals = {}
        
        for item in quotation.items:
            # Only include items from selected suppliers
            if item.supplier in selected_suppliers:
                if item.supplier not in grouped_items:
                    grouped_items[item.supplier] = []
                    supplier_totals[item.supplier] = {
                        'qty': 0,
                        'cost': 0
                    }
                
                grouped_items[item.supplier].append(item)
                
                # Calculate totals
                supplier_totals[item.supplier]['qty'] += item.quantity
                
                # Debug logging to trace cost_price values
                logger.debug(f"Item: {item.id}, Description: {item.description}, Cost Price: {item.cost_price}")
                
                # Make sure we correctly handle the cost_price field (could be None)
                cost_price = 0
                if hasattr(item, 'cost_price') and item.cost_price is not None:
                    cost_price = float(item.cost_price)
                
                supplier_totals[item.supplier]['cost'] += item.quantity * cost_price
        
        # Generate HTML content from the template
        html_content = render_template(
            'pdf/custom_supplier_report_template.html',
            quotation=quotation,
            grouped_items=grouped_items,
            supplier_totals=supplier_totals,
            selected_fields=selected_fields,
            include_prices=include_prices,
            include_company_header=include_company_header,
            include_terms=include_terms,
            group_by_supplier=group_by_supplier,
            currency=quotation.currency,
            date_generated=datetime.now().strftime('%Y-%m-%d %H:%M'),
            company=company,
            logo_data=logo_data,
            orientation=orientation
        )
        
        # Generate a unique filename
        filename = f"supplier_report_{quotation.quotation_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Generate PDF from HTML
        pdf_content = HTML(string=html_content).write_pdf()
        
        return pdf_content, filename
    
    except Exception as e:
        logger.error(f"Error generating custom supplier report PDF: {str(e)}")
        raise