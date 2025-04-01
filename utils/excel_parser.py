import pandas as pd
import logging
from app import db
from models import Customer, Product, PriceList

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
    logging.debug(f"Parsing Excel file: {file_path} for customer: {customer_id}")
    
    # Initialize stats
    stats = {
        'new_products': 0,
        'price_entries': 0,
        'errors': []
    }
    
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)
        
        # Basic validation - check required columns
        required_columns = ['product_name', 'price']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Additional columns that might be present
        sku_column = 'sku' if 'sku' in df.columns else None
        description_column = 'description' if 'description' in df.columns else None
        effective_date_column = 'effective_date' if 'effective_date' in df.columns else None
        expiry_date_column = 'expiry_date' if 'expiry_date' in df.columns else None
        
        # Process each row
        for _, row in df.iterrows():
            product_name = row['product_name']
            price = row['price']
            
            # Skip rows with missing essential data
            if pd.isna(product_name) or pd.isna(price):
                continue
            
            # Get or create product
            product = Product.query.filter(
                (Product.name == product_name) | 
                (sku_column and Product.sku == row.get(sku_column, None))
            ).first()
            
            if not product:
                # Create new product
                product = Product(
                    name=product_name,
                    sku=row.get(sku_column) if sku_column and not pd.isna(row.get(sku_column)) else None,
                    description=row.get(description_column) if description_column and not pd.isna(row.get(description_column)) else None
                )
                db.session.add(product)
                db.session.flush()  # Get the product ID without committing
                stats['new_products'] += 1
            
            # Create price list entry
            price_list = PriceList(
                customer_id=customer_id,
                product_id=product.id,
                price=price,
                effective_date=row.get(effective_date_column) if effective_date_column and not pd.isna(row.get(effective_date_column)) else None,
                expiry_date=row.get(expiry_date_column) if expiry_date_column and not pd.isna(row.get(expiry_date_column)) else None,
                source_file=f"upload_{upload_id}"
            )
            db.session.add(price_list)
            stats['price_entries'] += 1
        
        # Commit all changes
        db.session.commit()
        logging.debug(f"Excel import complete. Stats: {stats}")
        return stats
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error parsing Excel file: {str(e)}")
        stats['errors'].append(str(e))
        raise
