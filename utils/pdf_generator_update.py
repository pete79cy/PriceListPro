"""
Updated PDF generator functions with improved layout and presentation
"""
from fpdf import FPDF
from flask import current_app
from datetime import datetime, timedelta
import os
import io
from models import CompanySettings
from utils.logger import logger

def safe_encode(text):
    """
    Safely encode text for PDF compatibility with Unicode support.
    
    Args:
        text: The text to encode
        
    Returns:
        str: The encoded text
    """
    if not text:
        return ""
    
    # Just return the text as is, since we're using Unicode fonts
    # Only convert to string in case it's not already a string
    return str(text)

def draw_supplier_section(pdf, supplier_name, items, include_prices, base_font="DejaVu", currency="€", selected_fields=None):
    """
    Draw a supplier section with items in the PDF
    
    Args:
        pdf: FPDF instance
        supplier_name: Name of the supplier
        items: List of items for this supplier
        include_prices: Whether to include price information
        base_font: Font to use
        currency: Currency symbol
        selected_fields: List of selected fields to include
        
    Returns:
        float: Subtotal for this supplier
    """
    pdf.set_font(base_font, 'B', 11)
    pdf.set_text_color(40)
    pdf.cell(0, 10, f"Supplier: {supplier_name}", ln=True)
    pdf.set_draw_color(180)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    # Define headers and column widths
    headers = ["Item", "Height", "Qty"]
    if include_prices:
        headers += [f"Cost Price ({currency})", f"Total ({currency})"]
    col_widths = [50, 35, 15, 30, 30] if include_prices else [60, 45, 25]

    # Header row
    pdf.set_font(base_font, 'B', 9)
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1, align='C')
    pdf.ln()

    # Data rows
    pdf.set_font(base_font, '', 9)
    fill = False
    subtotal = 0
    
    for item in items:
        # Calculate line total
        line_total = (item.cost_price or 0) * (item.quantity or 0)
        subtotal += line_total
        
        # Prepare row data
        row = [
            item.description or item.product_name or '',
            item.height or '',
            str(item.quantity or 0)
        ]
        
        # Add prices if included
        if include_prices:
            row += [
                f"{currency}{item.cost_price:.2f}" if item.cost_price else f"{currency}0.00",
                f"{currency}{line_total:.2f}"
            ]
        
        # Draw cells with alternating fill
        for i, text in enumerate(row):
            pdf.set_fill_color(245 if fill else 255)
            pdf.cell(col_widths[i], 8, safe_encode(text), border=1, fill=True)
        
        fill = not fill
        pdf.ln()
    
    # Add subtotal row if prices are included
    if include_prices:
        pdf.set_font(base_font, 'B', 9)
        pdf.cell(sum(col_widths[:-1]), 8, "Subtotal", border=1, align='R')
        pdf.cell(col_widths[-1], 8, f"{currency}{subtotal:.2f}", border=1, align='R')
        pdf.ln(12)
    
    return subtotal

