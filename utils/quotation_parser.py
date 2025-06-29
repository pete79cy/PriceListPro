import re
import pandas as pd
import PyPDF2
import uuid
import traceback
from datetime import datetime
from app import db
from models import Product, Customer, PriceList, Quotation
from utils.logger import logger
from utils.product_verification import verify_product_exists
from utils.pdf_parser import extract_scientific_name, extract_pot_size

def generate_unique_quotation_number():
    """
    Generate a unique quotation number with format PAK-YYYY-XXX
    where YYYY is the current year and XXX is a sequential number 
    starting from 001.
    
    Returns:
        str: A unique quotation number
    """
    year = datetime.now().year
    prefix = f"PAK-{year}-"
    
    # Find the highest sequential number in the current year
    last_quotation = Quotation.query.filter(
        Quotation.quotation_number.like(f"{prefix}%")
    ).order_by(db.desc(Quotation.quotation_number)).first()
    
    if last_quotation:
        # Extract the sequential number part
        try:
            last_seq_num = int(last_quotation.quotation_number.split('-')[2])
            new_seq_num = last_seq_num + 1
        except (IndexError, ValueError):
            # If there's an error parsing the last number, start from 1
            new_seq_num = 1
    else:
        # No existing quotations for this year
        new_seq_num = 1
    
    # Format as 3-digit number with leading zeros
    return f"{prefix}{new_seq_num:03d}"

