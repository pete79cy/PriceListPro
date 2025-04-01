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
        
        # Map expected column names
        column_mapping = {
            'Name': 'name',
            'Category': 'category',
            'Scientific Name': 'scientific_name',
            'Pot': 'pot',
            'Selling Price': 'price'
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
        logging.debug(f"Excel import complete. Stats: {stats}")
        return stats
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error parsing Excel file: {str(e)}")
        stats['errors'].append(str(e))
        raise
