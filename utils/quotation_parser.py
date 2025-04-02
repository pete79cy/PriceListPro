import re
import pandas as pd
import PyPDF2
import uuid
import traceback
from datetime import datetime
from app import db
from models import Product, Customer, PriceList
from utils.logger import logger
from utils.product_verification import verify_product_exists
from utils.pdf_parser import extract_scientific_name, extract_pot_size

def parse_quantity_from_unit(unit_value):
    """
    Extract quantity from unit field handling various formats:
    - Pure numbers: "10" → 10.0
    - Numbers with text: "10 pcs" → 10.0
    - Ranges like "10-15" → We'll take the first number (10.0)
    - Default to 1.0 if no valid number found
    
    Args:
        unit_value (str): The unit field value
        
    Returns:
        float: The extracted quantity or 1.0 if none found
    """
    if not unit_value or not isinstance(unit_value, str):
        return 1.0
        
    # Look for the first number pattern in the string
    match = re.search(r'(\d+(?:\.\d+)?)', str(unit_value))
    if match:
        try:
            return float(match.group(1))
        except (ValueError, TypeError):
            pass
            
    return 1.0

def parse_quotation_file(file_path, customer_id, file_type):
    """
    Parse a PDF or Excel file for quotation creation
    
    Args:
        file_path (str): Path to the file
        customer_id (int): Customer ID for price list lookup
        file_type (str): 'pdf' or 'excel'
        
    Returns:
        dict: Extracted products data
    """
    try:
        if file_type == 'pdf':
            return extract_quotation_data_from_pdf(file_path, customer_id)
        elif file_type == 'excel':
            return extract_quotation_data_from_excel(file_path, customer_id)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    except Exception as e:
        logger.error(f"Error parsing quotation file: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def extract_quotation_data_from_pdf(pdf_path, customer_id):
    """
    Extract quotation data from PDF file
    
    Args:
        pdf_path (str): Path to the PDF file
        customer_id (int): Customer ID for price list lookup
        
    Returns:
        dict: Extracted products with auto-populated prices when available
    """
    logger.info(f"Extracting quotation data from PDF: {pdf_path}")
    
    try:
        # Extract text from PDF
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page_text = pdf_reader.pages[page_num].extract_text()
                text += page_text
        
        # Split text into lines
        lines = text.split('\n')
        
        # Initialize quotation data
        quotation_data = {
            'products': [],
            'customer_id': customer_id,
            'quotation_number': f"QT-{uuid.uuid4().hex[:8].upper()}",
            'quotation_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        # Extract product information from text
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip lines that are clearly headers/footers
            if re.search(r'(invoice|page|date|number|total|subtotal|quotation)', line.lower()):
                continue
            
            # Try to extract product information
            # This is a simplified version - in practice, you'd need more sophisticated parsing logic
            # Look for lines with product descriptions/names
            if len(line.split()) >= 2:  # Only process lines with at least 2 words
                # Extract potential product details
                description = line
                scientific_name = extract_scientific_name(line)
                pot_size = extract_pot_size(line)
                
                # Check if product exists and get price from price list
                product_data = {
                    'name': description,
                    'scientific_name': scientific_name,
                    'pot': pot_size
                }
                
                # Try to find matching product in database
                product, message, is_new, was_created = verify_product_exists(
                    product_data, 
                    create_if_missing=False  # Don't create new products here
                )
                
                # Try to extract height information from the description
                height = None
                height_match = re.search(r'(\d+(?:/\d+)?(?:\s*-\s*\d+)?)\s*cm', line, re.IGNORECASE)
                if height_match:
                    height = height_match.group(0).strip()
                
                # Initialize product entry
                product_entry = {
                    'description': description,
                    'scientific_name': scientific_name,
                    'pot_size': pot_size,
                    'height': height,
                    'quantity': 1,
                    'selling_price': None,
                    'vat_rate': 19,  # Default VAT rate of 19%, can also be 5% or 0%
                    'supplier': None,
                    'cost_price': None,
                    'product_id': product.id if product else None
                }
                
                # If product exists, check for price list entry
                if product:
                    # Get price from customer's price list if available
                    price_list = PriceList.query.filter_by(
                        customer_id=customer_id,
                        product_id=product.id
                    ).first()
                    
                    if price_list:
                        product_entry['selling_price'] = price_list.price
                
                # Add to products list if it looks like a valid product entry
                quotation_data['products'].append(product_entry)
        
        return quotation_data
    
    except Exception as e:
        logger.error(f"Error extracting quotation data from PDF: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def extract_quotation_data_from_excel(excel_path, customer_id):
    """
    Extract quotation data from Excel file according to the specified format:
    
    Required columns (case-insensitive):
    - Category: Type of plant (e.g., Tree, Grasses)
    - Description: Scientific name of the plant
    - Height: Plant height information (e.g., "200cm" or "200/250cm")
    - Unit: Quantity unit (e.g., number of plants)
    - Unit Price: Price per unit in €
    - Actual Size: Actual size details (e.g., "8/10-2,5-3m")
    - Cost: Cost price from supplier
    - Supplier: Supplier name or "in-house production" indicator
    
    Args:
        excel_path (str): Path to the Excel file
        customer_id (int): Customer ID for price list lookup
        
    Returns:
        dict: Extracted products with data from Excel
    """
    logger.info(f"Extracting quotation data from Excel: {excel_path}")
    
    try:
        # Try to read Excel file with different engines and header configurations
        df = None
        try:
            df = pd.read_excel(excel_path, engine='openpyxl')
            logger.info("Successfully read Excel file with openpyxl using default header")
        except Exception as e_openpyxl:
            logger.warning(f"Error reading Excel with openpyxl using default header: {str(e_openpyxl)}")
            try:
                df = pd.read_excel(excel_path, engine='openpyxl', header=1)
                logger.info("Successfully read Excel file with openpyxl using header=1")
            except Exception as e_header1:
                logger.warning(f"Error reading Excel with openpyxl using header=1: {str(e_header1)}")
                df = pd.read_excel(excel_path, engine='openpyxl', header=None)
                logger.info("Successfully read Excel file with openpyxl using header=None")
                
                # Set default column names based on expected structure
                default_columns = ['category', 'description', 'height', 'unit', 'unit_price', 'actual_size', 'cost', 'supplier']
                # Only use as many default columns as we have in the dataframe
                usable_cols = min(len(default_columns), len(df.columns))
                column_rename = {i: default_columns[i] for i in range(usable_cols)}
                df = df.rename(columns=column_rename)
        
        # Normalize column names to handle variations in Excel headers
        df.columns = [str(col).strip().lower() for col in df.columns]
        
        # Map common variations of column names based on the expected structure
        column_maps = {
            'category': ['category', 'plant type', 'type', 'plant category'],
            'description': ['description', 'scientific name', 'botanical name', 'scientific', 'name', 'plant name'],
            'height': ['height', 'plant height', 'h', 'height (cm)', 'height cm'],
            'unit': ['unit', 'unit type', 'quantity unit', 'qty unit'],
            'unit_price': ['unit price', 'price', 'selling price', 'unit cost', 'price (€)', 'price per unit', 'unit_price', 'unit price', 'unitprice'],
            'actual_size': ['actual size', 'size', 'plant size', 'actual_size', 'real size'],
            'cost': ['cost', 'cost price', 'supplier cost', 'purchase price', 'buying price'],
            'supplier': ['supplier', 'vendor', 'source', 'provider', 'producer']
        }
        
        # Map the actual columns to our standard names
        column_mapping = {}
        for our_col, variations in column_maps.items():
            for df_col in df.columns:
                if df_col in variations:
                    column_mapping[df_col] = our_col
                    break
        
        # Rename columns based on mapping
        if column_mapping:
            df = df.rename(columns=column_mapping)
        
        # Initialize quotation data
        quotation_data = {
            'products': [],
            'customer_id': customer_id,
            'quotation_number': f"QT-{uuid.uuid4().hex[:8].upper()}",
            'quotation_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        # Get required column names that should be in the dataframe
        required_columns = ['description', 'unit_price']
        
        # Check if all required columns are present
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns in Excel file: {', '.join(missing_columns)}")
        
        # Remove empty rows and process each row
        df = df.dropna(how='all')
        for index, row in df.iterrows():
            # Skip header-like rows
            if isinstance(row.get('description'), str) and row.get('description').lower() in ['description', 'scientific name', 'name']:
                continue
            
            # Extract data from row based on our expected structure
            description = str(row.get('description', '')) if pd.notna(row.get('description', '')) else ''
            # Using description as scientific_name since that's what it contains according to the format
            scientific_name = description
            category = str(row.get('category', '')) if pd.notna(row.get('category', '')) else ''
            height = str(row.get('height', '')) if pd.notna(row.get('height', '')) else ''
            unit = str(row.get('unit', '')) if pd.notna(row.get('unit', '')) else ''
            actual_size = str(row.get('actual_size', '')) if pd.notna(row.get('actual_size', '')) else ''
            supplier = str(row.get('supplier', '')) if pd.notna(row.get('supplier', '')) else ''
            
            # Format height with "cm" if it's just a number or range without units
            if height and re.match(r'^\d+(/\d+)?$', height.strip()):
                height = f"{height.strip()} cm"
            
            # Extract cost and unit price
            cost_price = None
            unit_price = None
            
            if 'cost' in row and pd.notna(row['cost']):
                try:
                    cost_price = float(row['cost'])
                except (ValueError, TypeError):
                    pass
            
            if 'unit_price' in row and pd.notna(row['unit_price']):
                try:
                    unit_price = float(row['unit_price'])
                except (ValueError, TypeError):
                    pass
            
            # Skip empty rows
            if not description:
                continue
            
            # Check if product exists in the database based on scientific name
            product_data = {
                'name': description,  # Use description as name for lookup
                'scientific_name': scientific_name,
                'category': category
            }
            
            # Try to find matching product in database
            product, message, is_new, was_created = verify_product_exists(
                product_data, 
                create_if_missing=False  # Don't create new products here
            )
            
            # The pot_size in our case is derived from actual_size
            pot_size = actual_size
            
            # Initialize product entry using our new format
            product_entry = {
                'description': description,  # This holds the scientific name as per format
                'scientific_name': scientific_name,
                'pot_size': pot_size,
                'height': height,
                # Try to extract quantity from unit field - handle various formats
                'quantity': parse_quantity_from_unit(unit),
                'selling_price': unit_price,  # Price from the Excel file
                'vat_rate': 19,  # Default VAT rate of 19%, can also be 5% or 0%
                'supplier': supplier,
                'cost_price': cost_price,
                'product_id': product.id if product else None,
                'category': category,
                'actual_size': actual_size,
                'unit': unit
            }
            
            # If unit_price is not available but product exists in database, check price list
            if product and not unit_price:
                # Get price from customer's price list if available
                price_list = PriceList.query.filter_by(
                    customer_id=customer_id,
                    product_id=product.id
                ).first()
                
                if price_list:
                    product_entry['selling_price'] = price_list.price
            
            # Add to products list
            quotation_data['products'].append(product_entry)
        
        return quotation_data
    
    except Exception as e:
        logger.error(f"Error extracting quotation data from Excel: {str(e)}")
        logger.error(traceback.format_exc())
        raise