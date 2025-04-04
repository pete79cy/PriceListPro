"""
Invoice Excel Parser - Functions for parsing customer invoice Excel files.
Handles specific format with merged cells for:
- Customer name in line 11 (columns J-AE)
- From line 16 onwards:
  - Scientific name in merged columns E-L
  - Description in merged columns M-S
  - Quantity in merged columns T-W
  - Price in merged columns X-Z
  - VAT type in merged columns AA-AD (5% or 19%)
  - Total excluding VAT in column AE
"""

import pandas as pd
import re
import os
import uuid
import traceback
from datetime import datetime
from openpyxl import load_workbook
from app import db
from models import Product, Customer, PriceList
from utils.logger import logger
from utils.product_verification import verify_product_exists

def extract_customer_name_from_invoice(excel_path):
    """
    Extract customer name from line 11, typically in columns J-AE
    The function will scan a few rows around line 11 to locate the customer name.
    
    Args:
        excel_path (str): Path to the Excel file
        
    Returns:
        str: Customer name or None if not found
    """
    try:
        # Load the workbook with openpyxl to handle merged cells
        wb = load_workbook(excel_path, data_only=True)
        ws = wb.active
        
        # Log the workbook structure
        logger.info(f"Extracting customer name from file: {excel_path}")
        logger.info(f"Sheet names: {wb.sheetnames}, Active sheet: {ws.title}")
        
        # Try to find customer name by scanning rows 9-13 and columns 1-15
        # This makes our parser more flexible to handle slight variations in invoice formats
        customer_name = None
        
        # First look in expected position: line 11, column J
        expected_cell = ws.cell(row=11, column=10)  # Column J = 10
        expected_value = expected_cell.value
        logger.info(f"Value at expected customer cell (J11): {expected_value}")
        
        if expected_value and isinstance(expected_value, str) and len(expected_value.strip()) > 3:
            customer_name = expected_value.strip()
        else:
            # Scan nearby rows and columns to locate customer name
            logger.info("Customer name not found at expected location, scanning nearby cells")
            for row in range(9, 14):  # Check rows 9-13
                for col in range(1, 16):  # Check columns A-O
                    cell_value = ws.cell(row=row, column=col).value
                    if cell_value and isinstance(cell_value, str) and len(cell_value.strip()) > 3:
                        logger.info(f"Potential customer name found at row {row}, column {col}: {cell_value}")
                        # Only set customer_name if it's not yet set or if this value is longer
                        # (assuming longer strings are more likely to be proper names)
                        if not customer_name or len(cell_value) > len(customer_name):
                            customer_name = cell_value.strip()
        
        if customer_name:
            logger.info(f"Extracted customer name: {customer_name}")
            return customer_name
        else:
            logger.warning("Could not extract customer name from invoice after scanning multiple cells")
            return None
            
    except Exception as e:
        logger.error(f"Error extracting customer name from invoice: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def parse_vat_rate(vat_text):
    """
    Parse VAT rate from text like "19%" or "5%"
    
    Args:
        vat_text (str): Text containing VAT rate
        
    Returns:
        float: VAT rate as float (19.0, 5.0) or default 19.0 if not found
    """
    if not vat_text or not isinstance(vat_text, str):
        return 19.0
    
    # Look for percentage in the text
    match = re.search(r'(\d+)%', vat_text)
    if match:
        try:
            return float(match.group(1))
        except (ValueError, TypeError):
            pass
    
    # If we can't parse it, return default
    return 19.0

def parse_invoice_excel(excel_path, customer_id=None):
    """
    Parse customer invoice Excel file with specific format
    
    Args:
        excel_path (str): Path to the Excel file
        customer_id (int, optional): Customer ID if known. If None, will try to find customer by name.
        
    Returns:
        dict: Extracted products and price data
    """
    logger.info(f"Parsing customer invoice Excel: {excel_path}")
    
    try:
        # First, extract customer name if customer_id is not provided
        customer = None
        if not customer_id:
            customer_name = extract_customer_name_from_invoice(excel_path)
            if customer_name:
                # Try to find customer by name
                customer = Customer.query.filter(Customer.name.ilike(f"%{customer_name}%")).first()
                if customer:
                    customer_id = customer.id
                    logger.info(f"Found customer by name: {customer.name} (ID: {customer_id})")
                else:
                    logger.warning(f"Customer not found by name: {customer_name}")
        else:
            # Get customer by ID
            customer = Customer.query.get(customer_id)
        
        if not customer_id:
            raise ValueError("Customer ID not provided and could not be determined from invoice")
        
        # Load the workbook with openpyxl to handle merged cells
        wb = load_workbook(excel_path, data_only=True)
        ws = wb.active
        
        # Debug workbook structure
        logger.info(f"Invoice Excel file loaded successfully. Sheet names: {wb.sheetnames}")
        logger.info(f"Active sheet: {ws.title}")
        logger.info(f"Sheet dimensions: {ws.dimensions}")
        
        # Try to examine cell A1 and some key cells to check if the structure matches expected
        try:
            logger.info(f"Cell A1 value: {ws.cell(row=1, column=1).value}")
            logger.info(f"Customer name cell (J11): {ws.cell(row=11, column=10).value}")
            logger.info(f"First product cell (E16): {ws.cell(row=16, column=5).value}")
        except Exception as cell_err:
            logger.error(f"Error checking reference cells: {str(cell_err)}")
        
        # Initialize results
        products = []
        
        # Scan for the starting row - look for rows that might contain product data
        # This makes the parser more robust to different Excel layouts
        data_row_start = None
        for scan_row in range(12, 25):  # Look between rows 12-25 for product data
            scientific_name = ws.cell(row=scan_row, column=5).value  # Column E
            description = ws.cell(row=scan_row, column=13).value     # Column M
            price = ws.cell(row=scan_row, column=24).value           # Column X
            
            # Check if this row has what looks like product data
            if (scientific_name or description) and price:
                logger.info(f"Found potential data row at {scan_row}")
                data_row_start = scan_row
                break
        
        if not data_row_start:
            # If we didn't find a clear starting row, try more columns on row 16
            # as it's the expected starting point
            logger.info("No clear data starting row found, checking alternative column positions")
            data_row_start = 16
                
        # Also check some alternative column positions for scientific names/descriptions
        # This helps with Excel files that might have different column structures
        scientific_name_cols = [5, 6, 4]  # Try column E (5) first, then F, then D
        description_cols = [13, 12, 14]   # Try column M (13) first, then L, then N
        quantity_cols = [20, 19, 21]      # Try column T (20) first, then S, then U  
        price_cols = [24, 23, 25]         # Try column X (24) first, then W, then Y
        vat_cols = [27, 26, 28]           # Try column AA (27) first, then Z, then AB
        total_cols = [31, 30, 32]         # Try column AE (31) first, then AD, then AF
        
        logger.info(f"Starting to process product data from row {data_row_start}")
        
        # Start processing from detected start row
        row = data_row_start
        max_rows = 100  # Safety limit to prevent infinite loops
        row_count = 0
                
        # Keep track of whether we've found any products
        found_any_products = False
        
        while row_count < max_rows:
            row_count += 1
            
            # Examine multiple possible scientific name columns
            scientific_name = None
            for col in scientific_name_cols:
                cell_value = ws.cell(row=row, column=col).value
                if cell_value:
                    scientific_name = cell_value
                    logger.info(f"Found scientific name in column {col}: {scientific_name}")
                    break
            
            # If no scientific name found in any column, check if we can find data in other columns
            # Sometimes the Excel might have only product descriptions without scientific names
            description = None
            for col in description_cols:
                cell_value = ws.cell(row=row, column=col).value
                if cell_value:
                    description = cell_value
                    logger.info(f"Found description in column {col}: {description}")
                    break
                    
            # Look for price in different possible columns
            price = None
            for col in price_cols:
                cell_value = ws.cell(row=row, column=col).value
                if cell_value and (isinstance(cell_value, (int, float)) or 
                                  (isinstance(cell_value, str) and re.search(r'\d', cell_value))):
                    price = cell_value
                    logger.info(f"Found price in column {col}: {price}")
                    break
            
            # Check if we have at least one of scientific name or description, and a price
            # If not, we've probably reached the end of the product data
            if not ((scientific_name or description) and price):
                # If we've already found products in previous rows, assume this is the end of the list
                if found_any_products:
                    logger.info(f"No more product data at row {row}, stopping extraction")
                    break
                # If we haven't found any products yet, try the next row
                logger.info(f"No product data at row {row}, trying next row")
                row += 1
                continue
            
            # Mark that we've found at least one product
            found_any_products = True
            
            # Use scientific name as description if no description found
            if not description:
                description = scientific_name
            elif not scientific_name:
                # If only description is found but no scientific name, 
                # sometimes the scientific name is part of the description
                scientific_name = description
            
            # Look for quantity in different possible columns
            quantity = None
            for col in quantity_cols:
                cell_value = ws.cell(row=row, column=col).value
                if cell_value:
                    quantity = cell_value
                    logger.info(f"Found quantity in column {col}: {quantity}")
                    break
            
            # Look for VAT information in different possible columns
            vat_text = None
            for col in vat_cols:
                cell_value = ws.cell(row=row, column=col).value
                if cell_value:
                    vat_text = cell_value
                    logger.info(f"Found VAT in column {col}: {vat_text}")
                    break
            
            vat_rate = parse_vat_rate(vat_text)
            
            # Look for total in different possible columns
            total_ex_vat = None
            for col in total_cols:
                cell_value = ws.cell(row=row, column=col).value
                if cell_value and (isinstance(cell_value, (int, float)) or 
                                  (isinstance(cell_value, str) and re.search(r'\d', cell_value))):
                    total_ex_vat = cell_value
                    logger.info(f"Found total in column {col}: {total_ex_vat}")
                    break
            
            # Debug row data
            logger.info(f"Row {row} data: Scientific name: {scientific_name}, Description: {description}, " +
                       f"Quantity: {quantity}, Price: {price}, VAT: {vat_text}, Total ex VAT: {total_ex_vat}")
            
            # Clean and convert data
            try:
                if quantity and isinstance(quantity, (int, float)):
                    quantity = float(quantity)
                else:
                    # Try to extract number from text
                    if quantity and isinstance(quantity, str):
                        match = re.search(r'(\d+(?:\.\d+)?)', quantity)
                        if match:
                            quantity = float(match.group(1))
                        else:
                            quantity = 1.0
                    else:
                        quantity = 1.0
                        
                if price and isinstance(price, (int, float)):
                    price = float(price)
                else:
                    # Try to extract number from text
                    if price and isinstance(price, str):
                        match = re.search(r'(\d+(?:\.\d+)?)', price)
                        if match:
                            price = float(match.group(1))
                        else:
                            price = 0.0
                    else:
                        price = 0.0
            except (ValueError, TypeError):
                quantity = 1.0
                price = 0.0
            
            # Check if product exists in the database
            product_data = {
                'name': description,
                'scientific_name': scientific_name
            }
            
            product, message, is_new, was_created = verify_product_exists(
                product_data,
                create_if_missing=True  # Create product if not found
            )
            
            # Create product entry
            product_entry = {
                'product_id': product.id if product else None,
                'scientific_name': scientific_name,
                'description': description,
                'quantity': quantity,
                'price': price,
                'vat_rate': vat_rate,
                'total_ex_vat': total_ex_vat
            }
            
            products.append(product_entry)
            
            # Move to next row
            row += 1
        
        return {
            'customer_id': customer_id,
            'customer': customer,
            'products': products,
            'invoice_date': datetime.now().strftime('%Y-%m-%d'),
            'source_file': os.path.basename(excel_path)
        }
        
    except Exception as e:
        logger.error(f"Error parsing customer invoice Excel: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def update_price_list_from_invoice(invoice_data):
    """
    Update customer price lists based on invoice data
    
    Args:
        invoice_data (dict): Parsed invoice data from parse_invoice_excel
        
    Returns:
        dict: Summary of updates (updated_count, new_count, error_count)
    """
    logger.info(f"Updating price lists for customer ID: {invoice_data['customer_id']}")
    
    updated_count = 0
    new_count = 0
    error_count = 0
    
    customer_id = invoice_data['customer_id']
    source_file = invoice_data.get('source_file', 'unknown')
    
    for product_entry in invoice_data['products']:
        try:
            product_id = product_entry['product_id']
            price = product_entry['price']
            
            if not product_id or price <= 0:
                logger.warning(f"Skipping price list update for invalid product or price: {product_entry}")
                continue
                
            # Check if price list entry already exists
            existing_price = PriceList.query.filter_by(
                customer_id=customer_id,
                product_id=product_id
            ).first()
            
            if existing_price:
                # Update existing price
                if existing_price.price != price:
                    # Only update if price has changed
                    existing_price.price = price
                    existing_price.updated_at = datetime.utcnow()
                    existing_price.source_file = source_file
                    db.session.add(existing_price)
                    updated_count += 1
                    logger.info(f"Updated price for product ID {product_id} to {price}")
            else:
                # Create new price list entry
                new_price = PriceList(
                    customer_id=customer_id,
                    product_id=product_id,
                    price=price,
                    effective_date=datetime.now().date(),
                    source_file=source_file
                )
                db.session.add(new_price)
                new_count += 1
                logger.info(f"Added new price for product ID {product_id}: {price}")
                
        except Exception as e:
            logger.error(f"Error updating price list for product: {str(e)}")
            error_count += 1
    
    # Commit changes if any updates were made
    if updated_count > 0 or new_count > 0:
        try:
            db.session.commit()
            logger.info(f"Successfully committed {updated_count + new_count} price list changes")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error committing price list changes: {str(e)}")
            error_count += updated_count + new_count
            updated_count = 0
            new_count = 0
    
    return {
        'updated_count': updated_count,
        'new_count': new_count,
        'error_count': error_count,
        'customer_id': customer_id
    }