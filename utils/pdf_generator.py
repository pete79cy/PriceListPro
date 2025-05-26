"""
PDF Generator for delivery notes, charge sheets and other documents
Uses WeasyPrint to generate PDFs from HTML templates and ReportLab for enhanced designs
"""
import os
import base64
from datetime import datetime
from flask import render_template, current_app
from weasyprint import HTML, CSS
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import qrcode
import io
import logging

def generate_delivery_note_pdf(order, language='en', base_url=None):
    """
    Generate a PDF delivery note for an order with enhanced design and QR code
    
    Args:
        order: The order object to generate the delivery note for
        language (str): Language code for translations ('en', 'el', 'ar')
        base_url (str): Base URL for QR code generation
        
    Returns:
        bytes: The PDF file as bytes
    """
    # Get translations for the specified language
    from utils.translations import get_translations
    translations = get_translations(language)
    
    # QR code functionality removed
    qr_code_data = None
    
    # Render the HTML template with order details and translations
    html = render_template('pdfs/delivery_note.html',
                          order=order,
                          translations=translations,
                          language=language,
                          qr_code_data=qr_code_data,
                          date=datetime.now().strftime('%Y-%m-%d'))
    
    # Generate PDF using WeasyPrint
    pdf = HTML(string=html).write_pdf()
    return pdf

def generate_pro_forma_invoice_pdf(order):
    """
    Generate a PDF Pro Forma Invoice for an order
    
    Args:
        order: The order object to generate the Pro Forma Invoice for
        
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
    
    # QR code functionality removed
    qr_code_base64 = ""
    
    # Render the HTML template with order details
    html = render_template('pdfs/pro_forma_invoice.html',
                          order=order,
                          subtotal=subtotal,
                          vat_breakdown=vat_breakdown,
                          total=total,
                          qr_code_base64=qr_code_base64,
                          page_number=1,
                          total_pages=1,
                          date=datetime.now().strftime('%Y-%m-%d'))
    
    # Generate PDF using WeasyPrint
    pdf = HTML(string=html).write_pdf()
    return pdf

# For backward compatibility
def generate_charge_sheet_pdf(order):
    """Backward compatibility wrapper - redirects to Pro Forma Invoice"""
    return generate_pro_forma_invoice_pdf(order)
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


def generate_enhanced_delivery_note_pdf(quotation, base_url=None):
    """
    Generate an enhanced delivery note PDF using ReportLab with QR codes and status badges
    
    Args:
        quotation: The quotation object to generate the delivery note for
        base_url: Base URL for QR code generation
        
    Returns:
        bytes: The PDF file as bytes
    """
    # Register Unicode font for Greek characters
    try:
        # Try to register DejaVu Sans font for proper Greek character support
        pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
        font_name = 'DejaVuSans'
    except:
        try:
            # Fallback to Liberation Sans if available
            pdfmetrics.registerFont(TTFont('LiberationSans', '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'))
            font_name = 'LiberationSans'
        except:
            # If no Unicode fonts available, use Helvetica but clean the text
            font_name = 'Helvetica'
    
    # Create a BytesIO buffer to store the PDF
    buffer = io.BytesIO()
    
    # Create the PDF canvas
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 20 * mm

    # Header
    try:
        c.setFont(f"{font_name}-Bold", 18)
    except:
        c.setFont(font_name, 18)
    c.drawString(margin, height - 40, f"Delivery Note – {quotation.quotation_number}")

    # Status Badge (based on quotation status if available)
    status_text = "ACCEPTED"
    status_color = colors.green
    if hasattr(quotation, 'status'):
        if quotation.status == 'draft':
            status_text = "DRAFT"
            status_color = colors.orange
        elif quotation.status == 'sent':
            status_text = "SENT"
            status_color = colors.blue
        elif quotation.status == 'accepted':
            status_text = "ACCEPTED"
            status_color = colors.green
        elif quotation.status == 'rejected':
            status_text = "REJECTED"
            status_color = colors.red
    
    # Draw status badge
    c.setFillColor(status_color)
    c.roundRect(width - 100, height - 50, 80, 20, 5, fill=1)
    c.setFillColor(colors.white)
    try:
        c.setFont(f"{font_name}-Bold", 10)
    except:
        c.setFont(font_name, 10)
    c.drawCentredString(width - 60, height - 45, status_text)
    c.setFillColor(colors.black)

    # QR code functionality removed for enhanced delivery notes

    # Sub-header with date and customer
    c.setFont(font_name, 12)
    c.drawString(margin, height - 60, f"Date: {quotation.quotation_date}")
    if quotation.customer:
        c.drawString(margin, height - 75, f"Customer: {quotation.customer.name}")

    # Table Headers
    headers = ["#", "Quantity", "Description", "Pot Size"]
    header_x = [margin, margin + 30, margin + 80, margin + 280]
    header_y = height - 100
    
    try:
        c.setFont(f"{font_name}-Bold", 10)
    except:
        c.setFont(font_name, 10)
    for i, header in enumerate(headers):
        c.drawString(header_x[i], header_y, header)
    
    # Draw header line
    c.line(margin, header_y - 5, width - margin, header_y - 5)

    # Table Data
    y = header_y - 20
    item_count = 0
    total_quantity = 0
    
    # Sort items by position to maintain order
    sorted_items = sorted(quotation.items, key=lambda x: x.position if x.position is not None else 0)
    
    for item in sorted_items:
        item_count += 1
        total_quantity += item.quantity
        
        # Check if we need a new page
        if y < 100:  # Leave space for footer
            c.showPage()
            y = height - 50
            
            # Redraw headers on new page
            c.setFont("Helvetica-Bold", 10)
            for i, header in enumerate(headers):
                c.drawString(header_x[i], y, header)
            c.line(margin, y - 5, width - margin, y - 5)
            y -= 20
        
        # Draw row data with Unicode font for Greek characters
        c.setFont(font_name, 9)
        
        # Get clean description (no need to remove characters with Unicode font)
        description = item.description or ""
        
        row_data = [
            str(item_count),
            str(int(item.quantity)) if item.quantity == int(item.quantity) else str(item.quantity),
            description[:40] + "..." if len(description) > 40 else description,
            item.pot_size or "N/A"
        ]
        
        for i, cell in enumerate(row_data):
            c.drawString(header_x[i], y, str(cell))
        
        y -= 20

    # Summary section
    y -= 20
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, f"Total distinct SKUs: {item_count}")
    c.drawString(margin + 150, y, f"Total units: {int(total_quantity)}")

    # Footer with signatures
    signature_y = 80
    c.setFont("Helvetica", 10)
    c.drawString(margin, signature_y, "Delivered By:")
    c.line(margin, signature_y - 15, margin + 200, signature_y - 15)
    c.drawString(margin, signature_y - 25, "Name: ________________")
    c.drawString(margin, signature_y - 40, "Date: ________________")
    
    c.drawString(margin + 250, signature_y, "Received By:")
    c.line(margin + 250, signature_y - 15, width - margin, signature_y - 15)
    c.drawString(margin + 250, signature_y - 25, "Name: ________________")
    c.drawString(margin + 250, signature_y - 40, "Date: ________________")

    # Save the PDF
    c.save()
    
    # Get the PDF bytes
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes