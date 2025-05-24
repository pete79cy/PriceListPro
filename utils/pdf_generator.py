"""
PDF Generator for delivery notes, charge sheets and other documents
Uses WeasyPrint to generate PDFs from HTML templates
"""
import os
import base64
from datetime import datetime
from flask import render_template, current_app
from weasyprint import HTML, CSS
import logging

def generate_delivery_note_pdf(order, language='en'):
    """
    Generate a PDF delivery note for an order
    
    Args:
        order: The order object to generate the delivery note for
        language (str): Language code for translations ('en', 'el', 'ar')
        
    Returns:
        bytes: The PDF file as bytes
    """
    # Get translations for the specified language
    from utils.translations import get_translations
    translations = get_translations(language)
    
    # Render the HTML template with order details and translations
    html = render_template('pdfs/delivery_note.html',
                          order=order,
                          translations=translations,
                          language=language,
                          date=datetime.now().strftime('%Y-%m-%d'))
    
    # Generate PDF using WeasyPrint
    pdf = HTML(string=html).write_pdf()
    return pdf

def generate_charge_sheet_pdf(order):
    """
    Generate a PDF initial charge sheet for an order
    
    Args:
        order: The order object to generate the charge sheet for
        
    Returns:
        bytes: The PDF file as bytes
    """
    # Calculate financial totals for the template
    subtotal = 0
    vat_dict = {}
    
    # Calculate subtotal and VAT by rate
    for item in order.items:
        item_total = item.get_total()
        subtotal += item_total
        
        # Track VAT amounts by rate
        vat_rate = item.vat_rate
        vat_amount = item_total * (vat_rate / 100)
        
        if vat_rate in vat_dict:
            vat_dict[vat_rate] += vat_amount
        else:
            vat_dict[vat_rate] = vat_amount
    
    # Convert to list for template sorting
    vat_breakdown = [{'rate': rate, 'amount': amount} for rate, amount in vat_dict.items()]
    vat_breakdown.sort(key=lambda x: x['rate'])
    
    # Calculate grand total
    total = subtotal + sum(item['amount'] for item in vat_breakdown)
    
    # Render the HTML template with order details
    html = render_template('pdfs/charge_sheet_new.html',
                          order=order,
                          subtotal=subtotal,
                          vat_breakdown=vat_breakdown,
                          total=total,
                          date=datetime.now().strftime('%Y-%m-%d'))
    
    # Generate PDF using WeasyPrint
    pdf = HTML(string=html).write_pdf()
    return pdf

# For backward compatibility
def generate_delivery_note(order, language='en'):
    """Alias for generate_delivery_note_pdf for backward compatibility"""
    return generate_delivery_note_pdf(order, language)

def generate_quotation_pdf(quotation, items=None):
    """
    Generate a PDF for a quotation
    
    Args:
        quotation: The quotation object
        items: Optional list of quotation items (if not provided, will use quotation.items)
        
    Returns:
        bytes: The PDF file as bytes
    """
    # Basic implementation - this would be expanded with actual HTML rendering
    html = render_template('pdfs/quotation.html', 
                          quotation=quotation,
                          items=items or quotation.items)
    pdf = HTML(string=html).write_pdf()
    return pdf

def generate_supplier_pdf_report(quotation, supplier_name, upload_folder):
    """
    Generate a PDF report for a specific supplier from a quotation
    
    Args:
        quotation: The quotation object
        supplier_name: Name of the supplier
        upload_folder: Directory to save the PDF
        
    Returns:
        str: Path to the generated PDF file
    """
    # Get items for this supplier from the quotation
    supplier_items = [item for item in quotation.items if item.supplier == supplier_name]
    
    if not supplier_items:
        return None
    
    # Create a simple supplier object with the name
    supplier = {'name': supplier_name}
    
    # Generate the report title
    title = f"Supplier Report for {supplier_name} - Quotation {quotation.quotation_number}"
    
    # Render the template
    html = render_template('pdfs/supplier_report.html',
                          supplier=supplier,
                          items=supplier_items,
                          title=title)
    
    # Generate PDF
    pdf = HTML(string=html).write_pdf()
    
    # Save to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"supplier_{supplier_name}_{quotation.quotation_number}_{timestamp}.pdf"
    pdf_path = os.path.join(upload_folder, filename)
    
    with open(pdf_path, 'wb') as f:
        f.write(pdf)
    
    return pdf_path

