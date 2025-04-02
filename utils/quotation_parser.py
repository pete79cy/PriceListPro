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
                    'vat_rate': 19,  # Default VAT rate
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
    Extract quotation data from Excel file
    
    Args:
        excel_path (str): Path to the Excel file
        customer_id (int): Customer ID for price list lookup
        
    Returns:
        dict: Extracted products with auto-populated prices when available
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
                
                # Set default column names based on position
                default_columns = ['category', 'name', 'scientific_name', 'pot', 'price']
                # Only use as many default columns as we have in the dataframe
                usable_cols = min(len(default_columns), len(df.columns))
                column_rename = {i: default_columns[i] for i in range(usable_cols)}
                df = df.rename(columns=column_rename)
        
        # Normalize column names to handle variations in Excel headers
        df.columns = [str(col).strip().lower() for col in df.columns]
        
        # Map common variations of column names
        column_maps = {
            'name': ['name', 'product', 'description', 'product name', 'product description', 'item'],
            'scientific_name': ['scientific name', 'scientific', 'latin name', 'botanical name', 'botanical'],
            'pot': ['pot', 'pot size', 'size', 'container', 'container size'],
            'height': ['height', 'plant height', 'h', 'height (cm)', 'height cm'],
            'price': ['price', 'unit price', 'selling price', 'sell price', 'cost']
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
        
        # Remove empty rows and process each row
        df = df.dropna(how='all')
        for index, row in df.iterrows():
            # Skip header-like rows
            if isinstance(row.get('name'), str) and row.get('name').lower() in ['name', 'product', 'description']:
                continue
            
            # Extract data from row
            description = str(row.get('name', '')) if pd.notna(row.get('name', '')) else ''
            scientific_name = str(row.get('scientific_name', '')) if pd.notna(row.get('scientific_name', '')) else ''
            pot_size = str(row.get('pot', '')) if pd.notna(row.get('pot', '')) else ''
            height = str(row.get('height', '')) if pd.notna(row.get('height', '')) else ''
            
            # Format height with "cm" if it's just a number
            if height and re.match(r'^\d+(/\d+)?$', height.strip()):
                height = f"{height.strip()} cm"
            
            # Skip empty rows
            if not description and not scientific_name:
                continue
            
            # Ensure we have at least a description
            if not description and scientific_name:
                description = scientific_name
            
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
            
            # Extract selling price from Excel if available
            excel_price = None
            if 'price' in row and pd.notna(row['price']):
                try:
                    excel_price = float(row['price'])
                except (ValueError, TypeError):
                    pass
            
            # Initialize product entry
            product_entry = {
                'description': description,
                'scientific_name': scientific_name,
                'pot_size': pot_size,
                'height': height,
                'quantity': 1,
                'selling_price': excel_price,  # Use price from Excel if available
                'vat_rate': 19,  # Default VAT rate
                'supplier': None,
                'cost_price': None,
                'product_id': product.id if product else None
            }
            
            # If product exists and we don't have a price from Excel, check price list
            if product and not excel_price:
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