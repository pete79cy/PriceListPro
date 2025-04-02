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
                page_text = pdf_reader.pages[page_num].extract_text()
                text += page_text
                logging.debug(f"PDF Page {page_num+1} content: {page_text[:200]}...")  # Log first 200 chars
                
        # Log the whole text for debugging
        logging.debug(f"Extracted full text from PDF (truncated): {text[:500]}...")
        if len(text) < 10:  # Very short text is suspicious
            logging.warning(f"Extracted text is unusually short: '{text}'. PDF might be image-based or corrupted.")
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
    currency_symbol = '€'  # Euro is the default currency
    total_patterns = [
        r'TOTAL\s*(?::|([€])|(EUR))?\s*(\d+[.,]\d+)',
        r'(?:Total|Amount Due|Grand Total|Sum)[:\s](?:([€])|(EUR))?\s*(\d+[.,]\d+)',
        r'([€])\s*(\d+[.,]\d+)'  # Euro currency pattern
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
                    currency_map = {'EUR': '€'}  # Euro only
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
    
    # First try to find any special format lines like "1Myrtus communis microphylla nanaΜερσινια Ψυντρόφυλλη 2L20 3.00 19.00 60.00"
    # This special pattern has A/A, plant name, and numbers all stuck together
    special_pattern = r'(\d+)([A-Z][a-z]+ [a-z]+ [a-z]+)([^0-9]*)\s*(\d+L?)\s*(\d+)\s+(\d+[.,]\d+)\s+(\d+[.,]\d+)\s+(\d+[.,]\d+)'
    special_matches = re.finditer(special_pattern, text)
    
    special_items_found = False
    for match in special_matches:
        try:
            # This captures the special pattern with Greek format: A/A, Latin name, Greek name, pot size, qty, price, VAT, total
            item_num, latin_name, greek_name, pot_size, quantity, price, vat, total = match.groups()
            
            logging.debug(f"Found special format item: {match.group(0)}")
            logging.debug(f"Item parts: A/A={item_num}, Latin={latin_name}, Greek={greek_name}, Pot={pot_size}, Qty={quantity}, Price={price}, VAT={vat}, Total={total}")
            
            # Extract scientific name and common name
            scientific_name = latin_name.strip()
            common_name = greek_name.strip()
            
            # Combine for description
            description = f"{scientific_name} {common_name}".strip()
            
            # Convert values to numbers
            try:
                quantity = float(quantity)
                price = float(price.replace(',', '.'))
                vat_value = float(vat.replace(',', '.'))
                total = float(total.replace(',', '.'))
                
                # Calculate VAT percentage
                subtotal = price * quantity
                if subtotal > 0:
                    vat_percentage = (vat_value / subtotal) * 100
                else:
                    vat_percentage = None
            except ValueError:
                logging.warning(f"Error converting numeric values for item: {description}")
                continue
            
            # Add to items list
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
            special_items_found = True
            
        except Exception as e:
            logging.warning(f"Error parsing special format invoice line item: {str(e)}")
    
    # If special items were found, skip the regular pattern (we've already processed them)
    if special_items_found:
        logging.info(f"Found {len(invoice_data['items'])} items using special Greek format pattern")
        return invoice_data
    
    # Extract line items using standard pattern
    # Look for patterns like those in the sample invoice
    item_pattern = r'(\d+)\s+(.*?)\s+(\d+)\s+(\d+[.,]\d+)(?:\s+(\d+[.,]\d+))?\s+(\d+[.,]\d+)'
    item_matches = re.finditer(item_pattern, text)
    
    for match in item_matches:
        try:
            item_num, description, quantity, price, vat_rate, total = match.groups()
            
            # Skip if this is the A/A field which is just a numbering field
            # Handle both Latin and Greek characters for A/A
            if (description.strip().upper() == 'A/A' or description.strip().upper() == 'Α/Α' or 
                description.strip().upper().startswith('A/A ') or description.strip().upper().startswith('Α/Α ')):
                continue
                
            # Thoroughly filter any A/A prefixes (handling both Latin and Greek characters)
            # A/A could appear as A/A or Α/Α (with Greek letters)
            if (re.search(r'\bA/A\b|\bA/A\s+|\bΑ/Α\b|\bΑ/Α\s+', description.upper()) or 
                description.upper().startswith('A/A') or description.upper().startswith('Α/Α')):
                # Remove A/A and any numbers that might follow it
                description = re.sub(r'^(?:A/A|Α/Α)\s*\d*\s*', '', description, flags=re.IGNORECASE)
                
            # Clean up any remaining A/A references    
            description = description.replace('(A/A)', '').replace('(Α/Α)', '')
                
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
    
    # If no items found with detailed pattern, try simpler approaches
    if not invoice_data['items']:
        logging.warning("No items found with detailed pattern. Trying simpler approaches...")
        lines = text.split('\n')
        item_mode = False
        
        # Log the content to help with debugging
        logging.debug(f"Text split into {len(lines)} lines for analysis")
        
        # First approach - Look for lines with table headers
        for i, line in enumerate(lines):
            # Skip empty lines
            if not line.strip():
                continue
            
            # Look for table headers that might indicate the start of item listing
            if re.search(r'(DESCRIPTION|QTY|PRICE|ITEM|PRODUCT|description|qty|price|item|product|amount|total)', line, re.IGNORECASE) and not item_mode:
                logging.debug(f"Found potential table header at line {i}: {line}")
                item_mode = True
                continue
            
            if item_mode:
                # If line contains price-like pattern, it might be an item line
                price_match = re.search(r'(\d+[.,]\d+)', line)
                if price_match and not re.search(r'(subtotal|tax|vat|total|balance|discount)', line, re.IGNORECASE):
                    logging.debug(f"Potential item line found: {line}")
                    # Try to extract item details
                    parts = re.split(r'\s{2,}', line)
                    
                    if len(parts) >= 2:
                        description = parts[0].strip()
                        
                        # Skip A/A field which is just a numbering field
                        if (description.upper() == 'A/A' or description.upper() == 'Α/Α' or 
                            description.upper().startswith('A/A ') or description.upper().startswith('Α/Α ')):
                            continue
                            
                        # Thoroughly filter any A/A prefixes (handling both Latin and Greek characters)
                        # A/A could appear as A/A or Α/Α (with Greek letters)
                        if (re.search(r'\bA/A\b|\bA/A\s+|\bΑ/Α\b|\bΑ/Α\s+', description.upper()) or 
                            description.upper().startswith('A/A') or description.upper().startswith('Α/Α')):
                            # Remove A/A and any numbers that might follow it, handling both Latin and Greek characters
                            description = re.sub(r'^(?:A/A|Α/Α)\s*\d*\s*', '', description, flags=re.IGNORECASE)
                            
                        # Clean up any remaining A/A references    
                        description = description.replace('(A/A)', '').replace('(Α/Α)', '')
                            
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
        
        # Second approach - More aggressive pattern matching if still no items
        if not invoice_data['items']:
            logging.warning("Still no items found. Trying more aggressive pattern matching...")
            
            # Any line with a plant name and at least one number might be an item
            plant_keywords = ['plant', 'tree', 'flower', 'bulb', 'shrub', 'herb', 'carissa', 'blanket', 'ficus', 'emerald']
            
            for line in lines:
                if not line.strip() or len(line.strip()) < 5:
                    continue
                    
                # Check if the line has both plant-related words and numbers
                contains_plant_term = any(keyword in line.lower() for keyword in plant_keywords)
                contains_numbers = re.search(r'\d+[.,]\d+', line)
                
                # Special case: If line is clearly a product description (capitalized words) with numbers
                looks_like_product = re.search(r'[A-Z][a-z]+ [a-z]+|[A-Z][a-z]+', line) and contains_numbers
                
                if (contains_plant_term or looks_like_product) and contains_numbers:
                    logging.debug(f"Found potential product line via keywords: {line}")
                    # Extract numbers for price/quantity
                    numbers = [float(num.replace(',', '.')) for num in re.findall(r'(\d+[.,]\d+)', line)]
                    
                    if numbers:
                        # Extract description - anything before the first number
                        number_positions = [line.find(match) for match in re.findall(r'\d+[.,]\d+', line)]
                        first_number_pos = min(number_positions) if number_positions else len(line)
                        description = line[:first_number_pos].strip()
                        
                        # Default values
                        quantity = 1.0
                        price = numbers[0] if numbers else 0.0
                        total = price * quantity
                        
                        # If we have multiple numbers, try to guess what they are
                        if len(numbers) >= 2:
                            # First number could be quantity if small
                            if numbers[0] < 100:
                                quantity = numbers[0]
                                price = numbers[1]
                            else:
                                # Otherwise first number is probably price
                                price = numbers[0]
                                
                            # Last number is likely the total
                            if len(numbers) >= 3:
                                total = numbers[-1]
                            else:
                                total = quantity * price
                        
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
        
        # Third approach - Even more basic extraction if still no items
        if not invoice_data['items']:
            logging.warning("Still no items found. Trying last resort extraction...")
            
            # Analyze the PDF structure to find potential product table
            for i, line in enumerate(lines):
                # Skip very short lines and lines without numbers
                if len(line.strip()) < 5 or not re.search(r'\d', line):
                    continue
                
                # Skip lines that are clearly headers/footers
                if re.search(r'(invoice|page|date|number|total|subtotal)', line.lower()):
                    continue
                
                # If it has multiple words and at least one number, consider it a product
                words = line.split()
                if len(words) >= 3 and any(word.replace(',', '.').replace('.', '').isdigit() for word in words):
                    # Extract numbers
                    numbers = [float(num.replace(',', '.')) for num in re.findall(r'(\d+[.,]\d+)', line)]
                    
                    # Extract potential description - first half of the line
                    half_point = len(line) // 2
                    description = line[:half_point].strip()
                    
                    # Default values
                    quantity = 1.0
                    price = numbers[0] if numbers else 0.0
                    total = price
                    
                    if numbers:
                        # Add guessed item
                        invoice_data['items'].append({
                            'description': description,
                            'scientific_name': None,
                            'pot_size': None,
                            'quantity': quantity,
                            'price': price,
                            'vat': None,
                            'vat_percentage': None,
                            'total': total
                        })
                        logging.debug(f"Added last-resort item: {description}")
                        
            # Log the result of our extraction attempts
            if not invoice_data['items']:
                logging.error("Failed to extract any items after all approaches.")
            else:
                logging.info(f"Extracted {len(invoice_data['items'])} items with last-resort approach.")
    
    logging.debug(f"Extracted invoice data: {invoice_data}")
    return invoice_data