def generate_supplier_products_pdf(supplier, products=None):
    """
    Generate a PDF of products for a supplier
    
    Args:
        supplier: The supplier object
        products: Optional list of products
        
    Returns:
        bytes: The PDF file as bytes
    """
    # Basic implementation
    html = render_template('pdfs/supplier_products.html',
                          supplier=supplier,
                          products=products or supplier.products)
    pdf = HTML(string=html).write_pdf()
    return pdf

def generate_supplier_catalog_pdf(supplier, categories=None):
    """
    Generate a product catalog PDF for a supplier
    
    Args:
        supplier: The supplier object
        categories: Optional list of product categories
        
    Returns:
        bytes: The PDF file as bytes
    """
    # Basic implementation
    html = render_template('pdfs/supplier_catalog.html',
                          supplier=supplier,
                          categories=categories)
    pdf = HTML(string=html).write_pdf()
    return pdf

def generate_custom_supplier_report(supplier_data, items_data, report_params=None):
    """
    Generate a custom supplier report PDF
    
    Args:
        supplier_data: Dictionary containing supplier information
        items_data: List of items/products for the supplier
        report_params: Optional dictionary with report parameters
        
    Returns:
        bytes: The PDF file as bytes
    """
    # Set default report parameters
    if report_params is None:
        report_params = {}
    
    # Generate report title
    title = report_params.get('title', f"Custom Supplier Report - {supplier_data.get('name', 'Unknown Supplier')}")
    
    # Render the HTML template
    html = render_template('pdfs/custom_supplier_report.html',
                          supplier=supplier_data,
                          items=items_data,
                          title=title,
                          report_params=report_params,
                          date=datetime.now().strftime('%Y-%m-%d'))
    
    # Generate PDF using WeasyPrint
    pdf = HTML(string=html).write_pdf()
    return pdf

def generate_delivery_note_report(quotation, items, include_header=True, notes=None):
    """
    Generate a delivery note report PDF with Quantity, Description, and Actual Size fields
    
    Args:
        quotation: The quotation object
        items: List of quotation items to include
        include_header: Whether to include quotation header information
        notes: Optional notes to include in the report
        
    Returns:
        bytes: The PDF file as bytes
    """
    # Generate report title
    title = f"Delivery Note - {quotation.quotation_number}"
    
    # Render the HTML template
    html = render_template('pdfs/delivery_note_report.html',
                          quotation=quotation,
                          items=items,
                          title=title,
                          include_header=include_header,
                          notes=notes,
                          date=datetime.now().strftime('%Y-%m-%d'))
    
    # Generate PDF using WeasyPrint
    pdf = HTML(string=html).write_pdf()
    return pdf

def get_logo_data(company):
    """
    Get company logo data in base64 format for PDF documents
    
    Args:
        company: The company settings object with logo_path
        
    Returns:
        str: Base64 encoded logo data or empty string if no logo
    """
    if not company or not company.logo_path:
        return ""
        
    try:
        logo_path = company.logo_path
        if logo_path and not os.path.isabs(logo_path):
            # If relative path, make it absolute
            static_folder = current_app.static_folder if current_app and hasattr(current_app, 'static_folder') else 'static'
            logo_path = os.path.join(str(static_folder), str(logo_path))
            
        if logo_path and os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                logo_data = f.read()
            # Encode to base64 for inline HTML display
            encoded_logo = base64.b64encode(logo_data).decode('utf-8')
            # Determine MIME type based on file extension
            extension = os.path.splitext(logo_path)[1].lower() if logo_path else '.png'
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
        # Log the error but don't crash PDF generation because of a logo issue
        if hasattr(current_app, 'logger'):
            current_app.logger.error(f"Error loading company logo: {str(e)}")
        else:
            print(f"Error loading company logo: {str(e)}")
    
    # Return empty string if any issues occur
    return ""