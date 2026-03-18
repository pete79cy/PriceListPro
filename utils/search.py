import logging
import datetime
from sqlalchemy import func, or_
from app import db
from models import Customer, Product, PriceList

_MIN_DATE = datetime.date.min

def search_price_list(query, customer_id=None):
    """
    Search for products and prices based on a text query.
    Can search for a specific customer or all products.
    
    Args:
        query (str): The search query
        customer_id (int, optional): The customer ID to search price lists for
        
    Returns:
        dict: Search results including products and their prices
    """
    if customer_id:
        logging.debug(f"Searching for '{query}' for customer ID {customer_id}")
    else:
        logging.debug(f"Searching for '{query}' for all customers")
    
    # Normalize query
    query = query.strip().lower()
    
    # Find products that match the query
    products = Product.query.filter(
        or_(
            func.lower(Product.name).contains(query),
            func.lower(Product.description).contains(query),
            func.lower(Product.sku).contains(query)
        )
    ).all()
    
    product_ids = [p.id for p in products]
    
    # Get price entries for these products
    if customer_id:
        # Search for specific customer
        price_entries = PriceList.query.filter(
            PriceList.product_id.in_(product_ids),
            PriceList.customer_id == customer_id
        ).all()
    else:
        # Search all price entries, but we'll show general product info
        price_entries = PriceList.query.filter(
            PriceList.product_id.in_(product_ids)
        ).all()
    
    # Group prices by product
    results = []
    for product in products:
        # Find all prices for this product
        prices = [pe for pe in price_entries if pe.product_id == product.id]
        
        if customer_id and prices:
            # Customer-specific search with pricing
            prices.sort(key=lambda p: p.effective_date if p.effective_date else _MIN_DATE, reverse=True)
            
            results.append({
                'product_id': product.id,
                'product_name': product.name,
                'sku': product.sku,
                'description': product.description,
                'current_price': prices[0].price,
                'customer_specific': True,
                'price_history': [{
                    'price': p.price,
                    'effective_date': p.effective_date.strftime('%Y-%m-%d') if p.effective_date else None,
                    'expiry_date': p.expiry_date.strftime('%Y-%m-%d') if p.expiry_date else None
                } for p in prices]
            })
        elif not customer_id:
            # General search - show product info regardless of pricing
            # Get the most recent price from any customer if available
            recent_price = None
            if prices:
                prices.sort(key=lambda p: p.effective_date if p.effective_date else _MIN_DATE, reverse=True)
                recent_price = prices[0].price
            
            results.append({
                'product_id': product.id,
                'product_name': product.name,
                'sku': product.sku,
                'description': product.description,
                'current_price': recent_price,
                'customer_specific': False,
                'price_note': 'General price - select a customer for specific pricing' if recent_price else 'No pricing available'
            })
    
    # Calculate relevance scores (simple implementation)
    for result in results:
        # Basic relevance score: exact matches get higher score
        relevance = 0
        product_name = result['product_name'].lower()
        
        # Exact match gets highest score
        if query == product_name:
            relevance = 10
        # Starts with query
        elif product_name.startswith(query):
            relevance = 8
        # Contains query as a word
        elif f" {query} " in f" {product_name} ":
            relevance = 6
        # Contains query anywhere
        elif query in product_name:
            relevance = 4
        # SKU match
        elif result['sku'] and query in result['sku'].lower():
            relevance = 5
        # Description match
        elif result['description'] and query in result['description'].lower():
            relevance = 3
        
        result['relevance'] = relevance
    
    # Sort by relevance
    results.sort(key=lambda r: r['relevance'], reverse=True)
    
    logging.debug(f"Search results: {len(results)} matching products")
    return {
        'query': query,
        'customer_id': customer_id,
        'results': results
    }