def parse_quantity_from_unit(unit_value):
    """
    Extract quantity from unit field handling various formats:
    - Pure numbers: "10" → 10.0
    - Numbers with text: "10 pcs" → 10.0
    - Ranges like "10-15" → We'll take the first number (10.0)
    - European decimal format: "2,5" → 2.5
    - Default to 1.0 if no valid number found
    
    Args:
        unit_value (any): The unit field value (can be string, int, float)
        
    Returns:
        float: The extracted quantity or 1.0 if none found
    """
    logger.info(f"Parsing quantity from unit value: {unit_value} of type {type(unit_value)}")
    
    # Handle direct numeric types
    if isinstance(unit_value, (int, float)):
        logger.info(f"Direct numeric value detected: {unit_value}")
        return float(unit_value)
    
    # If it's None or empty, return default
    if not unit_value:
        logger.info(f"Empty or None value detected, returning default 1.0")
        return 1.0
    
    # Convert to string for processing    
    unit_str = str(unit_value).strip()
    logger.info(f"Processing string value: '{unit_str}'")
    
    # If the string is a simple number, parse it directly
    try:
        # Replace comma with dot for European number format
        cleaned_value = unit_str.replace(',', '.')
        parsed_value = float(cleaned_value)
        logger.info(f"Successfully parsed as simple number: {parsed_value}")
        return parsed_value
    except ValueError:
        # Not a simple number, continue with regex
        logger.info(f"Not a simple number, trying regex extraction")
        pass
        
    # Look for the first number pattern in the string
    # This regex handles both dot and comma as decimal separators
    match = re.search(r'(\d+(?:[.,]\d+)?)', unit_str)
    if match:
        try:
            # Replace comma with dot for European number format
            value = match.group(1).replace(',', '.')
            parsed_value = float(value)
            logger.info(f"Successfully extracted number with regex: {parsed_value}")
            return parsed_value
        except (ValueError, TypeError):
            # Log the failure for debugging
            logger.warning(f"Failed to parse quantity from: {unit_value}")
            pass
            
    logger.warning(f"No valid number found in '{unit_value}', returning default 1.0")
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
            'quotation_number': generate_unique_quotation_number(),
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
                    'supplier': "In-house Production",  # Default to In-house Production
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
        # Log the file being processed
        logger.info(f"Processing Excel file for quotation: {excel_path}")
        
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
                try:
                    df = pd.read_excel(excel_path, engine='openpyxl', header=None)
                    logger.info("Successfully read Excel file with openpyxl using header=None")
                    
                    # Set default column names based on expected structure
                    default_columns = ['category', 'description', 'height', 'unit', 'unit_price', 'actual_size', 'cost', 'supplier']
                    # Only use as many default columns as we have in the dataframe
                    usable_cols = min(len(default_columns), len(df.columns))
                    column_rename = {i: default_columns[i] for i in range(usable_cols)}
                    df = df.rename(columns=column_rename)
                except Exception as e_header_none:
                    logger.error(f"Failed to read Excel with any header configuration: {str(e_header_none)}")
                    raise ValueError("Could not read Excel file with any header configuration. Please check if the file is corrupted or in an unsupported format.")

        # Log the detected columns
        logger.info(f"Detected columns in Excel: {list(df.columns)}")
        
        # Normalize column names to handle variations in Excel headers
        df.columns = [str(col).strip().lower() for col in df.columns]
        
        # Map common variations of column names based on the expected structure
        column_maps = {
            'category': ['category', 'plant type', 'type', 'plant category', 'cat', 'cat.'],
            'description': ['description', 'scientific name', 'botanical name', 'scientific', 'name', 'plant name', 'desc', 'plant', 'description / scientific name'],
            'common_name': ['common name', 'common', 'name common', 'vernacular name', 'english name', 'display name'],
            'height': ['height', 'plant height', 'h', 'height (cm)', 'height cm', 'h(cm)', 'h cm'],
            'unit': ['unit', 'unit type', 'quantity unit', 'qty unit', 'units', 'qty', 'quantity'],
            'unit_price': ['unit price', 'price', 'selling price', 'unit cost', 'price (€)', 'price per unit', 'unit_price', 'unit price', 'unitprice', 'price €', 'unit price €', 'each'],
            'actual_size': ['actual size', 'size', 'plant size', 'actual_size', 'real size', 'pot size', 'container', 'pot'],
            'cost': ['cost', 'cost price', 'supplier cost', 'purchase price', 'buying price', 'cost €', 'buy price'],
            'supplier': ['supplier', 'vendor', 'source', 'provider', 'producer', 'origin']
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
        
        # Log the standardized columns
        logger.info(f"Standardized columns: {list(df.columns)}")
        
        # Initialize quotation data
        quotation_data = {
            'products': [],
            'customer_id': customer_id,
            'quotation_number': generate_unique_quotation_number(),
            'quotation_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        # Get required column names that should be in the dataframe
        required_columns = ['description']  # Only description is truly required
        
        # Check if all required columns are present
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns in Excel file: {', '.join(missing_columns)}")
        
        # Remove empty rows and process each row
        df = df.dropna(how='all')
        logger.info(f"Processing {len(df)} non-empty rows from Excel file")
        
        for index, row in df.iterrows():
            # Skip header-like rows
            if isinstance(row.get('description'), str) and row.get('description').lower() in ['description', 'scientific name', 'name']:
                logger.info(f"Skipping header-like row with description: {row.get('description')}")
                continue
            
            # Debugging: Log the data type of the row and the 'unit' field if it exists
            logger.info(f"Row {index} type: {type(row)}")
            if 'unit' in row:
                logger.info(f"Unit field type: {type(row['unit'])}, value: {row['unit']}")
                
            # Extract data from row based on our expected structure
            description = str(row.get('description', '')) if pd.notna(row.get('description', '')) else ''
            
            # Skip empty description rows
            if not description.strip():
                logger.info(f"Skipping row {index} due to empty description")
                continue
                
            # Try to get common name if available, otherwise use description for both fields
            common_name = str(row.get('common_name', '')) if pd.notna(row.get('common_name', '')) else ''
            
            # Determine which field goes where
            # Description field often contains scientific name in Excel files for plant nurseries
            scientific_name = description  # Use description as scientific name
            display_description = common_name if common_name else description  # Use common name as description if available
            
            category = str(row.get('category', '')) if pd.notna(row.get('category', '')) else ''
            height = str(row.get('height', '')) if pd.notna(row.get('height', '')) else ''
            # Check for direct numeric value in unit field
            raw_unit_value = row.get('unit', '')
            if pd.notna(raw_unit_value):
                if isinstance(raw_unit_value, (int, float)) and raw_unit_value > 0:
                    # If it's already a number, don't convert to string for parsing
                    logger.info(f"Found direct numeric unit value: {raw_unit_value}, type: {type(raw_unit_value)}")
                    unit = raw_unit_value  # Keep as numeric value
                else:
                    unit = str(raw_unit_value)
            else:
                unit = ''
            actual_size = str(row.get('actual_size', '')) if pd.notna(row.get('actual_size', '')) else ''
            supplier = str(row.get('supplier', '')) if pd.notna(row.get('supplier', '')) else ''
            
            # Format height properly
            if height:
                height = height.strip()
                # Add "cm" only if it's a number without units
                if re.match(r'^\d+(/\d+)?(-\d+(/\d+)?)?$', height):
                    height = f"{height} cm"
            
            # Set pot_size based on actual_size
            pot_size = actual_size.strip() if actual_size else ''
            
            # Set default supplier to "In-house Production" if empty
            if not supplier.strip():
                supplier = "In-house Production"
            
            # Extract cost and unit price
            cost_price = None
            unit_price = None
            
            if 'cost' in row and pd.notna(row['cost']):
                try:
                    cost_price = float(row['cost'])
                except (ValueError, TypeError):
                    # Try to handle currency formatting with commas or currency symbols
                    try:
                        cost_str = str(row['cost']).replace('€', '').replace(',', '.').strip()
                        cost_price = float(re.sub(r'[^\d.]', '', cost_str))
                    except:
                        pass
            
            if 'unit_price' in row and pd.notna(row['unit_price']):
                try:
                    unit_price = float(row['unit_price'])
                except (ValueError, TypeError):
                    # Try to handle currency formatting with commas or currency symbols
                    try:
                        price_str = str(row['unit_price']).replace('€', '').replace(',', '.').strip()
                        unit_price = float(re.sub(r'[^\d.]', '', price_str))
                    except:
                        pass
            
            # Check if product exists in the database based on scientific name
            product_data = {
                'name': scientific_name,  # Use scientific name as name for lookup
                'scientific_name': scientific_name,
                'category': category
            }
            
            # Try to find matching product in database
            product, message, is_new, was_created = verify_product_exists(
                product_data, 
                create_if_missing=False  # Don't create new products here
            )
            
            # Parse quantity with enhanced error handling and detailed logging
            try:
                # Log the raw unit value for debugging
                logger.info(f"About to parse quantity from raw unit value: {unit} of type {type(unit)}")
                
                # Convert unit to number if possible
                quantity = parse_quantity_from_unit(unit)
                
                # Log the final extracted quantity
                logger.info(f"Successfully extracted quantity: {quantity} from unit value: {unit}")
            except Exception as e:
                logger.warning(f"Failed to parse quantity from unit value: {unit}, error: {str(e)}")
                quantity = 1  # Default to 1 if parsing fails
                logger.info(f"Using default quantity: {quantity}")
            
            # Determine pricing status based on whether we have a price
            pricing_status = 'CONFIRMED' if unit_price is not None else 'PENDING'
            
            # Initialize product entry using our new format
            product_entry = {
                'description': display_description,  # Use common name or description
                'scientific_name': scientific_name,  # Scientific name from description field
                'pot_size': pot_size,
                'height': height,
                'quantity': quantity,
                'selling_price': unit_price,  # Price from the Excel file (can be None)
                'vat_rate': 19,  # Default VAT rate of 19%, can also be 5% or 0%
                'pricing_status': pricing_status,  # CONFIRMED or PENDING
                'supplier': supplier,
                'cost_price': cost_price,
                'product_id': product.id if product else None,
                'category': category,
                'actual_size': actual_size,
                'unit': unit
            }
            
            # Log the extracted product entry
            logger.info(f"Extracted product: {scientific_name}, price: {unit_price}, pot size: {pot_size}")
            
            # If unit_price is not available but product exists in database, check price list
            if product and not unit_price:
                # Get price from customer's price list if available
                price_list = PriceList.query.filter_by(
                    customer_id=customer_id,
                    product_id=product.id
                ).first()
                
                if price_list:
                    product_entry['selling_price'] = price_list.price
                    logger.info(f"Using price list price for {scientific_name}: {price_list.price}")
            
            # Add to products list
            quotation_data['products'].append(product_entry)
        
        logger.info(f"Successfully extracted {len(quotation_data['products'])} products from Excel")
        return quotation_data
    
    except Exception as e:
        logger.error(f"Error extracting quotation data from Excel: {str(e)}")
        logger.error(traceback.format_exc())
        raise