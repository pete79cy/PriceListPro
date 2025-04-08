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

def generate_quotation_excel(quotation, output_folder, columns=None):
    """
    Generate an Excel file from a quotation.
    
    Args:
        quotation: The Quotation object to export
        output_folder: The folder where the Excel file will be saved
        columns: Optional list of column configurations to include. Each item
                 should be a dict with 'key' and 'label' keys.
        
    Returns:
        str: The path to the generated Excel file
    """
    # Get company information from CompanySettings
    company = CompanySettings.query.first()
    if not company:
        company = CompanySettings()  # Use default values if no settings exist
        
    # Define default column configuration if not provided
    if columns is None:
        columns = [
            {"key": "index", "label": "#"},
            {"key": "description", "label": "Description"},
            {"key": "scientific_name", "label": "Scientific Name"},
            {"key": "pot_size", "label": "Actual Size"},
            {"key": "height", "label": "Asked Size"},
            {"key": "quantity", "label": "Quantity"},
            {"key": "unit_price", "label": "Unit Price"},
            {"key": "vat_rate", "label": "VAT Rate"},
            {"key": "supplier", "label": "Supplier"},
            {"key": "total_price", "label": "Total"}
        ]
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
    # Table headers based on selected columns
    headers = []
    column_keys = []
    
    # Map column keys to their data extraction methods
    column_data_map = {
        "index": lambda item, i: i,
        "description": lambda item, i: item.description,
        "scientific_name": lambda item, i: item.scientific_name,
        "pot_size": lambda item, i: item.pot_size,
        "height": lambda item, i: item.height,
        "quantity": lambda item, i: item.quantity,
        "unit_price": lambda item, i: item.selling_price,
        "vat_rate": lambda item, i: item.vat_rate,
        "supplier": lambda item, i: item.supplier,
        "total_price": lambda item, i: item.quantity * item.selling_price
    }
    
    # Format map for special number formatting
    format_map = {
        "unit_price": "#,##0.00",
        "vat_rate": "0.0",
        "total_price": "#,##0.00"
    }
    
    # Alignment map for columns
    alignment_map = {
        "index": center_align,
        "description": left_align,
        "scientific_name": left_align,
        "pot_size": center_align,
        "height": center_align,
        "quantity": center_align,
        "unit_price": right_align,
        "vat_rate": center_align,
        "supplier": left_align,
        "total_price": right_align
    }
    
    # Build the column headers and keys
    for col_config in columns:
        key = col_config["key"]
        label = col_config["label"]
        
        # Add currency symbol to price columns
        if key == "unit_price":
            label = f"{label} ({quotation.currency})"
        elif key == "total_price":
            label = f"{label} ({quotation.currency})"
            
        headers.append(label)
        column_keys.append(key)
    
    # Write headers to the worksheet
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
    items = sorted(quotation.items, key=lambda x: x.position or 0)
    for i, item in enumerate(items, 1):
        # Calculate item total (needed for VAT calculations)
        item_total = item.quantity * item.selling_price
        subtotal += item_total
        
        # Record VAT information
        vat_rate = item.vat_rate
        if vat_rate not in vat_totals:
            vat_totals[vat_rate] = 0
        vat_totals[vat_rate] += item_total
        
        # Write selected columns to the row
        for col_idx, key in enumerate(column_keys, 1):
            if key in column_data_map:
                # Get the cell value using the mapping function
                cell_value = column_data_map[key](item, i)
                
                # Write to the cell
                cell = ws.cell(row=row, column=col_idx)
                cell.value = cell_value
                cell.font = regular_font
                
                # Apply specific alignment
                if key in alignment_map:
                    cell.alignment = alignment_map[key]
                else:
                    cell.alignment = left_align
                
                # Apply border
                cell.border = thin_border
                
                # Apply number format if needed
                if key in format_map:
                    cell.number_format = format_map[key]
        
        row += 1
    
    # SUMMARY SECTION
    # Get the number of columns and their letters
    column_count = len(column_keys)
    if column_count == 0:
        column_count = 1  # Ensure at least one column
    
    last_column_letter = get_column_letter(column_count)
    total_column_letter = last_column_letter
    
    # If there's room for a summary column, add it
    if column_count > 1:
        # Use the last column for totals
        label_column_end = get_column_letter(column_count - 1)
    else:
        # If only one column, split it for label and value
        label_column_end = last_column_letter
        total_column_letter = last_column_letter
    
    # Subtotal
    ws.merge_cells(f'A{row}:{label_column_end}{row}')
    ws[f'A{row}'] = "Subtotal:"
    ws[f'A{row}'].font = header_font
    ws[f'A{row}'].alignment = right_align
    ws[f'A{row}'].border = thin_border
    
    ws[f'{total_column_letter}{row}'] = subtotal
    ws[f'{total_column_letter}{row}'].font = header_font
    ws[f'{total_column_letter}{row}'].alignment = right_align
    ws[f'{total_column_letter}{row}'].border = thin_border
    ws[f'{total_column_letter}{row}'].number_format = '#,##0.00'
    
    row += 1
    
    # VAT breakdowns
    grand_total = subtotal
    for vat_rate, vat_amount in sorted(vat_totals.items()):
        vat_value = vat_amount * (vat_rate / 100)
        grand_total += vat_value
        
        ws.merge_cells(f'A{row}:{label_column_end}{row}')
        ws[f'A{row}'] = f"VAT {vat_rate}%:"
        ws[f'A{row}'].font = header_font
        ws[f'A{row}'].alignment = right_align
        ws[f'A{row}'].border = thin_border
        
        ws[f'{total_column_letter}{row}'] = vat_value
        ws[f'{total_column_letter}{row}'].font = header_font
        ws[f'{total_column_letter}{row}'].alignment = right_align
        ws[f'{total_column_letter}{row}'].border = thin_border
        ws[f'{total_column_letter}{row}'].number_format = '#,##0.00'
        
        row += 1
    
    # Grand total
    total_fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
    
    ws.merge_cells(f'A{row}:{label_column_end}{row}')
    ws[f'A{row}'] = f"TOTAL ({quotation.currency}):"
    ws[f'A{row}'].font = title_font
    ws[f'A{row}'].alignment = right_align
    ws[f'A{row}'].border = thin_border
    ws[f'A{row}'].fill = total_fill
    
    ws[f'{total_column_letter}{row}'] = grand_total
    ws[f'{total_column_letter}{row}'].font = title_font
    ws[f'{total_column_letter}{row}'].alignment = right_align
    ws[f'{total_column_letter}{row}'].border = thin_border
    ws[f'{total_column_letter}{row}'].fill = total_fill
    ws[f'{total_column_letter}{row}'].number_format = '#,##0.00'
    
    row += 2
    
    # Notes section (optional) - using the correct field from the Quotation model
    if hasattr(quotation, 'notes') and quotation.notes:
        # Use all available columns for notes
        last_col = get_column_letter(max(column_count, 1))
        
        ws.merge_cells(f'A{row}:{last_col}{row}')
        ws[f'A{row}'] = "NOTES"
        ws[f'A{row}'].font = header_font
        ws[f'A{row}'].fill = header_fill
        
        row += 1
        
        ws.merge_cells(f'A{row}:{last_col}{row+3}')
        ws[f'A{row}'] = quotation.notes
        ws[f'A{row}'].font = regular_font
        ws[f'A{row}'].alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
    
    # Generate unique filename
    filename = f"{quotation.quotation_number}_quotation_{uuid.uuid4().hex[:8]}.xlsx"
    file_path = os.path.join(output_folder, filename)
    
    # Save the workbook
    wb.save(file_path)
    
    return file_path