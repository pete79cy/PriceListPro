import os
import io
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
        
def generate_custom_supplier_report_fpdf(quotation, selected_suppliers, selected_fields,
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
        from fpdf import FPDF
        import io
        from datetime import timedelta

        class PDF(FPDF):
            def __init__(self):
                # Initialize with UTF-8 support for Euro symbol (€)
                super().__init__(orientation='P')
                # Set utf8 encoding to handle Euro symbol
                self.set_auto_page_break(auto=True, margin=15)
                
            def header(self):
                if hasattr(self, 'company') and self.company:
                    self.set_font("Helvetica", 'B', 12)
                    self.cell(0, 10, self.company.name, ln=True)
                    self.set_font("Helvetica", '', 10)
                    address = self.company.address_line1
                    if hasattr(self.company, 'address_line2') and self.company.address_line2:
                        address += f", {self.company.address_line2}"
                    self.cell(0, 5, address or '', ln=True)
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
                self.set_text_color(0)

        # Initialize PDF object with UTF-8 support
        pdf = PDF()
        pdf.alias_nb_pages()
        
        # Company settings
        company = None
        if include_company_header:
            company = CompanySettings.query.first()
            if not company:
                company = CompanySettings()  # Use default values if no settings exist
            pdf.company = company
        
        # Add cover page
        pdf.add_page()
        
        # Cover page content
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(0, 10, f"Quotation Report: {quotation.quotation_number}", ln=True)
        pdf.set_font("Helvetica", '', 12)
        
        # Format date
        if hasattr(quotation, 'quotation_date'):
            quote_date = quotation.quotation_date.strftime('%Y-%m-%d') if quotation.quotation_date else 'N/A'
        else:
            quote_date = datetime.now().strftime('%Y-%m-%d')
            
        valid_until = None
        if hasattr(quotation, 'valid_until') and quotation.valid_until:
            valid_until = quotation.valid_until.strftime('%Y-%m-%d')
        else:
            # Default validity: 30 days from quotation date
            if hasattr(quotation, 'quotation_date') and quotation.quotation_date:
                valid_until = (quotation.quotation_date + timedelta(days=30)).strftime('%Y-%m-%d')
            else:
                valid_until = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        pdf.cell(0, 10, f"Date Issued: {quote_date}", ln=True)
        pdf.cell(0, 10, f"Valid Until: {valid_until}", ln=True)
        
        # Customer information
        customer_name = quotation.customer.name if hasattr(quotation, 'customer') and quotation.customer else 'N/A'
        pdf.cell(0, 10, f"Customer: {customer_name}", ln=True)
        pdf.cell(0, 10, f"Suppliers Included: {', '.join(selected_suppliers)}", ln=True)
        pdf.ln(10)

        # Add watermark
        pdf.add_watermark("CONFIDENTIAL")

        # Group items by supplier
        grouped_items = {}
        total_items = 0
        total_quantity = 0
        
        for item in quotation.items:
            supplier_name = item.supplier if hasattr(item, 'supplier') else (
                           item.supplier_name if hasattr(item, 'supplier_name') else 'Unknown')
            
            # Only include items from selected suppliers
            if supplier_name in selected_suppliers:
                if supplier_name not in grouped_items:
                    grouped_items[supplier_name] = []
                grouped_items[supplier_name].append(item)
                total_items += 1
                total_quantity += item.quantity
        
        # Calculate grand total
        grand_total = 0
        
        # Iterate through supplier groups
        for supplier_name, items in grouped_items.items():
            if not items:
                continue

            # Add supplier section header
            pdf.add_page()
            pdf.set_font("Helvetica", 'B', 14)
            pdf.cell(0, 10, f"Supplier: {supplier_name}", ln=True)
            pdf.ln(5)
            
            # Table headers
            pdf.set_font("Helvetica", 'B', 10)
            
            # Start with basic headers
            headers = []
            col_widths = []
            
            # Add custom fields based on selected_fields
            field_mapping = {
                'description': {'title': 'Item', 'width': 100},
                'quantity': {'title': 'Qty', 'width': 20},
                'supplier': {'title': 'Supplier', 'width': 40},
                'unit': {'title': 'Unit', 'width': 20},
                'notes': {'title': 'Notes', 'width': 60},
                'part_number': {'title': 'Part #', 'width': 30},
                'reference': {'title': 'Ref', 'width': 30}
            }
            
            # Always include description and quantity
            if 'description' not in selected_fields:
                selected_fields.insert(0, 'description')
            if 'quantity' not in selected_fields:
                selected_fields.insert(1, 'quantity')
                
            # Build headers from selected fields
            for field in selected_fields:
                if field in field_mapping:
                    headers.append(field_mapping[field]['title'])
                    col_widths.append(field_mapping[field]['width'])
            
            # Add price columns if needed
            if include_prices:
                headers.extend(["Cost Price", "Total Cost"])
                col_widths.extend([30, 30])
            
            # Draw header row
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 8, header, border=1)
            pdf.ln()

            # Table rows
            pdf.set_font("Helvetica", '', 10)
            total = 0
            fill = False
            
            for item in items:
                # Set row background
                pdf.set_fill_color(245 if fill else 255)
                
                # Process each field in order
                field_index = 0
                
                for field in selected_fields:
                    if field not in field_mapping:
                        continue
                    
                    if field == 'description':
                        value = item.description if hasattr(item, 'description') else 'N/A'
                    elif field == 'quantity':
                        value = str(item.quantity) if hasattr(item, 'quantity') else '0'
                    elif field == 'supplier':
                        value = item.supplier if hasattr(item, 'supplier') else 'N/A'
                    elif field == 'unit':
                        value = item.unit if hasattr(item, 'unit') else ''
                    elif field == 'notes':
                        value = item.notes if hasattr(item, 'notes') else ''
                    elif field == 'part_number':
                        value = item.part_number if hasattr(item, 'part_number') else ''
                    elif field == 'reference':
                        value = item.reference if hasattr(item, 'reference') else ''
                    else:
                        value = 'N/A'
                    
                    # Print cell with value
                    pdf.cell(col_widths[field_index], 8, str(value), border=1, fill=fill)
                    field_index += 1
                
                # Get quantity value for calculations
                quantity = item.quantity if hasattr(item, 'quantity') else 0
                
                # Price cells
                if include_prices:
                    # Get price - for supplier reports, we should prioritize cost_price
                    unit_price = 0
                    if hasattr(item, 'cost_price') and item.cost_price is not None:
                        unit_price = item.cost_price
                    elif hasattr(item, 'price'):
                        unit_price = item.price
                    elif hasattr(item, 'selling_price'):
                        unit_price = item.selling_price
                    
                    # Format prices
                    # Handle Euro symbol specifically for encoding compatibility
                    currency = quotation.currency if hasattr(quotation, 'currency') else 'EUR '
                    if currency == '€':
                        currency = 'EUR '  # Replace Euro symbol with text representation
                        
                    # Calculate price cells position (they come after all selected fields)
                    price_pos = len(headers) - 2  # Unit Price column
                    total_pos = len(headers) - 1  # Total column
                    
                    pdf.cell(col_widths[price_pos], 8, f"{currency}{unit_price:.2f}", border=1, fill=fill)
                    
                    # Calculate line total
                    line_total = unit_price * quantity
                    total += line_total
                    grand_total += line_total
                    pdf.cell(col_widths[total_pos], 8, f"{currency}{line_total:.2f}", border=1, fill=fill)
                
                pdf.ln()
                fill = not fill  # Toggle fill for next row

            # Add subtotal row if prices are included
            if include_prices:
                pdf.set_font("Helvetica", 'B', 10)
                
                # Calculate combined width of all field columns except the price columns
                field_width = sum(col_widths[:price_pos])
                
                # Create subtotal row
                pdf.cell(field_width, 8, "Subtotal", border=1)
                
                currency = quotation.currency if hasattr(quotation, 'currency') else 'EUR '
                if currency == '€':
                    currency = 'EUR '  # Replace Euro symbol with text representation
                
                # Add the price columns (unit price + total)
                pdf.cell(col_widths[price_pos] + col_widths[total_pos], 8, f"{currency}{total:.2f}", border=1)
                pdf.ln(15)

        # Add Summary Page
        if include_prices:
            pdf.add_page()
            pdf.set_font("Helvetica", 'B', 14)
            pdf.cell(0, 10, "Supplier Report Summary", ln=True)
            pdf.ln(5)
            
            # Summary data
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 10, f"Quotation: {quotation.quotation_number}", ln=True)
            pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
            pdf.cell(0, 10, f"Total Suppliers: {len(grouped_items)}", ln=True)
            pdf.cell(0, 10, f"Total Items: {total_items}", ln=True)
            pdf.cell(0, 10, f"Total Quantity: {total_quantity}", ln=True)
            pdf.ln(10)
            
            # Cost Summary Table
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 10, "Cost Summary", ln=True)
            pdf.ln(5)
            
            pdf.set_font("Helvetica", 'B', 10)
            headers = ["Supplier", "Items", "Total Cost"]
            col_widths = [80, 30, 40]
            
            # Draw header row
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 8, header, border=1)
            pdf.ln()
            
            # Supplier rows
            pdf.set_font("Helvetica", '', 10)
            fill = False
            
            # Get currency symbol
            currency = quotation.currency if hasattr(quotation, 'currency') else 'EUR '
            if currency == '€':
                currency = 'EUR '  # Replace Euro symbol with text representation
            
            for supplier_name, items in grouped_items.items():
                supplier_cost = 0
                for item in items:
                    # Calculate supplier total based on cost_price
                    unit_price = 0
                    if hasattr(item, 'cost_price') and item.cost_price is not None:
                        unit_price = item.cost_price
                    elif hasattr(item, 'price'):
                        unit_price = item.price
                    elif hasattr(item, 'selling_price'):
                        unit_price = item.selling_price
                    
                    supplier_cost += unit_price * item.quantity
                
                # Set row background
                pdf.set_fill_color(245 if fill else 255)
                
                # Supplier name
                pdf.cell(col_widths[0], 8, supplier_name, border=1, fill=fill)
                
                # Item count
                pdf.cell(col_widths[1], 8, str(len(items)), border=1, fill=fill)
                
                # Supplier total
                pdf.cell(col_widths[2], 8, f"{currency}{supplier_cost:.2f}", border=1, fill=fill)
                
                pdf.ln()
                fill = not fill
            
            # Grand Total
            pdf.set_font("Helvetica", 'B', 10)
            pdf.cell(col_widths[0] + col_widths[1], 8, "Grand Total", border=1)
            pdf.cell(col_widths[2], 8, f"{currency}{grand_total:.2f}", border=1)
            pdf.ln(20)
            
            # Date and signature
            pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
            pdf.ln(15)
            pdf.line(20, pdf.get_y(), 80, pdf.get_y())
            pdf.cell(0, 10, "Authorized Signature", ln=True)
            
        # Notes section
        if notes:
            pdf.add_page()
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 10, "Notes", ln=True)
            pdf.set_font("Helvetica", 'I', 10)
            pdf.set_text_color(50)
            pdf.multi_cell(0, 7, notes, border=1)
            pdf.ln()

        # Terms and Conditions
        if include_terms and company:
            pdf.add_page()
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 10, "Terms and Conditions", ln=True)
            pdf.set_font("Helvetica", '', 10)
            
            # Get terms from company settings if available
            terms_text = "Standard terms apply."
            if hasattr(company, 'terms') and company.terms:
                terms_text = company.terms
                
            pdf.multi_cell(0, 6, terms_text)
            pdf.ln()

        # Create filename with timestamp for uniqueness
        filename = f"supplier_report_{quotation.quotation_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Create a temporary file to save the PDF
        temp_filepath = f"/tmp/{filename}"
        
        # Generate and save the PDF to the temporary file
        pdf.output(temp_filepath)
        
        # Read the file back as bytes
        with open(temp_filepath, 'rb') as f:
            pdf_bytes = f.read()
            
        # Clean up the temporary file
        os.remove(temp_filepath)
        
        return pdf_bytes, filename

    except Exception as e:
        logger.error(f"Error generating custom supplier report with FPDF: {str(e)}")
        raise

