"""
Supplier product duplicate detection utility.

This module provides functionality to detect potential duplicate supplier products
using fuzzy matching of names and other product attributes.
"""
import os
from difflib import SequenceMatcher
from datetime import datetime
from typing import List, Tuple, Dict, Any
from openai import OpenAI

from app import db
from models import SupplierProduct, Supplier
from utils.logger import logger
from utils.db_utils import with_db_reconnect

# Threshold for string similarity to be considered a duplicate (0-1)
# Higher values mean stricter matching
DEFAULT_SIMILARITY_THRESHOLD = 0.9


def is_text_similar(a: str, b: str, threshold: float = DEFAULT_SIMILARITY_THRESHOLD) -> bool:
    """
    Check if two strings are similar based on sequence matching.
    
    Args:
        a: First string
        b: Second string
        threshold: Similarity threshold (0-1)
        
    Returns:
        bool: True if strings are similar, False otherwise
    """
    if not a or not b:
        return False
        
    # Convert to lowercase for case-insensitive comparison
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= threshold


def find_duplicate_products(products: List[SupplierProduct], 
                            threshold: float = DEFAULT_SIMILARITY_THRESHOLD) -> List[Tuple[SupplierProduct, SupplierProduct]]:
    """
    Find potential duplicate products in a list of supplier products.
    
    Args:
        products: List of SupplierProduct objects to check
        threshold: Similarity threshold for name matching (0-1)
        
    Returns:
        list: List of tuples containing pairs of duplicate products
    """
    if not products or len(products) < 2:
        return []
        
    duplicates = []
    seen_pairs = set()
    
    # For each product, compare with all other products
    for i, prod1 in enumerate(products):
        for j, prod2 in enumerate(products[i+1:], i+1):
            # Skip if already seen this pair or products from different suppliers
            pair_key = tuple(sorted([prod1.id, prod2.id]))
            if pair_key in seen_pairs or prod1.supplier_id != prod2.supplier_id:
                continue
                
            # Check for similarity in product names
            if is_text_similar(prod1.product_name, prod2.product_name, threshold):
                duplicates.append((prod1, prod2))
                seen_pairs.add(pair_key)
                continue
                
            # If both have scientific names, check those too
            if prod1.scientific_name and prod2.scientific_name and \
               is_text_similar(prod1.scientific_name, prod2.scientific_name, threshold):
                # If pot sizes are the same or similar
                if (not prod1.pot_size or not prod2.pot_size or 
                    is_text_similar(prod1.pot_size, prod2.pot_size, 0.8)):
                    duplicates.append((prod1, prod2))
                    seen_pairs.add(pair_key)
                    continue
                    
            # Check for very similar pricing as an additional signal (if both price and cost are similar)
            if prod1.price and prod2.price:
                price_diff = abs(prod1.price - prod2.price)
                price_threshold = min(prod1.price, prod2.price) * 0.05  # 5% difference threshold
                
                # If prices are very close
                if price_diff <= price_threshold:
                    # And if both have cost prices and they're also similar
                    if prod1.cost_price and prod2.cost_price:
                        cost_diff = abs(prod1.cost_price - prod2.cost_price)
                        cost_threshold = min(prod1.cost_price, prod2.cost_price) * 0.05
                        
                        if cost_diff <= cost_threshold:
                            # Only add if there's at least some name similarity
                            if SequenceMatcher(None, prod1.product_name.lower(), prod2.product_name.lower()).ratio() >= 0.5:
                                duplicates.append((prod1, prod2))
                                seen_pairs.add(pair_key)
    
    return duplicates


