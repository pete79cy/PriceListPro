import pandas as pd
import logging
import traceback
from app import db
from models import Customer, Product, PriceList
from utils.logger import logger

# Log that this module was loaded
logger.info("Excel parser module loaded")

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
            'price': 'price'
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
            
            # Get or create product - use case-insensitive comparison
            logger.debug(f"Looking for product with name: {product_name}")
            
            # For Greek character names, we'll just create a new product every time
            # This avoids encoding issues and potential database errors
            product = None
            normalized_name = ""
            
            try:
                if isinstance(product_name, str):
                    normalized_name = product_name.strip()
                    logger.debug(f"Normalized product name for creation: '{normalized_name}'")
                else:
                    normalized_name = str(product_name).strip() if product_name is not None else ""
            except Exception as encoding_error:
                logger.warning(f"Error normalizing product name: {str(encoding_error)}")
                normalized_name = ""
            
            # Skip all database lookups - just create new products
            logger.debug(f"Will create new product with name: '{normalized_name}'")
            product = None
            
            if not product:
                # Create new product - log all fields first to aid debugging
                logger.debug(f"Creating new product - Name: {product_name}, Category: {category}, Scientific Name: {scientific_name}, Pot: {pot}")
                
                # Keep the original Greek characters, just strip whitespace
                safe_name = str(product_name).strip() if product_name is not None else None
                safe_category = str(category).strip() if category is not None else None
                safe_scientific_name = str(scientific_name).strip() if scientific_name is not None else None
                safe_pot = str(pot).strip() if pot is not None else None
                safe_description = f"{safe_scientific_name or ''} {safe_pot or ''}".strip() or None
                
                logger.debug(f"Using original values for product - Name: '{safe_name}', Category: '{safe_category}', Scientific: '{safe_scientific_name}', Pot: '{safe_pot}'")
                
                
                product = Product(
                    name=safe_name,
                    category=safe_category,
                    scientific_name=safe_scientific_name,
                    pot=safe_pot,
                    description=safe_description
                )
                db.session.add(product)
                db.session.flush()  # Get the product ID without committing
                stats['new_products'] += 1
            else:
                # Update existing product fields if provided - use safe values
                logger.debug(f"Updating existing product: {product.name} (ID: {product.id})")
                
                # Keep the original Greek characters, just strip whitespace
                safe_category = str(category).strip() if category is not None else None
                safe_scientific_name = str(scientific_name).strip() if scientific_name is not None else None
                safe_pot = str(pot).strip() if pot is not None else None
                
                logger.debug(f"Updating product with original values - Category: '{safe_category}', Scientific: '{safe_scientific_name}', Pot: '{safe_pot}'")
                
                if safe_category is not None:
                    product.category = safe_category
                if safe_scientific_name is not None:
                    product.scientific_name = safe_scientific_name
                if safe_pot is not None:
                    product.pot = safe_pot
                if safe_scientific_name is not None or safe_pot is not None:
                    safe_description = f"{safe_scientific_name or ''} {safe_pot or ''}".strip()
                    product.description = safe_description or product.description
            
            # Create price list entry if price exists
            if price is not None:
                price_list = PriceList(
                    customer_id=customer_id,
                    product_id=product.id,
                    price=price,
                    source_file=f"upload_{upload_id}"
                )
                db.session.add(price_list)
                stats['price_entries'] += 1
        
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