def generate_custom_supplier_report(quotation, selected_suppliers, selected_fields, include_prices=True, 
                                   include_company_header=True, include_terms=True, group_by_supplier=True,
                                   notes=None, use_fpdf=False):
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
        notes: Optional notes to include in the report
        use_fpdf: Whether to use FPDF for PDF generation (default: False, uses WeasyPrint)
        
    Returns:
        tuple: (PDF content as bytes, filename)
    """
    if use_fpdf:
        return generate_custom_supplier_report_fpdf(
            quotation, selected_suppliers, selected_fields,
            include_prices, include_company_header, include_terms,
            group_by_supplier, notes
        )
    
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
        total_cost = 0.0  # Initialize total cost
        
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
                
                item_total_cost = item.quantity * cost_price
                supplier_totals[item.supplier]['cost'] += item_total_cost
                total_cost += item_total_cost
        
        # Generate HTML content from the template
        html_content = render_template(
            'pdf/custom_supplier_report_template.html',
            quotation=quotation,
            grouped_items=grouped_items,
            supplier_totals=supplier_totals,
            selected_fields=selected_fields,
            fields=selected_fields,  # Ensure fields is passed for compatibility
            include_prices=include_prices,
            include_company_header=include_company_header,
            include_terms=include_terms,
            group_by_supplier=group_by_supplier,
            currency=quotation.currency,
            date_generated=datetime.now().strftime('%Y-%m-%d %H:%M'),
            company=company,
            logo_data=logo_data,
            orientation=orientation,
            notes=notes,  # Pass notes to template
            total_cost=total_cost,  # Add total_cost variable
            suppliers=selected_suppliers  # Pass suppliers list for rendering
        )
        
        # Generate a unique filename
        filename = f"supplier_report_{quotation.quotation_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Generate PDF from HTML
        pdf_content = HTML(string=html_content).write_pdf()
        
        return pdf_content, filename
    
    except Exception as e:
        logger.error(f"Error generating custom supplier report PDF: {str(e)}")
        raise