def find_supplier_duplicates(supplier_id = None, 
                             threshold: float = DEFAULT_SIMILARITY_THRESHOLD) -> List[Tuple[SupplierProduct, SupplierProduct]]:
    """
    Find potential duplicate products for a specific supplier or all suppliers.
    
    Args:
        supplier_id: Supplier ID to check, or None for all suppliers
        threshold: Similarity threshold for matching (0-1)
        
    Returns:
        list: List of tuples containing pairs of duplicate products
    """
    # Start with a base query
    query = SupplierProduct.query
    
    # Filter by supplier if specified
    if supplier_id:
        try:
            supplier_id = int(supplier_id)
            query = query.filter(SupplierProduct.supplier_id == supplier_id)
        except (ValueError, TypeError):
            logger.warning(f"Invalid supplier_id in find_supplier_duplicates: {supplier_id}")
            return []
    
    # Get all products for the specified supplier(s)
    products = query.all()
    
    # Process by supplier to avoid cross-supplier comparisons
    if supplier_id is not None:
        # If a specific supplier was requested, just process those products
        return find_duplicate_products(products, threshold)
    else:
        # Group by supplier_id and process each group
        duplicates = []
        products_by_supplier = {}
        
        # Group products by supplier
        for product in products:
            if product.supplier_id not in products_by_supplier:
                products_by_supplier[product.supplier_id] = []
            products_by_supplier[product.supplier_id].append(product)
        
        # Process each supplier's products separately
        for supplier_id, supplier_products in products_by_supplier.items():
            duplicates.extend(find_duplicate_products(supplier_products, threshold))
        
        return duplicates


def ask_openai_for_resolution(duplicate_pairs: List[Tuple[SupplierProduct, SupplierProduct]]) -> List[Dict[str, Any]]:
    """
    Ask OpenAI to analyze potential duplicate products and suggest resolutions.
    
    Args:
        duplicate_pairs: List of tuples with potential duplicate products
        
    Returns:
        list: List of dictionaries with analysis and suggestions
    """
    if not duplicate_pairs:
        return []
        
    # Check if OpenAI API key is configured
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OpenAI API key not found. Cannot perform AI analysis.")
        return [{"pair": (p1.id, p2.id), 
                 "suggestion": "Could not analyze - OpenAI API key not configured",
                 "is_duplicate": None} 
                for p1, p2 in duplicate_pairs]
    
    try:
        # Initialize the OpenAI client with some error handling
        client = OpenAI(api_key=api_key, timeout=60.0)
        
        # Test the API connection
        model_list = client.models.list()
        logger.info(f"Successfully connected to OpenAI API. Available models: {len(model_list.data)} models")
    except Exception as client_error:
        logger.error(f"Error initializing OpenAI client: {str(client_error)}")
        return [{"pair": (p1.id, p2.id), 
                 "suggestion": f"OpenAI API connection error: {str(client_error)}",
                 "is_duplicate": None} 
                for p1, p2 in duplicate_pairs]
    
    results = []
    
    for p1, p2 in duplicate_pairs:
        try:
            # Format the product information
            p1_info = f"ID: {p1.id}, Name: {p1.product_name}, Scientific: {p1.scientific_name or 'None'}, " \
                      f"Pot: {p1.pot_size or 'None'}, Height: {p1.height or 'None'}, " \
                      f"Price: {p1.price}, Cost: {p1.cost_price or 'Unknown'}"
            
            p2_info = f"ID: {p2.id}, Name: {p2.product_name}, Scientific: {p2.scientific_name or 'None'}, " \
                      f"Pot: {p2.pot_size or 'None'}, Height: {p2.height or 'None'}, " \
                      f"Price: {p2.price}, Cost: {p2.cost_price or 'Unknown'}"
            
            # Create the prompt
            prompt = f"""
            Analyze these two plant nursery products from supplier '{p1.supplier.name}' and determine if they're duplicates:
            
            Product 1: {p1_info}
            
            Product 2: {p2_info}
            
            Important context: Plant nurseries often create duplicate entries with slightly different names or details when receiving new inventory batches of the same plant. Look for these patterns:
            - Slight name variations (e.g., "Monstera deliciosa" vs "Monstera Deliciosa")
            - Same scientific name but slightly different common names
            - Same plant but different pot sizes (these should NOT be considered duplicates)
            - Same plant with slightly different pricing due to quality/size differences
            - Typographical errors in product names
            
            Provide your analysis:
            1. Are these products duplicates? (yes/no/maybe)
            2. Explanation: Why do you think they are or aren't duplicates?
            3. Recommended action: merge, keep both, or need more information
            4. If merging, which values to keep for each field (choose the more complete/accurate data)?
            """
            
            # Query OpenAI with fallback models
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Using a more widely available model
                    messages=[
                        {"role": "system", "content": "You are a plant nursery inventory specialist helping to detect duplicate products."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,  # Lower temperature for more consistent responses
                    max_tokens=500
                )
            except Exception as model_error:
                logger.error(f"Error with primary OpenAI model: {str(model_error)}")
                # Try with a simpler model as fallback
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=400
                )
            
            # Process response
            analysis = response.choices[0].message.content.strip()
            
            # Basic parsing to extract the duplicate status
            is_duplicate = None
            if "yes" in analysis.lower()[:50]:  # Check first part of response
                is_duplicate = True
            elif "no" in analysis.lower()[:50]:
                is_duplicate = False
            
            # Add result
            results.append({
                "pair": (p1.id, p2.id),
                "product1": p1,
                "product2": p2,
                "suggestion": analysis,
                "is_duplicate": is_duplicate
            })
            
        except Exception as e:
            logger.error(f"Error getting OpenAI analysis for products {p1.id} and {p2.id}: {str(e)}")
            results.append({
                "pair": (p1.id, p2.id),
                "product1": p1,
                "product2": p2,
                "suggestion": f"Error during analysis: {str(e)}",
                "is_duplicate": None
            })
    
    return results


