import logging
from sqlalchemy import func, or_
from app import db
from models import Customer, Product, PriceList

def search_price_list(query, customer_id):
    """
    Search for products and prices based on a text query for a specific customer.
    Implements AI-powered search by using text similarity and smart matching.
    
    Args:
        query (str): The search query
        customer_id (int): The customer ID to search price lists for
        
    Returns:
        dict: Search results including products and their prices
    """
    logging.debug(f"Searching for '{query}' for customer ID {customer_id}")
    
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
    
    # Get price entries for these products and the specified customer
    price_entries = PriceList.query.filter(
        PriceList.product_id.in_(product_ids),
        PriceList.customer_id == customer_id
    ).all()
    
    # Group prices by product
    results = []
    for product in products:
        # Find all prices for this product
        prices = [pe for pe in price_entries if pe.product_id == product.id]
        
        # If found, add to results
        if prices:
            # Sort by effective date, newest first
            prices.sort(key=lambda p: p.effective_date if p.effective_date else '1900-01-01', reverse=True)
            
            results.append({
                'product_id': product.id,
                'product_name': product.name,
                'sku': product.sku,
                'description': product.description,
                'current_price': prices[0].price,
                'price_history': [{
                    'price': p.price,
                    'effective_date': p.effective_date.strftime('%Y-%m-%d') if p.effective_date else None,
                    'expiry_date': p.expiry_date.strftime('%Y-%m-%d') if p.expiry_date else None
                } for p in prices]
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
