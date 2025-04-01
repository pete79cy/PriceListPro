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
            # First try with default engine and handle first-row header issue
            logger.info(f"Attempting to read Excel with openpyxl: {file_path}")
            # Skip the non-header row and use the first row with actual headers
            df = pd.read_excel(file_path, engine='openpyxl', header=1)
            logger.info("Successfully read Excel file with openpyxl")
        except Exception as excel_error:
            logger.warning(f"Error reading Excel with openpyxl: {str(excel_error)}")
            logger.warning(f"Full traceback: {traceback.format_exc()}")
            # Try with alternative engines
            try:
                logger.info(f"Attempting to read Excel with xlrd: {file_path}")
                df = pd.read_excel(file_path, engine='xlrd', header=1)
                logger.info("Successfully read Excel file with xlrd")
            except Exception as xlrd_error:
                logger.error(f"Error reading Excel with xlrd: {str(xlrd_error)}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                raise ValueError(f"Could not read Excel file: {file_path}. Please check the file format.")
        
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
            raise ValueError("Missing required column: 'Name'")
        
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
            price = row.get('price') if 'price' in df.columns and not pd.isna(row.get('price')) else None
            
            # Get or create product - use case-insensitive comparison
            logger.debug(f"Looking for product with name: {product_name}")
            
            # Normalize product name for database query
            # Convert to UTF-8 to handle encoding issues
            normalized_name = product_name
            try:
                # Prevent encoding issues by explicitly handling UTF-8 conversion
                if isinstance(product_name, str):
                    normalized_name = product_name.strip()
                    logger.debug(f"Normalized product name: {normalized_name}")
            except Exception as encoding_error:
                logger.warning(f"Error normalizing product name: {str(encoding_error)}")
                
            # Use case-insensitive search to avoid encoding issues
            product = Product.query.filter(Product.name.ilike(f"{normalized_name}")).first()
            
            if not product:
                # Create new product - log all fields first to aid debugging
                logger.debug(f"Creating new product - Name: {product_name}, Category: {category}, Scientific Name: {scientific_name}, Pot: {pot}")
                
                # Ensure we have clean, properly-encoded strings for all fields
                safe_name = str(product_name).strip() if product_name is not None else None
                safe_category = str(category).strip() if category is not None else None
                safe_scientific_name = str(scientific_name).strip() if scientific_name is not None else None
                safe_pot = str(pot).strip() if pot is not None else None
                safe_description = f"{safe_scientific_name or ''} {safe_pot or ''}".strip() or None
                
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
                
                # Ensure we have clean, properly-encoded strings for all fields
                safe_category = str(category).strip() if category is not None else None
                safe_scientific_name = str(scientific_name).strip() if scientific_name is not None else None
                safe_pot = str(pot).strip() if pot is not None else None
                
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