@with_db_reconnect(max_retries=3)
def flag_duplicate_products(duplicates_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Flag products as duplicates in the database.
    
    Args:
        duplicates_data: List of dictionaries with duplicate pair information from session storage.
        
    Returns:
        dict: Result summary with success and error counts
    """
    if not duplicates_data:
        return {
            "success_count": 0,
            "error_count": 0,
            "message": "No duplicates to flag"
        }
    
    results = {
        "success_count": 0,
        "error_count": 0,
        "flagged_products": []
    }
    
    # Flag each duplicate pair
    for duplicate_data in duplicates_data:
        try:
            # For serialized data from session storage, we need to extract from the product dictionaries
            if 'product1' in duplicate_data and 'product2' in duplicate_data and isinstance(duplicate_data['product1'], dict):
                # We're dealing with serialized product data from session
                product1_id = duplicate_data['product1']['id']
                product2_id = duplicate_data['product2']['id']
            else:
                # Extract product IDs from the pair tuple
                product1_id, product2_id = duplicate_data["pair"]
            
            # Get the products
            product1 = SupplierProduct.query.get(product1_id)
            product2 = SupplierProduct.query.get(product2_id)
            
            if not product1 or not product2:
                results["error_count"] += 1
                logger.warning(f"Could not find products with IDs {product1_id} and/or {product2_id}")
                continue
            
            # Flag both products as being duplicates
            product1.flagged_duplicate = True
            product2.flagged_duplicate = True
            
            # If the analysis indicates this is a duplicate, mark it as such
            if duplicate_data.get('is_duplicate') == True:
                # Mark second product as duplicate of first
                # We're choosing product1 as the "canonical" version
                product2.is_duplicate = True 
                product2.duplicate_of_id = product1.id
                product2.duplicate_notes = f"Flagged as duplicate of {product1.product_name} by AI analysis"
                
                # Add the AI suggestion as a note
                if duplicate_data.get('suggestion'):
                    product2.notes = (product2.notes or '') + f"\n\nAI Duplicate Analysis:\n{duplicate_data['suggestion']}"
            
            # Add to results
            results["success_count"] += 2
            results["flagged_products"].extend([product1_id, product2_id])
            
        except Exception as e:
            results["error_count"] += 1
            logger.error(f"Error flagging duplicate products: {str(e)}")
    
    # Commit changes
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error committing duplicate flags: {str(e)}")
        results["error_count"] += results["success_count"]
        results["success_count"] = 0
        results["message"] = f"Database error: {str(e)}"
    
    return results