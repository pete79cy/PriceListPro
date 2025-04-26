"""
Template-based Excel generator for quotations.
This module provides functionality to export quotation data as Excel files
using the specific template format requested.
"""

import os
import uuid
import logging
import shutil
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

logger = logging.getLogger(__name__)

def generate_template_excel(quotation, output_folder, template_path=None):
    """
    Generate an Excel file from a quotation using the specified template format.
    
    Args:
        quotation: The Quotation object to export
        output_folder: The folder where the Excel file will be saved
        template_path: Optional path to a template Excel file. If not provided,
                      a new file will be created with the standard template format.
        
    Returns:
        str: The path to the generated Excel file
    """
    try:
        # Create a new workbook with the template structure
        wb = Workbook()
        ws = wb.active
        ws.title = "Quotation Template"
        
        # Set up column headers to match the template format
        headers = ["Category", "Description", "Height", "Unit", "Unit Price", "Actual Size", "Cost", "Supplier"]
        
        # Set up header style
        header_font = Font(bold=True, size=12, color="FFFFFF")
        header_fill = PatternFill(start_color="336699", end_color="336699", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        
        # Define border style
        thin_border = Border(
            left=Side(style='thin'), 
            right=Side(style='thin'), 
            top=Side(style='thin'), 
            bottom=Side(style='thin')
        )
        
        # Apply column widths
        ws.column_dimensions['A'].width = 15  # Category
        ws.column_dimensions['B'].width = 40  # Description
        ws.column_dimensions['C'].width = 12  # Height
        ws.column_dimensions['D'].width = 10  # Unit
        ws.column_dimensions['E'].width = 12  # Unit Price
        ws.column_dimensions['F'].width = 12  # Actual Size
        ws.column_dimensions['G'].width = 12  # Cost
        ws.column_dimensions['H'].width = 15  # Supplier
        
        # Write headers and apply styles
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border
        
        # Add quotation items starting from row 2
        row_idx = 2
        
        for item in quotation.items:
            # Determine category (if applicable)
            category = ""
            if hasattr(item, 'product') and item.product and hasattr(item.product, 'category'):
                category = item.product.category or ""
            
            # Map QuotationItem fields to template columns
            ws.cell(row=row_idx, column=1, value=category)  # Category
            ws.cell(row=row_idx, column=2, value=item.description)  # Description
            ws.cell(row=row_idx, column=3, value=item.height or "")  # Height
            ws.cell(row=row_idx, column=4, value=item.quantity)  # Unit
            ws.cell(row=row_idx, column=5, value=item.selling_price)  # Unit Price
            ws.cell(row=row_idx, column=6, value=item.pot_size or "")  # Actual Size
            ws.cell(row=row_idx, column=7, value=item.cost_price if hasattr(item, 'cost_price') else "")  # Cost
            ws.cell(row=row_idx, column=8, value=item.supplier or "")  # Supplier
            
            # Apply borders to all cells in this row
            for col in range(1, 9):
                ws.cell(row=row_idx, column=col).border = thin_border
            
            row_idx += 1
        
        # Add customer info at the bottom (optional)
        row_idx += 2  # Add some space
        ws.cell(row=row_idx, column=1, value="Quotation:")
        ws.cell(row=row_idx, column=2, value=quotation.quotation_number)
        
        row_idx += 1
        ws.cell(row=row_idx, column=1, value="Customer:")
        ws.cell(row=row_idx, column=2, value=quotation.customer.name if quotation.customer else "")
        
        row_idx += 1
        ws.cell(row=row_idx, column=1, value="Date:")
        ws.cell(row=row_idx, column=2, value=quotation.quotation_date.strftime('%Y-%m-%d') if quotation.quotation_date else "")
        
        # Generate unique filename with quotation number
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{quotation.quotation_number}_quotation_{timestamp}.xlsx"
        file_path = os.path.join(output_folder, filename)
        
        # Save the workbook
        wb.save(file_path)
        logger.info(f"Generated template Excel for quotation #{quotation.quotation_number} at {file_path}")
        
        return file_path
        
    except Exception as e:
        logger.error(f"Error generating template Excel for quotation #{quotation.quotation_number}: {str(e)}")
        return None


def generate_bulk_template_excel(quotations, output_folder, template_path=None):
    """
    Generate multiple Excel files for quotations using the specified template format.
    
    Args:
        quotations: List of Quotation objects to export
        output_folder: The folder where the Excel files will be saved
        template_path: Optional path to a template Excel file
        
    Returns:
        list: Paths to the generated Excel files
    """
    excel_files = []
    
    for quotation in quotations:
        try:
            excel_path = generate_template_excel(
                quotation=quotation,
                output_folder=output_folder,
                template_path=template_path
            )
            
            if excel_path:
                excel_files.append(excel_path)
                logger.info(f"Generated template Excel for quotation #{quotation.quotation_number}")
                
        except Exception as e:
            logger.error(f"Error generating template Excel for quotation #{quotation.quotation_number}: {str(e)}")
            # Continue with other quotations even if one fails
    
    return excel_files