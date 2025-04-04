import os
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from utils.logger import logger

def create_excel_template(output_path):
    """
    Create an Excel template file for price list uploads.
    
    Args:
        output_path (str): Path where the Excel template will be saved
        
    Returns:
        bool: True if successful, False if error
    """
    try:
        logger.info(f"Creating Excel template at: {output_path}")
        
        # Create a workbook and select the active worksheet
        wb = Workbook()
        ws = wb.active
        ws.title = "Price List Template"
        
        # Define headers
        headers = ["Category", "Name", "Scientific Name", "Pot", "Selling Price"]
        
        # Set up header style
        header_font = Font(bold=True, size=12, color="FFFFFF")
        header_fill = PatternFill(start_color="2C3E50", end_color="2C3E50", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        
        # Write headers and apply styles
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            # Set column width based on header length
            column_letter = get_column_letter(col_num)
            ws.column_dimensions[column_letter].width = max(15, len(header) + 5)
        
        # Add example data
        examples = [
            ["Trees", "Oak Tree", "Quercus robur", "15L", 49.99],
            ["Flowers", "Red Rose", "Rosa 'Red Hybrid'", "2L", 12.50],
            ["Climbers", "Ivy", "Hedera helix", "3L", 8.75]
        ]
        
        # Write example data
        for row_num, example in enumerate(examples, 2):
            for col_num, value in enumerate(example, 1):
                cell = ws.cell(row=row_num, column=col_num, value=value)
                cell.alignment = Alignment(horizontal="left", vertical="center")
        
        # Add instruction row
        instruction_row = len(examples) + 3
        ws.cell(row=instruction_row, column=1, value="Instructions:")
        ws.cell(row=instruction_row, column=1).font = Font(bold=True)
        
        instructions = [
            "1. Fill in your price list data using the format shown in the examples above.",
            "2. 'Category' and 'Scientific Name' are optional but recommended.",
            "3. 'Name' and 'Selling Price' are required fields.",
            "4. 'Pot' should include the pot size (e.g., '2L', '5L', etc.).",
            "5. Save the file as .xlsx or .xls before uploading."
        ]
        
        for i, instruction in enumerate(instructions):
            ws.cell(row=instruction_row + i + 1, column=1, value=instruction)
            ws.merge_cells(f"A{instruction_row + i + 1}:E{instruction_row + i + 1}")
            ws.cell(row=instruction_row + i + 1, column=1).alignment = Alignment(horizontal="left")
        
        # Save the workbook
        wb.save(output_path)
        logger.info(f"Excel template created successfully at: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating Excel template: {str(e)}")
        return False

def create_quotation_template(output_path):
    """
    Create an Excel template file for quotation uploads based on the specified format.
    
    Args:
        output_path (str): Path where the Excel template will be saved
        
    Returns:
        bool: True if successful, False if error
    """
    try:
        logger.info(f"Creating quotation Excel template at: {output_path}")
        
        # Create a workbook and select the active worksheet
        wb = Workbook()
        ws = wb.active
        ws.title = "Quotation Template"
        
        # Define headers based on the specified format and matching test01.xlsx
        headers = ["Category", "Description", "Height", "Unit", "Unit price", "Actual Size", "Cost", "Supplier"]
        
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
        
        # Write headers and apply styles
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border
            
            # Set column width based on header length and content
            column_letter = get_column_letter(col_num)
            ws.column_dimensions[column_letter].width = max(15, len(header) + 5)
        
        # Add example data based on the format and matching test01.xlsx
        examples = [
            ["Trees", "Cupressus sempervirens 'Totem'", "200-220 cm", 4, 45.00, "60L", 35.00, "Shaelos"],
            ["Trees", "Feijoa sellowiana (Multi-stem)", "180-200 cm", 4, 20.00, "15L", 15.00, "Arocaria"],
            ["Grasses", "Agapanthus africanus", "20-30 cm", 8, 3.50, "2L", None, None]
        ]
        
        # Write example data
        for row_num, example in enumerate(examples, 2):
            for col_num, value in enumerate(example, 1):
                cell = ws.cell(row=row_num, column=col_num, value=value)
                cell.alignment = Alignment(horizontal="left", vertical="center")
                cell.border = thin_border
                
                # Format the cost and price columns
                if col_num in [5, 7]:  # Unit Price and Cost columns
                    cell.number_format = '€#,##0.00'
        
        # Add instruction row
        instruction_row = len(examples) + 3
        ws.cell(row=instruction_row, column=1, value="Instructions:")
        ws.cell(row=instruction_row, column=1).font = Font(bold=True)
        
        instructions = [
            "1. Fill in your quotation data using the format shown in the examples above.",
            "2. 'Description' (Scientific name) and 'Unit price' are required fields.",
            "3. 'Category' indicates the type of plant (e.g., Trees, Grasses, etc.).",
            "4. 'Height' should be in format like '200-220 cm' or '180-200 cm'.",
            "5. 'Unit' should contain the quantity (number of plants) as a number.",
            "6. 'Actual Size' typically contains the pot size (e.g., '60L', '15L').",
            "7. 'Cost' is the cost price from the supplier (optional).",
            "8. 'Supplier' should be the supplier name like 'Shaelos' or 'Arocaria'.",
            "9. Save the file as .xlsx or .xls before uploading."
        ]
        
        for i, instruction in enumerate(instructions):
            ws.cell(row=instruction_row + i + 1, column=1, value=instruction)
            ws.merge_cells(f"A{instruction_row + i + 1}:H{instruction_row + i + 1}")
            ws.cell(row=instruction_row + i + 1, column=1).alignment = Alignment(horizontal="left")
        
        # Save the workbook
        wb.save(output_path)
        logger.info(f"Quotation Excel template created successfully at: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating quotation Excel template: {str(e)}")
        return False

def ensure_template_exists(app_static_folder):
    """
    Ensure that the Excel templates exist in the static folder.
    If they don't exist, create them.
    
    Args:
        app_static_folder (str): Path to the app's static folder
        
    Returns:
        dict: Paths to the template files
    """
    templates_folder = os.path.join(app_static_folder, 'templates')
    os.makedirs(templates_folder, exist_ok=True)
    
    # Price list template
    price_list_template_path = os.path.join(templates_folder, 'price_list_template.xlsx')
    if not os.path.exists(price_list_template_path):
        create_excel_template(price_list_template_path)
    
    # Quotation template
    quotation_template_path = os.path.join(templates_folder, 'quotation_template.xlsx')
    if not os.path.exists(quotation_template_path):
        create_quotation_template(quotation_template_path)
    
    return {
        'price_list': price_list_template_path,
        'quotation': quotation_template_path
    }