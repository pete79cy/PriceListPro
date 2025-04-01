import pandas as pd
import logging
import traceback
from app import db
from models import Customer, Product, PriceList
from utils.logger import logger
from utils.product_management import find_or_create_product, create_or_update_price_list

# Log that this module was loaded
logger.info("Excel parser module loaded")

def sanitize_string(value):
    """
    Sanitize a string value to ensure it can be safely stored in the database.
    Handles encoding issues and strips whitespace.
    
    Args:
        value: The value to sanitize (any type)
        
    Returns:
        str or None: The sanitized string, or None if the value was None or empty
    """
    if value is None:
        return None
    # Convert to string if not already
    string_value = str(value)
    # Strip whitespace
    string_value = string_value.strip()
    # Handle potential numeric or other non-string types
    if not isinstance(value, str):
        try:
            string_value = str(value)
        except:
            return None
    # Explicitly encode and decode to handle any character encoding issues
    try:
        # Try UTF-8 first (most common for modern text)
        string_value = string_value.encode('utf-8').decode('utf-8')
    except UnicodeError:
        try:
            # Try with Greek encoding if UTF-8 fails
            string_value = string_value.encode('iso-8859-7').decode('utf-8', errors='ignore')
            logger.info(f"Converted Greek characters in: {value}")
        except UnicodeError:
            # If that fails too, use a more forgiving approach
            string_value = string_value.encode('utf-8', errors='replace').decode('utf-8')
            logger.warning(f"Had to replace characters in: {value}")
    return string_value if string_value else None

