import re
import logging
import PyPDF2
from datetime import datetime

def extract_scientific_name(text):
    """Extract scientific name from text if present"""
    if not text:
        return None
    sci_name_match = re.search(r'^([A-Z][a-z]+ [a-z]+)(?:\s+|$)', text)
    if sci_name_match:
        return sci_name_match.group(1)
    return None

def extract_pot_size(text):
    """Extract pot size from text if present"""
    if not text:
        return None
    pot_match = re.search(r'(\d+L|\d+\s*L)', text)
    if pot_match:
        return pot_match.group(1)
    return None

def extract_text_from_pdf(pdf_path):
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text content
    """
    logging.debug(f"Extracting text from PDF: {pdf_path}")
    
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text()
        return text
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {str(e)}")
        raise

def extract_invoice_data(text):
    """
    Extract invoice data from the PDF text using regex and NLP techniques.
    
    Args:
        text (str): Text content from the PDF
        
    Returns:
        dict: Extracted invoice data including invoice number, date, items, and totals
    """
    logging.debug("Extracting invoice data from text")
    
    invoice_data = {
        'invoice_number': None,
        'invoice_date': None,
        'total_amount': None,
        'customer_name': None,
        'items': []
    }
    
    # Extract invoice number
    invoice_number_match = re.search(r'(?:INVOICE Number|INVOICE #|Invoice Number|Invoice #)[:\s]+([A-Za-z0-9\-]+)', text, re.IGNORECASE)
    if invoice_number_match:
        invoice_data['invoice_number'] = invoice_number_match.group(1).strip()
    
    # Extract invoice date
    date_patterns = [
        r'(?:INVOICE DATE|Invoice Date|Bill Date)[:\s]+(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
        r'(?:Date|Dated)[:\s]+(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
        r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})'  # Generic date pattern
    ]
    
    for pattern in date_patterns:
        date_match = re.search(pattern, text, re.IGNORECASE)
        if date_match:
            date_str = date_match.group(1).strip()
            # Try to parse the date in various formats
            for date_format in ['%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y', '%d.%m.%Y', '%m.%d.%Y']:
                try:
                    date_obj = datetime.strptime(date_str, date_format)
                    invoice_data['invoice_date'] = date_obj.strftime('%Y-%m-%d')
                    break
                except ValueError:
                    continue
            if invoice_data['invoice_date']:
                break
    
    # Extract customer name
    customer_section = re.search(r'Customer Information(.*?)(?:Plant Passport|[A-Z\/]{2,})', text, re.DOTALL | re.IGNORECASE)
    if customer_section:
        customer_info = customer_section.group(1).strip()
        customer_name_match = re.search(r'Name\s+(.*?)(?:Address|$)', customer_info, re.DOTALL | re.IGNORECASE)
        if customer_name_match:
            invoice_data['customer_name'] = customer_name_match.group(1).strip()
    
    # Extract total amount and currency
    currency_symbol = '€'  # Default currency symbol
    total_patterns = [
        r'TOTAL\s*(?::|([€$£])|(EUR|USD|GBP))?\s*(\d+[.,]\d+)',
        r'(?:Total|Amount Due|Grand Total|Sum)[:\s](?:([€$£])|(EUR|USD|GBP))?\s*(\d+[.,]\d+)',
        r'([€$£])\s*(\d+[.,]\d+)'  # Generic currency pattern
    ]
    
    for pattern in total_patterns:
        total_match = re.search(pattern, text, re.IGNORECASE)
        if total_match:
            groups = total_match.groups()
            if 'TOTAL' in pattern or '(?:Total' in pattern:
                # Handle patterns with currency symbol/code
                if groups[0]:  # Symbol found
                    currency_symbol = groups[0]
                elif groups[1]:  # Currency code found
                    currency_map = {'EUR': '€', 'USD': '$', 'GBP': '£'}
                    currency_symbol = currency_map.get(groups[1].upper(), '€')
                
                # Get the amount from the correct group
                total_str = groups[2].strip().replace(',', '.')
            else:
                # Handle simple currency pattern
                currency_symbol = groups[0] or '€'
                total_str = groups[1].strip().replace(',', '.')
            
            try:
                invoice_data['total_amount'] = float(total_str)
                invoice_data['currency'] = currency_symbol
                break
            except (ValueError, IndexError):
                continue
    
    # Extract line items 
    # Look for patterns like those in the sample invoice
    item_pattern = r'(\d+)\s+(.*?)\s+(\d+)\s+(\d+[.,]\d+)(?:\s+(\d+[.,]\d+))?\s+(\d+[.,]\d+)'
    item_matches = re.finditer(item_pattern, text)
    
    for match in item_matches:
        try:
            item_num, description, quantity, price, vat_rate, total = match.groups()
            
            # In PDFs, Column A = Scientific Name, Description = Name, PRICE = Selling Price
            description = description.strip()
            
            # The field that comes before description is typically the scientific name (Column A in Excel)
            scientific_name = None
            name = description
            
            # Try to extract scientific name if present
            # Format often looks like: "Carissa macrocarpa Emerald Blanket"
            # where "Carissa macrocarpa" is the scientific name and "Emerald Blanket" is the product name
            sci_name_match = re.search(r'^([A-Z][a-z]+ [a-z]+)(?:\s+(.+))?$', description)
            if sci_name_match:
                scientific_name = sci_name_match.group(1)
                # If we have a product name after the scientific name, use that as the description
                if sci_name_match.group(2):
                    name = sci_name_match.group(2).strip()
            
            # Update description to be just the product name
            description = name
            
            # Try to extract pot size if present (often with L for liters)
            pot_size = None
            pot_match = re.search(r'(\d+L|\d+\s*L)', description)
            if pot_match:
                pot_size = pot_match.group(1)
            
            # Handle VAT rate (might be percentage or amount)
            vat_value = 0
            vat_percentage = None
            
            # First convert values to numbers so we can calculate VAT properly
            try:
                quantity = float(quantity)
                price = float(price.replace(',', '.'))
                total = float(total.replace(',', '.'))
            except ValueError:
                continue
                
            if vat_rate:
                try:
                    vat_rate_value = float(vat_rate.replace(',', '.'))
                    
                    # Detect if value is percentage or amount
                    if vat_rate_value < 50:  # Likely a percentage if less than 50
                        vat_percentage = vat_rate_value
                        # Calculate VAT amount based on price and quantity
                        vat_value = (price * quantity * vat_percentage) / 100
                    else:
                        # It's a direct VAT amount
                        vat_value = vat_rate_value
                except ValueError:
                    pass
            
            # Values already converted above, no need to convert again
            
            # Add to items list with improved VAT handling
            invoice_data['items'].append({
                'description': description,
                'scientific_name': scientific_name,
                'pot_size': pot_size,
                'quantity': quantity,
                'price': price,
                'vat': vat_value,
                'vat_percentage': vat_percentage,
                'total': total
            })
        except Exception as e:
            logging.warning(f"Error parsing invoice line item: {str(e)}")
    
    # If no items found with detailed pattern, try simpler approach
    if not invoice_data['items']:
        lines = text.split('\n')
        item_mode = False
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
            
            # Look for table headers that might indicate the start of item listing
            if re.search(r'(DESCRIPTION|QTY|PRICE|description|product|service|qty|quantity|price|amount|total)', line, re.IGNORECASE) and not item_mode:
                item_mode = True
                continue
            
            if item_mode:
                # If line contains price-like pattern, it might be an item line
                price_match = re.search(r'(\d+[.,]\d+)', line)
                if price_match and not re.search(r'(subtotal|tax|vat|total|balance|discount)', line, re.IGNORECASE):
                    # Try to extract item details
                    parts = re.split(r'\s{2,}', line)
                    
                    if len(parts) >= 2:
                        description = parts[0].strip()
                        # Try to extract price and quantity
                        numbers = [float(num.replace(',', '.')) for num in re.findall(r'(\d+[.,]\d+)', line)]
                        
                        if len(numbers) >= 2:
                            quantity = numbers[0] if numbers[0] < 100 else 1.0  # Assume first small number is quantity
                            price = numbers[1] if len(numbers) > 1 else numbers[0]
                            total = numbers[-1] if len(numbers) > 2 else quantity * price
                            
                            # Add item to the list
                            invoice_data['items'].append({
                                'description': description,
                                'scientific_name': extract_scientific_name(description),
                                'pot_size': extract_pot_size(description),
                                'quantity': quantity,
                                'price': price,
                                'vat': None,
                                'vat_percentage': None,
                                'total': total
                            })
                
                # If we encounter a line that might indicate the end of items section
                if re.search(r'(subtotal|tax|vat|total|balance|discount)', line, re.IGNORECASE):
                    item_mode = False
    
    logging.debug(f"Extracted invoice data: {invoice_data}")
    return invoice_data
