import os
import uuid
import base64
import io
import re
from datetime import datetime, timedelta
from flask import render_template, current_app
from weasyprint import HTML
from fpdf import FPDF
from utils.logger import logger
from models import CompanySettings

def sanitize_text_for_latin1(text):
    """
    Sanitize text to ensure it's compatible with latin-1 encoding
    
    Args:
        text: Text to sanitize
        
    Returns:
        str: Sanitized text compatible with latin-1 encoding
    """
    if text is None:
        return ""
        
    # Replace common problematic characters
    text = str(text)
    text = text.replace('€', 'EUR')
    text = text.replace('£', 'GBP')
    text = text.replace('©', '(c)')
    text = text.replace('®', '(R)')
    text = text.replace('™', '(TM)')
    text = text.replace('…', '...')
    
    # Replace any other characters outside of latin-1 range with closest ASCII equivalent
    result = ""
    for char in text:
        try:
            char.encode('latin-1')
            result += char
        except UnicodeEncodeError:
            # If can't encode to latin-1, replace with '?'
            result += '?'
    
    return result

class PDF(FPDF):
    """Custom PDF class with header, footer and watermark capabilities"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store company settings object
        self.company = None  # Will be set later to a CompanySettings instance
        
    # Type hint accessor methods for company property
    def set_company(self, company_settings):
        """Set the company settings object safely"""
        self.company = company_settings
    
    def header(self):
        if self.company:
            self.set_font("Helvetica", 'B', 12)
            self.cell(0, 10, self.company.name, ln=True)
            self.set_font("Helvetica", '', 10)
            self.cell(0, 5, self.company.address_line1 or '', ln=True)
            self.cell(0, 5, self.company.email or '', ln=True)
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f"Page {self.page_no()} / {{nb}}", align='C')

    def add_watermark(self, text):
        self.set_font("Helvetica", 'B', 40)
        self.set_text_color(240, 240, 240)
        self.rotate(45, x=self.w / 3, y=self.h / 2)
        self.text(self.w / 3, self.h / 2, text)
        self.rotate(0)

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
        


def generate_custom_supplier_report(quotation, selected_suppliers, selected_fields,
                                    include_prices=True, include_company_header=True,
                                    include_terms=True, group_by_supplier=True,
                                    notes=None):
    """
    Generate a custom PDF report for selected suppliers from a quotation using FPDF
    
    Args:
        quotation: The Quotation object
        selected_suppliers: List of supplier names to include in the report
        selected_fields: List of field names to include in the report
        include_prices: Whether to include price information
        include_company_header: Whether to include company header
        include_terms: Whether to include terms and conditions
        group_by_supplier: Whether to group items by supplier
        notes: Optional notes to include in the report
        
    Returns:
        tuple: (PDF content as bytes, filename)
    """
    try:
        pdf = PDF()
        pdf.alias_nb_pages()
        pdf.add_page()

        # Company settings
        company = None
        if include_company_header:
            company = CompanySettings.query.first()
            if not company:
                company = CompanySettings()  # Use default values if no settings exist
            pdf.set_company(company)
        
        # Cover page content
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(0, 10, f"Quotation Report: {quotation.quotation_number}", ln=True)
        pdf.set_font("Helvetica", '', 12)
        pdf.cell(0, 10, f"Date Issued: {quotation.quotation_date.strftime('%Y-%m-%d')}", ln=True)
        
        # Valid until date (30 days from quotation date if not specified)
        valid_until = quotation.quotation_date + timedelta(days=30)
        pdf.cell(0, 10, f"Valid Until: {valid_until.strftime('%Y-%m-%d')}", ln=True)
        
        # Handle potential non-latin1 characters in customer name
        customer_name = quotation.customer.name if quotation.customer else 'N/A'
        # Sanitize customer name for latin-1 encoding
        customer_name = sanitize_text_for_latin1(customer_name)
        
        pdf.cell(0, 10, f"Customer: {customer_name}", ln=True)
        # Join suppliers but ensure they don't contain non-latin1 characters
        safe_suppliers = [sanitize_text_for_latin1(s) for s in selected_suppliers]
        pdf.cell(0, 10, f"Suppliers Included: {', '.join(safe_suppliers)}", ln=True)
        pdf.ln(10)

        # Add watermark
        pdf.add_watermark("CONFIDENTIAL")

        # Group items by supplier if needed
        grouped_items = {}
        
        for item in quotation.items:
            # Only include items from selected suppliers
            if item.supplier in selected_suppliers:
                if item.supplier not in grouped_items:
                    grouped_items[item.supplier] = []
                
                grouped_items[item.supplier].append(item)

        # Process by supplier
        for supplier_name in selected_suppliers:
            items = grouped_items.get(supplier_name, [])
            if not items:
                continue

            pdf.set_font("Helvetica", 'B', 14)
            pdf.set_text_color(0)
            pdf.cell(0, 10, f"Supplier: {supplier_name}", ln=True)
            pdf.set_font("Helvetica", 'B', 10)

            # Table headers
            headers = ["Item", "Qty"]
            if include_prices:
                headers.extend(["Unit Price", "Total"])
            
            # Add other selected fields from selected_fields
            for field in selected_fields:
                if field not in ['description', 'quantity', 'selling_price', 'total']:
                    headers.append(field.replace('_', ' ').title())
            
            # Calculate column width based on page width and number of columns
            col_width = pdf.w / len(headers)
            
            # Print headers
            for header in headers:
                pdf.cell(col_width, 8, header, border=1)
            pdf.ln()

            # Table rows
            pdf.set_font("Helvetica", '', 10)
            total = 0
            fill = False
            
            for item in items:
                pdf.set_fill_color(245 if fill else 255)
                
                # Item description - Safely handle special characters
                safe_description = sanitize_text_for_latin1(item.description[:30])
                pdf.cell(col_width, 8, safe_description, border=1, fill=fill)
                
                # Quantity
                pdf.cell(col_width, 8, str(item.quantity), border=1, fill=fill)
                
                # Price columns if included
                if include_prices:
                    # Use a standard currency symbol that's compatible with latin-1 encoding
                    currency_symbol = "$" if quotation.currency == "€" else quotation.currency
                    pdf.cell(col_width, 8, f"{currency_symbol}{item.selling_price:.2f}", border=1, fill=fill)
                    line_total = item.selling_price * item.quantity
                    total += line_total
                    pdf.cell(col_width, 8, f"{currency_symbol}{line_total:.2f}", border=1, fill=fill)
                
                # Additional fields
                for field in selected_fields:
                    if field not in ['description', 'quantity', 'selling_price', 'total']:
                        value = getattr(item, field, '')
                        if value is not None:
                            # Sanitize the value for latin-1 encoding
                            safe_value = sanitize_text_for_latin1(str(value)[:20])
                            pdf.cell(col_width, 8, safe_value, border=1, fill=fill)
                        else:
                            pdf.cell(col_width, 8, '', border=1, fill=fill)
                
                pdf.ln()
                fill = not fill

            # Supplier subtotal
            if include_prices:
                pdf.set_font("Helvetica", 'B', 10)
                pdf.cell(col_width * 3, 8, "Subtotal", border=1)
                # Use a standard currency symbol that's compatible with latin-1 encoding
                currency_symbol = "$" if quotation.currency == "€" else quotation.currency
                pdf.cell(col_width, 8, f"{currency_symbol}{total:.2f}", border=1)
                pdf.ln(15)

        # Notes section
        if notes:
            pdf.add_page()
            pdf.set_font("Helvetica", 'I', 10)
            pdf.set_text_color(50)
            # Sanitize notes for latin-1 encoding
            safe_notes = sanitize_text_for_latin1(notes)
            pdf.multi_cell(0, 10, f"Notes: {safe_notes}", border=1)
            pdf.ln()

        # Terms and Conditions
        if include_terms and company:
            pdf.add_page()
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 10, "Terms and Conditions", ln=True)
            pdf.set_font("Helvetica", '', 10)
            terms_text = "Standard terms apply. All prices are subject to change."
            if hasattr(company, 'terms') and company.terms:
                terms_text = company.terms
            # Sanitize terms for latin-1 encoding
            safe_terms = sanitize_text_for_latin1(terms_text)
            pdf.multi_cell(0, 6, safe_terms)
            pdf.ln()

        # Final output - get PDF as string and convert to bytes
        pdf_output = io.BytesIO()
        # Get PDF as string (dest='S') and convert to bytes with latin1 encoding
        pdf_str = pdf.output(dest='S')
        if isinstance(pdf_str, str):
            pdf_bytes = pdf_str.encode('latin1')  # For older FPDF versions
        else:
            pdf_bytes = pdf_str  # For newer FPDF versions
            
        pdf_output.write(pdf_bytes)
        pdf_output.seek(0)
        
        # Generate a unique filename
        filename = f"supplier_report_{quotation.quotation_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return pdf_output.read(), filename
    
    except Exception as e:
        logger.error(f"Error generating custom supplier report PDF: {str(e)}")
        raise