def parse_excel_file(file_path, customer_id, upload_id):
    """
    Parse an Excel file containing price list data.
    
    Args:
        file_path (str): Path to the Excel file
        customer_id (int): ID of the customer this price list belongs to
        upload_id (int): ID of the upload record
        
    Returns:
        dict: Stats about the import (new products, price entries, etc.)
    """
    logger.info(f"Parsing Excel file: {file_path} for customer: {customer_id}")
    
    # Initialize stats
    stats = {
        'new_products': 0,
        'price_entries': 0,
        'errors': []
    }
    
    # Log detailed information for debugging
    logger.debug(f"Excel parse starting - file: {file_path}, customer_id: {customer_id}, upload_id: {upload_id}")
    
    try:
        # Read the Excel file with error handling
        try:
            # First try to read the file with the default header=0 (first row as header)
            logger.info(f"Attempting to read Excel with openpyxl using header=0: {file_path}")
            df = pd.read_excel(file_path, engine='openpyxl', header=0)
            logger.info("Successfully read Excel file with openpyxl using header=0")
        except Exception as excel_error_0:
            logger.warning(f"Error reading Excel with openpyxl using header=0: {str(excel_error_0)}")
            try:
                # Try with header=1 (second row as header)
                logger.info(f"Attempting to read Excel with openpyxl using header=1: {file_path}")
                df = pd.read_excel(file_path, engine='openpyxl', header=1)
                logger.info("Successfully read Excel file with openpyxl using header=1")
            except Exception as excel_error_1:
                logger.warning(f"Error reading Excel with openpyxl using header=1: {str(excel_error_1)}")
                try:
                    # Try with header=None and manually set column names later
                    logger.info(f"Attempting to read Excel with openpyxl using header=None: {file_path}")
                    df = pd.read_excel(file_path, engine='openpyxl', header=None)
                    logger.info("Successfully read Excel file with openpyxl using header=None")
                    
                    # Set default column names based on position
                    default_columns = ['category', 'name', 'scientific_name', 'pot', 'price']
                    # Only use as many default columns as we have in the dataframe
                    usable_cols = min(len(default_columns), len(df.columns))
                    column_rename = {i: default_columns[i] for i in range(usable_cols)}
                    df = df.rename(columns=column_rename)
                    logger.info(f"Assigned default column names: {df.columns.tolist()}")
                except Exception as excel_error_none:
                    logger.warning(f"Error reading Excel with openpyxl using header=None: {str(excel_error_none)}")
                    logger.warning(f"Full traceback: {traceback.format_exc()}")
                    # Try with alternative engines as last resort
                    try:
                        logger.info(f"Attempting to read Excel with xlrd: {file_path}")
                        df = pd.read_excel(file_path, engine='xlrd', header=0)
                        logger.info("Successfully read Excel file with xlrd")
                    except Exception as xlrd_error:
                        logger.error(f"Error reading Excel with xlrd: {str(xlrd_error)}")
                        logger.error(f"Full traceback: {traceback.format_exc()}")
                        raise ValueError(f"Could not read Excel file: {file_path}. Please check the file format and ensure it contains the required column headers.")
        
        # Log the columns found for debugging
        logger.info(f"Excel columns found: {df.columns.tolist()}")
        
        # Clean column names - handle non-ASCII characters
        cleaned_columns = {}
        for col in df.columns:
            # Create a clean ASCII version of the column name
            cleaned_col = str(col).encode('ascii', 'ignore').decode('ascii')
            if cleaned_col != col:
                logger.info(f"Cleaned column name: '{col}' -> '{cleaned_col}'")
                df = df.rename(columns={col: cleaned_col})
                
        logger.info(f"Columns after cleaning: {df.columns.tolist()}")
        
        # Map expected column names - case insensitive for flexibility
        column_mapping = {
            'Name': 'name',
            'NAME': 'name',
            'name': 'name',
            'Category': 'category',
            'CATEGORY': 'category',
            'category': 'category', 
            'Scientific Name': 'scientific_name',
            'SCIENTIFIC NAME': 'scientific_name',
            'scientific name': 'scientific_name',
            'Scientific_Name': 'scientific_name',
            'Pot': 'pot',
            'POT': 'pot',
            'pot': 'pot',
            'Pot Size': 'pot',
            'POT SIZE': 'pot',
            'Selling Price': 'price',
            'SELLING PRICE': 'price',
            'Price': 'price',
            'PRICE': 'price',
            'price': 'price',
            # Add Greek column mappings
            'Α/Α': 'index',  # Index number column - will be ignored
            'ΟΝΟΜΑ': 'name',  # Greek for "NAME"
            'ΤΙΜΗ': 'price',  # Greek for "PRICE"
            'ΜΕΓΕΘΟΣ': 'pot'  # Greek for "SIZE"
        }
        
        # Rename columns if they exist in the dataframe
        df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns}, inplace=True)
        
        # Basic validation - check required columns
        if 'name' not in df.columns:
            logger.info(f"No 'name' column found in the Excel file. Available columns: {df.columns.tolist()}")
            
            # Try to find any column that might contain product names
            name_keywords = ['name', 'product', 'item', 'description', 'plant', 'blue', 'tree', 'flower']
            possible_name_columns = []
            
            for col in df.columns:
                if isinstance(col, str):
                    col_lower = col.lower()
                    for keyword in name_keywords:
                        if keyword in col_lower:
                            possible_name_columns.append(col)
                            logger.info(f"Found potential name column: '{col}' (contains '{keyword}')")
                            break
            
            # If we found potential name columns, use the first one
            if possible_name_columns:
                first_name_col = possible_name_columns[0]
                logger.info(f"Using '{first_name_col}' as the product name column")
                df = df.rename(columns={first_name_col: 'name'})
            else:
                logger.info("No keyword-based name columns found. Looking for any string columns...")
                # Check if we have at least one string column that could be a name
                string_cols = []
                for col in df.columns:
                    try:
                        if col != '' and df[col].dtype == 'object':
                            string_cols.append(col)
                            logger.info(f"Found string column: '{col}'")
                    except:
                        logger.warning(f"Error checking column type for '{col}'")
                
                if string_cols:
                    # Use the first non-empty string column as the name column
                    first_string_col = string_cols[0]
                    logger.info(f"Using first string column '{first_string_col}' as the product name column")
                    df = df.rename(columns={first_string_col: 'name'})
                else:
                    # One last attempt - use the second column if it exists (often contains product names)
                    if len(df.columns) > 1:
                        second_col = df.columns[1]
                        logger.info(f"Using second column '{second_col}' as the product name column")
                        df = df.rename(columns={second_col: 'name'})
                    else:
                        raise ValueError("Missing required column: 'Name'. Please ensure your Excel file has a column for product names.")
        
        # Process each row
        for _, row in df.iterrows():
            product_name = row['name']
            
            # Skip rows with missing essential data
            if pd.isna(product_name):
                continue
            
            # Get optional fields
            category = row.get('category') if 'category' in df.columns and not pd.isna(row.get('category')) else None
            scientific_name = row.get('scientific_name') if 'scientific_name' in df.columns and not pd.isna(row.get('scientific_name')) else None
            pot = row.get('pot') if 'pot' in df.columns and not pd.isna(row.get('pot')) else None
            
            # Look for price in the 'price' column, or try to find a numeric column that could be price
            price = None
            if 'price' in df.columns and not pd.isna(row.get('price')):
                price = row.get('price')
            else:
                # Try to find a price column by looking for numeric columns
                numeric_cols = []
                for col in df.columns:
                    if col != 'name' and col != 'category' and col != 'scientific_name' and col != 'pot':
                        try:
                            # Check if this column has numeric values
                            val = row.get(col)
                            if val is not None and not pd.isna(val):
                                # Try to convert to float
                                try:
                                    float_val = float(val)
                                    numeric_cols.append((col, float_val))
                                except:
                                    pass
                        except:
                            pass
                
                # If we found numeric columns, use the first one as price
                if numeric_cols:
                    price_col, price_val = numeric_cols[0]
                    logger.debug(f"Using column '{price_col}' as price with value {price_val}")
                    price = price_val
            
            # Use safe string values
            safe_name = sanitize_string(product_name)
            safe_category = sanitize_string(category)
            safe_scientific_name = sanitize_string(scientific_name)
            safe_pot = sanitize_string(pot)
            
            # Prepare product data dictionary
            product_data = {
                'name': safe_name,
                'category': safe_category,
                'scientific_name': safe_scientific_name,
                'pot': safe_pot,
                'description': f"{safe_scientific_name or ''} {safe_pot or ''}".strip() or None
            }
            
            # Use the find_or_create_product function from product_management
            product, message, is_new = find_or_create_product(product_data)
            
            if is_new:
                logger.info(message)
                stats['new_products'] += 1
            else:
                logger.debug(message)
            
            # Create or update price list entry if price exists
            if price is not None and product:
                source_file_name = f"upload_{upload_id}"
                price_list, price_message, is_new_price = create_or_update_price_list(
                    customer_id=customer_id,
                    product_id=product.id,
                    new_price=price,
                    source_file=source_file_name
                )
                
                if is_new_price:
                    stats['price_entries'] += 1
                
                logger.debug(price_message)
        
        # Commit all changes
        db.session.commit()
        logger.info(f"Excel import complete. Stats: {stats}")
        return stats
        
    except Exception as e:
        db.session.rollback()
        error_message = f"Error parsing Excel file: {str(e)}"
        logger.error(error_message)
        logger.error(f"Full traceback: {traceback.format_exc()}")
        stats['errors'].append(error_message)
        
        # Return stats with error information instead of raising exception
        # This allows the web interface to display the error message
        return stats