def generate_custom_supplier_report_with_ubuntu(quotation, selected_suppliers, selected_fields,
                                include_prices=True, include_company_header=True,
                                include_terms=True, group_by_supplier=True,
                                notes=None):
    """
    Generate a custom PDF report for selected suppliers from a quotation using FPDF with Ubuntu font
    
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
        pdf = FPDF()
        pdf.alias_nb_pages()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Font registration - we're using Ubuntu font but keeping DejaVu as the font name for compatibility
        print("Registering fonts...")
        # Use absolute paths
        base_dir = os.getcwd()
        font_path = os.path.join(base_dir, 'static/fonts/DejaVuSans.ttf')
        font_bold_path = os.path.join(base_dir, 'static/fonts/DejaVuSans-Bold.ttf')
        font_italic_path = os.path.join(base_dir, 'static/fonts/DejaVuSans-Italic.ttf')
        
        print(f"Font path: {font_path}, exists: {os.path.exists(font_path)}")
        print(f"Font bold path: {font_bold_path}, exists: {os.path.exists(font_bold_path)}")
        print(f"Font italic path: {font_italic_path}, exists: {os.path.exists(font_italic_path)}")
        
        pdf.add_font("DejaVu", "", font_path, uni=True)
        if os.path.exists(font_bold_path):
            pdf.add_font("DejaVu", "B", font_bold_path, uni=True)
        if os.path.exists(font_italic_path):
            pdf.add_font("DejaVu", "I", font_italic_path, uni=True)
        
        pdf.set_font("DejaVu", '', 10)

        # Load company details
        company = None
        if include_company_header:
            company = CompanySettings.query.first()
            
            # Add company header
            pdf.set_font("DejaVu", 'B', 11)
            pdf.cell(0, 6, safe_encode(company.name if company else ""), ln=True)
            pdf.set_font("DejaVu", '', 9)
            if company:
                address = safe_encode(company.address_line1 or "")
                if hasattr(company, 'address_line2') and company.address_line2:
                    address += f", {safe_encode(company.address_line2)}"
                pdf.cell(0, 5, address, ln=True)
                pdf.cell(0, 5, safe_encode(company.email or ""), ln=True)
            pdf.ln(3)

        # Header summary
        pdf.set_font("DejaVu", 'B', 14)
        pdf.cell(0, 10, safe_encode(f"Quotation Report: {quotation.quotation_number}"), ln=True)
        pdf.set_font("DejaVu", '', 10)
        pdf.cell(0, 6, f"Date Issued: {quotation.quotation_date.strftime('%Y-%m-%d')}", ln=True)
        
        # Valid until date - add 30 days from quotation date if valid_until not present
        valid_until = quotation.quotation_date + timedelta(days=30)
        pdf.cell(0, 6, f"Valid Until: {valid_until.strftime('%Y-%m-%d')}", ln=True)
        
        # Customer information
        if hasattr(quotation, 'customer') and quotation.customer:
            pdf.cell(0, 6, safe_encode(f"Customer: {quotation.customer.name}"), ln=True)
        
        # Suppliers included
        pdf.multi_cell(0, 6, safe_encode(f"Suppliers Included: {', '.join(selected_suppliers)}"))
        pdf.ln(6)

        # Process each supplier
        grand_total = 0
        currency = quotation.currency if hasattr(quotation, 'currency') and quotation.currency else '€'
        
        for supplier in selected_suppliers:
            # Get items for this supplier
            items = [i for i in quotation.items if i.supplier == supplier]
            if not items:
                continue
                
            # Draw supplier section
            subtotal = draw_supplier_section(pdf, supplier, items, include_prices, "DejaVu", currency, selected_fields)
            grand_total += subtotal

        # Notes section
        if notes:
            pdf.set_font("DejaVu", 'I', 9)
            pdf.set_text_color(90)
            pdf.multi_cell(0, 6, safe_encode(f"Notes: {notes}"))
            pdf.ln(4)

        # Grand total
        if include_prices:
            pdf.set_font("DejaVu", 'B', 11)
            pdf.set_text_color(0)
            pdf.cell(0, 8, f"Grand Total: {currency}{grand_total:.2f}", ln=True)
            pdf.ln(5)

        # Terms section
        if include_terms and company:
            pdf.add_page()
            pdf.set_font("DejaVu", 'B', 12)
            pdf.cell(0, 10, "Terms and Conditions", ln=True)
            pdf.set_font("DejaVu", '', 10)
            pdf.set_text_color(0)
            
            # Get terms from company settings or use default
            terms_text = "Standard terms and conditions apply."
            if hasattr(company, 'terms') and company.terms:
                terms_text = company.terms
                
            pdf.multi_cell(0, 6, safe_encode(terms_text))

        # Generate PDF
        # Get output as bytes directly - try with different encodings if needed
        try:
            print("Generating PDF output...")
            pdf_bytes = pdf.output(dest='S').encode('latin1')
            print(f"Successfully generated PDF of size {len(pdf_bytes)} bytes")
        except Exception as e:
            print(f"Error with Latin-1 encoding: {str(e)}")
            # Try without encoding - fpdf2 may handle it differently
            try:
                pdf_bytes = pdf.output(dest='S')
                if isinstance(pdf_bytes, bytes):
                    print(f"Alternative method generated PDF of size {len(pdf_bytes)} bytes")
                else:
                    print(f"Output is not bytes but {type(pdf_bytes)}")
                    # Convert string to bytes if needed
                    if isinstance(pdf_bytes, str):
                        pdf_bytes = pdf_bytes.encode('utf-8')
            except Exception as inner_e:
                print(f"Error with alternative method: {str(inner_e)}")
                raise
        
        # Create a timestamped filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_ubuntu_report_{timestamp}.pdf"
        
        # Also save directly to a file for testing
        with open(filename, "wb") as f:
            f.write(pdf_bytes)
        print(f"PDF directly saved to {filename} with size {os.path.getsize(filename)} bytes")
        
        return pdf_bytes, filename

    except Exception as e:
        logger.error(f"Error generating custom supplier report: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise