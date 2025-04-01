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
            # First try with default engine
            logger.info(f"Attempting to read Excel with openpyxl: {file_path}")
            df = pd.read_excel(file_path, engine='openpyxl')
            logger.info("Successfully read Excel file with openpyxl")
        except Exception as excel_error:
            logger.warning(f"Error reading Excel with openpyxl: {str(excel_error)}")
            logger.warning(f"Full traceback: {traceback.format_exc()}")
            # Try with alternative engines
            try:
                logger.info(f"Attempting to read Excel with xlrd: {file_path}")
                df = pd.read_excel(file_path, engine='xlrd')
                logger.info("Successfully read Excel file with xlrd")
            except Exception as xlrd_error:
                logger.error(f"Error reading Excel with xlrd: {str(xlrd_error)}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                raise ValueError(f"Could not read Excel file: {file_path}. Please check the file format.")
        
        # Log the columns found for debugging
        logger.info(f"Excel columns found: {df.columns.tolist()}")
        
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
            
            # Get or create product
            product = Product.query.filter(Product.name == product_name).first()
            
            if not product:
                # Create new product
                product = Product(
                    name=product_name,
                    category=category,
                    scientific_name=scientific_name,
                    pot=pot,
                    description=f"{scientific_name or ''} {pot or ''}".strip() or None
                )
                db.session.add(product)
                db.session.flush()  # Get the product ID without committing
                stats['new_products'] += 1
            else:
                # Update existing product fields if provided
                if category is not None:
                    product.category = category
                if scientific_name is not None:
                    product.scientific_name = scientific_name
                if pot is not None:
                    product.pot = pot
                if scientific_name is not None or pot is not None:
                    product.description = f"{scientific_name or ''} {pot or ''}".strip() or product.description
            
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
