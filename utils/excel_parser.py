import pandas as pd
import logging
import traceback
import unicodedata
from unidecode import unidecode
from app import db
from models import Customer, Product, PriceList
from utils.logger import logger

# Log that this module was loaded
logger.info("Excel parser module loaded")

def transliterate_text(text):
    """
    Transliterate text from any language (including Greek) to ASCII.
    This is better than just stripping non-ASCII characters as it tries
    to find appropriate ASCII equivalents.
    
    Args:
        text (str): Text to transliterate
        
    Returns:
        str: Transliterated ASCII text
    """
    if not isinstance(text, str) or not text:
        return text
    
    # Ensure text is a proper Unicode string before conversion
    if not isinstance(text, str):
        text = str(text)
    
    # Clean any strange whitespace characters
    text = text.strip()
    
    # First try unidecode which handles many languages including Greek
    try:
        transliterated = unidecode(text)
        logger.debug(f"Unidecode result for '{text}': '{transliterated}'")
        
        # If unidecode returned an empty string or mostly spaces, 
        # try Unicode normalization as a fallback
        if not transliterated.strip() or len(transliterated.strip()) < len(text.strip()) // 2:
            logger.debug(f"Unidecode produced poor result for '{text}', trying normalization")
            normalized = unicodedata.normalize('NFKD', text)
            ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')
            
            # If normalization also fails, keep the original 
            if not ascii_text.strip():
                logger.warning(f"Both transliteration methods failed for '{text}', preserving original")
                return text  # Return original to preserve data
            
            transliterated = ascii_text
    except Exception as e:
        logger.error(f"Error during transliteration for '{text}': {str(e)}")
        # Fall back to simple ASCII encoding in case of error
        try:
            transliterated = text.encode('ascii', 'ignore').decode('ascii')
        except:
            logger.error(f"Even fallback ASCII encoding failed for '{text}'")
            return text  # Return original as last resort
    
    # If all conversion attempts resulted in empty string, return original
    if not transliterated.strip() and text.strip():
        logger.warning(f"All transliteration attempts produced empty result for '{text}', preserving original")
        return text
        
    logger.debug(f"Transliterated '{text}' to '{transliterated}'")
    return transliterated

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
        # Initialize counters for batch processing
        batch_size = 100
        current_batch_count = 0
        new_products_batch = []
        price_list_batch = []
        
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
            
            # Transliterate product name using our new function (handles Greek and other non-ASCII chars)
            original_name = product_name
            normalized_name = None
            
            try:
                if isinstance(product_name, str):
                    # First, strip whitespace
                    cleaned_name = product_name.strip()
                    # Then, transliterate to ASCII properly
                    normalized_name = transliterate_text(cleaned_name)
                    logger.debug(f"Transliterated product name: '{cleaned_name}' to '{normalized_name}'")
                    
                    # If transliteration returned empty string, use fallback
                    if not normalized_name or not normalized_name.strip():
                        logger.warning(f"Transliteration returned empty result for '{cleaned_name}', falling back to basic ASCII")
                        normalized_name = cleaned_name.encode('ascii', 'ignore').decode('ascii')
            except Exception as encoding_error:
                logger.warning(f"Error transliterating product name: {str(encoding_error)}")
                normalized_name = str(product_name).encode('ascii', 'ignore').decode('ascii')
                
            # Use case-insensitive search with transliterated name
            if normalized_name and normalized_name.strip():
                try:
                    logger.debug(f"Searching for product with name like: '{normalized_name}'")
                    product = Product.query.filter(Product.name.ilike(f"%{normalized_name}%")).first()
                except Exception as db_error:
                    logger.error(f"Database error searching for product: {str(db_error)}")
                    # Fallback to even more conservative search
                    product = None
            else:
                logger.warning(f"No valid name for database search, original: '{original_name}'")
                product = None
            
            if not product:
                # Create new product - log all fields first to aid debugging
                logger.debug(f"Creating new product - Name: {product_name}, Category: {category}, Scientific Name: {scientific_name}, Pot: {pot}")
                
                # Ensure we have clean, properly-transliterated strings for all fields
                # Use our transliterate function to better handle non-ASCII characters (including Greek)
                safe_name = transliterate_text(str(product_name).strip()) if product_name is not None else None
                safe_category = transliterate_text(str(category).strip()) if category is not None else None
                safe_scientific_name = transliterate_text(str(scientific_name).strip()) if scientific_name is not None else None
                safe_pot = transliterate_text(str(pot).strip()) if pot is not None else None
                safe_description = transliterate_text(f"{safe_scientific_name or ''} {safe_pot or ''}".strip()) or None
                
                logger.debug(f"Sanitized product values - Name: '{safe_name}', Category: '{safe_category}', Scientific: '{safe_scientific_name}', Pot: '{safe_pot}'")
                
                
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
                
                # Ensure we have clean, properly-transliterated strings for all fields
                # Use our transliterate function to better handle non-ASCII characters (including Greek)
                safe_category = transliterate_text(str(category).strip()) if category is not None else None
                safe_scientific_name = transliterate_text(str(scientific_name).strip()) if scientific_name is not None else None
                safe_pot = transliterate_text(str(pot).strip()) if pot is not None else None
                
                logger.debug(f"Updating product with transliterated values - Category: '{safe_category}', Scientific: '{safe_scientific_name}', Pot: '{safe_pot}'")
                
                if safe_category is not None:
                    product.category = safe_category
                if safe_scientific_name is not None:
                    product.scientific_name = safe_scientific_name
                if safe_pot is not None:
                    product.pot = safe_pot
                if safe_scientific_name is not None or safe_pot is not None:
                    safe_description = transliterate_text(f"{safe_scientific_name or ''} {safe_pot or ''}".strip())
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
                
                # Increment batch counter
                current_batch_count += 1
                
                # Commit changes in batches to prevent timeouts
                if current_batch_count >= batch_size:
                    logger.info(f"Committing batch of {current_batch_count} operations")
                    try:
                        db.session.commit()
                        # Reset batch counter after successful commit
                        current_batch_count = 0
                    except Exception as batch_error:
                        db.session.rollback()
                        logger.error(f"Error committing batch: {str(batch_error)}")
                        raise  # Re-raise to handle in outer exception block
        
        # Commit any remaining records in the final batch
        if current_batch_count > 0:
            logger.info(f"Committing final batch of {current_batch_count} operations")
            db.session.commit()
            
        logger.info(f"Excel import complete. Stats: {stats}")
        return stats
        
    except Exception as e:
        # Rollback in case of any errors
        db.session.rollback()
        error_message = f"Error parsing Excel file: {str(e)}"
        logger.error(error_message)
        logger.error(f"Full traceback: {traceback.format_exc()}")
        stats['errors'].append(error_message)
        
        # Return stats with error information instead of raising exception
        # This allows the web interface to display the error message
        return stats
