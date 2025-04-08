"""
Excel generator for quotations using openpyxl.
This module provides functionality to export quotation data as Excel files.
"""

import os
import uuid
import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from models import CompanySettings

def generate_quotation_excel(quotation, output_folder):
    """
    Generate an Excel file from a quotation.
    
    Args:
        quotation: The Quotation object to export
        output_folder: The folder where the Excel file will be saved
        
    Returns:
        str: The path to the generated Excel file
    """
    # Get company information from CompanySettings
    company = CompanySettings.query.first()
    if not company:
        company = CompanySettings()  # Use default values if no settings exist
    # Create a new workbook and select the active worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = f"Quotation {quotation.quotation_number}"
    
    # Define styles
    header_font = Font(name='Arial', size=12, bold=True)
    regular_font = Font(name='Arial', size=11)
    title_font = Font(name='Arial', size=14, bold=True)
    
    center_align = Alignment(horizontal='center', vertical='center')
    left_align = Alignment(horizontal='left', vertical='center')
    right_align = Alignment(horizontal='right', vertical='center')
    
    header_fill = PatternFill(start_color="DDEBF7", end_color="DDEBF7", fill_type="solid")
    
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Adjust column widths
    ws.column_dimensions['A'].width = 5   # #
    ws.column_dimensions['B'].width = 30  # Description
    ws.column_dimensions['C'].width = 20  # Scientific Name
    ws.column_dimensions['D'].width = 12  # Pot Size
    ws.column_dimensions['E'].width = 12  # Height
    ws.column_dimensions['F'].width = 10  # Quantity
    ws.column_dimensions['G'].width = 12  # Unit Price
    ws.column_dimensions['H'].width = 10  # VAT Rate
    ws.column_dimensions['I'].width = 15  # Supplier
    ws.column_dimensions['J'].width = 15  # Total
    
    # HEADER SECTION
    # Title and quotation number
    ws.merge_cells('A1:J1')
    ws['A1'] = f"QUOTATION #{quotation.quotation_number}"
    ws['A1'].font = title_font
    ws['A1'].alignment = center_align
    
    # Company information
    row = 3
    
    ws.merge_cells(f'A{row}:E{row}')
    ws[f'A{row}'] = "COMPANY INFORMATION"
    ws[f'A{row}'].font = header_font
    ws[f'A{row}'].fill = header_fill
    
    ws.merge_cells(f'F{row}:J{row}')
    ws[f'F{row}'] = "CUSTOMER INFORMATION"
    ws[f'F{row}'].font = header_font
    ws[f'F{row}'].fill = header_fill
    
    row += 1
    
    # Company details
    company_data = [
        ("Company:", company.name or "Your Company Name"),
        ("Address Line 1:", company.address_line1 or "Company Address"),
        ("Address Line 2:", company.address_line2 or ""),
        ("Phone:", company.phone or "Company Phone"),
        ("Email:", company.email or "Company Email")
    ]
    
    # Customer details
    customer_data = [
        ("Customer:", quotation.customer.name if quotation.customer else "N/A"),
        ("Address:", quotation.customer.address if quotation.customer and quotation.customer.address else "N/A"),
        ("Phone:", quotation.customer.phone if quotation.customer and quotation.customer.phone else "N/A"),
        ("Email:", quotation.customer.email if quotation.customer and quotation.customer.email else "N/A"),
        ("Category:", quotation.customer.category.name if quotation.customer and quotation.customer.category else "N/A")
    ]
    
    for i in range(5):
        # Company info
        ws.merge_cells(f'A{row+i}:B{row+i}')
        ws[f'A{row+i}'] = company_data[i][0]
        ws[f'A{row+i}'].font = header_font
        ws[f'A{row+i}'].alignment = left_align
        
        ws.merge_cells(f'C{row+i}:E{row+i}')
        ws[f'C{row+i}'] = company_data[i][1]
        ws[f'C{row+i}'].font = regular_font
        ws[f'C{row+i}'].alignment = left_align
        
        # Customer info
        ws.merge_cells(f'F{row+i}:G{row+i}')
        ws[f'F{row+i}'] = customer_data[i][0]
        ws[f'F{row+i}'].font = header_font
        ws[f'F{row+i}'].alignment = left_align
        
        ws.merge_cells(f'H{row+i}:J{row+i}')
        ws[f'H{row+i}'] = customer_data[i][1]
        ws[f'H{row+i}'].font = regular_font
        ws[f'H{row+i}'].alignment = left_align
    
    row += 6
    
    # Quotation details
    ws.merge_cells(f'A{row}:J{row}')
    ws[f'A{row}'] = "QUOTATION DETAILS"
    ws[f'A{row}'].font = header_font
    ws[f'A{row}'].fill = header_fill
    
    row += 1
    
    # Date and reference
    ws.merge_cells(f'A{row}:B{row}')
    ws[f'A{row}'] = "Date:"
    ws[f'A{row}'].font = header_font
    ws[f'A{row}'].alignment = left_align
    
    ws.merge_cells(f'C{row}:E{row}')
    ws[f'C{row}'] = quotation.quotation_date.strftime("%Y-%m-%d")
    ws[f'C{row}'].font = regular_font
    ws[f'C{row}'].alignment = left_align
    
    ws.merge_cells(f'F{row}:G{row}')
    ws[f'F{row}'] = "Currency:"
    ws[f'F{row}'].font = header_font
    ws[f'F{row}'].alignment = left_align
    
    ws.merge_cells(f'H{row}:J{row}')
    ws[f'H{row}'] = quotation.currency
    ws[f'H{row}'].font = regular_font
    ws[f'H{row}'].alignment = left_align
    
    row += 2
    
    # ITEMS TABLE
    # Table headers
    headers = [
        "#", "Description", "Scientific Name", "Pot Size", "Height",
        "Quantity", f"Unit Price ({quotation.currency})", "VAT Rate (%)", "Supplier", f"Total ({quotation.currency})"
    ]
    
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col)
        cell.value = header
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = thin_border
    
    row += 1
    
    # Calculate VAT statistics
    vat_totals = {}
    subtotal = 0
    
    # Table rows - sorted by position
    for i, item in enumerate(sorted(quotation.items, key=lambda x: x.position or 0), 1):
        col = 1
        
        # Item number
        cell = ws.cell(row=row, column=col)
        cell.value = i
        cell.font = regular_font
        cell.alignment = center_align
        cell.border = thin_border
        col += 1
        
        # Description
        cell = ws.cell(row=row, column=col)
        cell.value = item.description
        cell.font = regular_font
        cell.alignment = left_align
        cell.border = thin_border
        col += 1
        
        # Scientific name
        cell = ws.cell(row=row, column=col)
        cell.value = item.scientific_name
        cell.font = regular_font
        cell.alignment = left_align
        cell.border = thin_border
        col += 1
        
        # Pot size
        cell = ws.cell(row=row, column=col)
        cell.value = item.pot_size
        cell.font = regular_font
        cell.alignment = center_align
        cell.border = thin_border
        col += 1
        
        # Height
        cell = ws.cell(row=row, column=col)
        cell.value = item.height
        cell.font = regular_font
        cell.alignment = center_align
        cell.border = thin_border
        col += 1
        
        # Quantity
        cell = ws.cell(row=row, column=col)
        cell.value = item.quantity
        cell.font = regular_font
        cell.alignment = center_align
        cell.border = thin_border
        col += 1
        
        # Unit price
        cell = ws.cell(row=row, column=col)
        cell.value = item.selling_price
        cell.font = regular_font
        cell.alignment = right_align
        cell.border = thin_border
        cell.number_format = '#,##0.00'
        col += 1
        
        # VAT rate
        cell = ws.cell(row=row, column=col)
        cell.value = item.vat_rate
        cell.font = regular_font
        cell.alignment = center_align
        cell.border = thin_border
        cell.number_format = '0.0'
        col += 1
        
        # Supplier
        cell = ws.cell(row=row, column=col)
        cell.value = item.supplier
        cell.font = regular_font
        cell.alignment = left_align
        cell.border = thin_border
        col += 1
        
        # Total
        item_total = item.quantity * item.selling_price
        subtotal += item_total
        
        vat_rate = item.vat_rate
        if vat_rate not in vat_totals:
            vat_totals[vat_rate] = 0
        vat_totals[vat_rate] += item_total
        
        cell = ws.cell(row=row, column=col)
        cell.value = item_total
        cell.font = regular_font
        cell.alignment = right_align
        cell.border = thin_border
        cell.number_format = '#,##0.00'
        
        row += 1
    
    # SUMMARY SECTION
    # Subtotal
    ws.merge_cells(f'A{row}:I{row}')
    ws[f'A{row}'] = "Subtotal:"
    ws[f'A{row}'].font = header_font
    ws[f'A{row}'].alignment = right_align
    ws[f'A{row}'].border = thin_border
    
    ws[f'J{row}'] = subtotal
    ws[f'J{row}'].font = header_font
    ws[f'J{row}'].alignment = right_align
    ws[f'J{row}'].border = thin_border
    ws[f'J{row}'].number_format = '#,##0.00'
    
    row += 1
    
    # VAT breakdowns
    grand_total = subtotal
    for vat_rate, vat_amount in sorted(vat_totals.items()):
        vat_value = vat_amount * (vat_rate / 100)
        grand_total += vat_value
        
        ws.merge_cells(f'A{row}:I{row}')
        ws[f'A{row}'] = f"VAT {vat_rate}%:"
        ws[f'A{row}'].font = header_font
        ws[f'A{row}'].alignment = right_align
        ws[f'A{row}'].border = thin_border
        
        ws[f'J{row}'] = vat_value
        ws[f'J{row}'].font = header_font
        ws[f'J{row}'].alignment = right_align
        ws[f'J{row}'].border = thin_border
        ws[f'J{row}'].number_format = '#,##0.00'
        
        row += 1
    
    # Grand total
    total_fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
    
    ws.merge_cells(f'A{row}:I{row}')
    ws[f'A{row}'] = f"TOTAL ({quotation.currency}):"
    ws[f'A{row}'].font = title_font
    ws[f'A{row}'].alignment = right_align
    ws[f'A{row}'].border = thin_border
    ws[f'A{row}'].fill = total_fill
    
    ws[f'J{row}'] = grand_total
    ws[f'J{row}'].font = title_font
    ws[f'J{row}'].alignment = right_align
    ws[f'J{row}'].border = thin_border
    ws[f'J{row}'].fill = total_fill
    ws[f'J{row}'].number_format = '#,##0.00'
    
    row += 2
    
    # Notes section (optional) - using the correct field from the Quotation model
    if hasattr(quotation, 'notes') and quotation.notes:
        ws.merge_cells(f'A{row}:J{row}')
        ws[f'A{row}'] = "NOTES"
        ws[f'A{row}'].font = header_font
        ws[f'A{row}'].fill = header_fill
        
        row += 1
        
        ws.merge_cells(f'A{row}:J{row+3}')
        ws[f'A{row}'] = quotation.notes
        ws[f'A{row}'].font = regular_font
        ws[f'A{row}'].alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
    
    # Generate unique filename
    filename = f"{quotation.quotation_number}_quotation_{uuid.uuid4().hex[:8]}.xlsx"
    file_path = os.path.join(output_folder, filename)
    
    # Save the workbook
    wb.save(file_path)
    
    return file_path