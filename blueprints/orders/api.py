"""
API routes for daily orders management
Provides smart product search, pricing, and order item management
"""

from flask import jsonify, request
from replit_auth import require_login
from sqlalchemy import or_, and_
from datetime import datetime, date

from . import orders
from models import db, Product, Customer, PriceList, OrderItem, Order, SupplierProduct
from .routes import get_customer_price, update_customer_price_list


@orders.route('/api/search/products')
@require_login
def api_search_products():
    """Optimized product search with efficient database queries"""
    query = request.args.get('q', '').strip()
    customer_id = request.args.get('customer_id', type=int)
    limit = request.args.get('limit', 20, type=int)
    
    if not query or len(query) < 2:
        return jsonify([])
    
    # Use a single optimized query with LEFT JOIN for price list data
    from sqlalchemy.orm import aliased
    
    # Create alias for PriceList to enable LEFT JOIN
    price_list_alias = aliased(PriceList)
    
    # Optimized search with single query and JOIN
    search_filter = or_(
        Product.name.ilike(f'%{query}%'),
        Product.scientific_name.ilike(f'%{query}%'),
        Product.category.ilike(f'%{query}%'),
        Product.sku.ilike(f'%{query}%')
    )
    
    # Single query with LEFT JOIN to get products and their price list entries
    if customer_id:
        product_query = db.session.query(
            Product,
            price_list_alias.id.label('price_list_id'),
            price_list_alias.price.label('customer_price')
        ).outerjoin(
            price_list_alias,
            and_(
                price_list_alias.product_id == Product.id,
                price_list_alias.customer_id == customer_id
            )
        ).filter(search_filter).limit(limit * 2)
    else:
        product_query = db.session.query(
            Product,
            db.literal_column("NULL").label('price_list_id'),
            db.literal_column("NULL").label('customer_price')
        ).filter(search_filter).limit(limit * 2)
    
    results = []
    
    # Process regular products efficiently
    for product, price_list_id, customer_price in product_query:
        # Use customer price if available, otherwise use default price from get_customer_price
        if customer_price is not None:
            price = customer_price
        else:
            price = get_customer_price(customer_id, product.id) if customer_id else 0.0
        
        results.append({
            'id': product.id,
            'name': product.name,
            'scientific_name': product.scientific_name or '',
            'category': product.category or '',
            'size': product.pot or '',  # Using 'size' instead of 'pot' for consistency
            'sku': product.sku or '',
            'description': product.description or '',
            'price': float(price),
            'price_formatted': f'€{price:.2f}',
            'has_customer_price': price_list_id is not None,
            'price_list_id': price_list_id,
            'vat_rate': 5.0,  # Default VAT rate for plants
            'type': 'product'
        })
    
    # Only search supplier products if we have fewer results than requested
    if len(results) < limit:
        remaining_limit = limit - len(results)
        
        # Efficient supplier product search with JOIN
        supplier_query = db.session.query(SupplierProduct).join(
            SupplierProduct.supplier, isouter=True
        ).filter(
            or_(
                SupplierProduct.product_name.ilike(f'%{query}%'),
                SupplierProduct.scientific_name.ilike(f'%{query}%')
            )
        ).limit(remaining_limit)
        
        # Get existing product names for deduplication
        existing_names = {r['name'].lower() for r in results}
        
        for supplier_product in supplier_query:
            # Skip if we already have this product
            if supplier_product.product_name.lower() in existing_names:
                continue
                
            results.append({
                'id': f'supplier_{supplier_product.id}',
                'name': supplier_product.product_name,
                'scientific_name': supplier_product.scientific_name or '',
                'category': 'Supplier Product',
                'size': supplier_product.pot_size or '',
                'sku': '',
                'description': f'From {supplier_product.supplier.name}' if supplier_product.supplier else '',
                'price': float(supplier_product.price or 0.0),
                'price_formatted': f'€{supplier_product.price:.2f}' if supplier_product.price else '€0.00',
                'has_customer_price': False,
                'price_list_id': None,
                'vat_rate': 5.0,  # Default VAT rate for plants
                'type': 'supplier_product',
                'supplier_id': supplier_product.supplier_id,
                'supplier_name': supplier_product.supplier.name if supplier_product.supplier else ''
            })
    
    # Optimized relevance sorting
    query_lower = query.lower()
    
    def relevance_score(item):
        name = item['name'].lower()
        
        if name == query_lower:
            return (0, name)  # Exact match
        elif name.startswith(query_lower):
            return (1, name)  # Starts with query
        elif query_lower in name:
            return (2, name)  # Contains query
        else:
            return (3, name)  # Other matches
    
    results.sort(key=relevance_score)
    
    return jsonify(results[:limit])


@orders.route('/api/products/<int:product_id>/price')
@require_login
def api_get_product_price():
    """Get product price for a specific customer"""
    product_id = request.args.get('product_id', type=int)
    customer_id = request.args.get('customer_id', type=int)
    
    if not product_id or not customer_id:
        return jsonify({'error': 'Missing product_id or customer_id'}), 400
    
    price = get_customer_price(customer_id, product_id)
    
    # Get price list entry details
    price_list_entry = PriceList.query.filter_by(
        customer_id=customer_id,
        product_id=product_id
    ).first()
    
    return jsonify({
        'price': price,
        'has_customer_price': price_list_entry is not None,
        'price_list_id': price_list_entry.id if price_list_entry else None,
        'last_updated': price_list_entry.updated_at.isoformat() if price_list_entry else None
    })


@orders.route('/api/price-list/update', methods=['POST'])
@require_login
def api_update_price_list():
    """Update customer price list entry"""
    data = request.get_json()
    
    customer_id = data.get('customer_id', type=int)
    product_id = data.get('product_id', type=int)
    price = data.get('price', type=float)
    
    if not all([customer_id, product_id, price is not None]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if price < 0:
        return jsonify({'error': 'Price cannot be negative'}), 400
    
    try:
        price_list_item = update_customer_price_list(customer_id, product_id, price)
        
        return jsonify({
            'success': True,
            'price_list_id': price_list_item.id,
            'price': price_list_item.price,
            'updated_at': price_list_item.updated_at.isoformat()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@orders.route('/api/orders/<int:order_id>/items', methods=['GET'])
@require_login
def api_get_order_items(order_id):
    """Get all items for a specific order"""
    order = Order.query.get_or_404(order_id)
    
    items = []
    for item in order.items:
        items.append({
            'id': item.id,
            'product_id': item.product_id,
            'price_list_id': item.price_list_id,
            'plant_name': item.plant_name,
            'size': item.size,
            'quantity': item.quantity,
            'price': item.price,
            'vat_rate': item.vat_rate,
            'total': item.get_total(),
            'vat_amount': item.get_vat_amount(),
            'notes': item.notes,
            'product_name': item.product.name if item.product else None,
            'has_price_list': item.price_list_id is not None
        })
    
    return jsonify({
        'order_id': order_id,
        'items': items,
        'total_items': len(items),
        'subtotal': sum(item['total'] for item in items),
        'total_vat': sum(item['vat_amount'] for item in items)
    })


@orders.route('/api/orders/<int:order_id>/items', methods=['POST'])
@require_login
def api_add_order_item(order_id):
    """Add a new item to an order"""
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['plant_name', 'quantity', 'price']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        # Create new order item
        item = OrderItem(
            order_id=order_id,
            product_id=data.get('product_id'),
            price_list_id=data.get('price_list_id'),
            plant_name=data['plant_name'],
            size=data.get('size', ''),
            quantity=int(data['quantity']),
            price=float(data['price']),
            vat_rate=float(data.get('vat_rate', 19.0)),
            notes=data.get('notes', '')
        )
        
        db.session.add(item)
        
        # Update customer price list if requested and product_id is provided
        if data.get('update_price_list', False) and item.product_id:
            update_customer_price_list(order.customer_id, item.product_id, item.price)
            item.updated_price_list = True
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'item': {
                'id': item.id,
                'plant_name': item.plant_name,
                'size': item.size,
                'quantity': item.quantity,
                'price': item.price,
                'vat_rate': item.vat_rate,
                'total': item.get_total(),
                'vat_amount': item.get_vat_amount(),
                'updated_price_list': item.updated_price_list
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@orders.route('/api/orders/<int:order_id>/items/<int:item_id>', methods=['PUT'])
@require_login
def api_update_order_item(order_id, item_id):
    """Update an existing order item"""
    order = Order.query.get_or_404(order_id)
    item = OrderItem.query.filter_by(id=item_id, order_id=order_id).first_or_404()
    
    data = request.get_json()
    
    try:
        # Update item fields
        if 'plant_name' in data:
            item.plant_name = data['plant_name']
        if 'size' in data:
            item.size = data['size']
        if 'quantity' in data:
            item.quantity = int(data['quantity'])
        if 'price' in data:
            old_price = item.price
            item.price = float(data['price'])
            
            # Update customer price list if requested and price changed
            if (data.get('update_price_list', False) and 
                item.product_id and 
                old_price != item.price):
                update_customer_price_list(order.customer_id, item.product_id, item.price)
                item.updated_price_list = True
                
        if 'vat_rate' in data:
            item.vat_rate = float(data['vat_rate'])
        if 'notes' in data:
            item.notes = data['notes']
        
        item.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'item': {
                'id': item.id,
                'plant_name': item.plant_name,
                'size': item.size,
                'quantity': item.quantity,
                'price': item.price,
                'vat_rate': item.vat_rate,
                'total': item.get_total(),
                'vat_amount': item.get_vat_amount(),
                'updated_price_list': item.updated_price_list
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@orders.route('/api/orders/<int:order_id>/items/<int:item_id>', methods=['DELETE'])
@require_login
def api_delete_order_item(order_id, item_id):
    """Delete an order item"""
    order = Order.query.get_or_404(order_id)
    item = OrderItem.query.filter_by(id=item_id, order_id=order_id).first_or_404()
    
    try:
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@orders.route('/api/vat/rates')
@require_login
def api_get_vat_rates():
    """Get available VAT rates"""
    return jsonify([
        {'rate': 5.0, 'label': '5% (Reduced Rate)', 'description': 'Plants and food products'},
        {'rate': 19.0, 'label': '19% (Standard Rate)', 'description': 'Standard goods and services'},
        {'rate': 0.0, 'label': '0% (Exempt)', 'description': 'Tax-exempt items'}
    ])


@orders.route('/api/price-list/<int:price_list_id>', methods=['PUT'])
@require_login
def api_update_price_list_entry(price_list_id):
    """Update an existing price list entry"""
    price_list_entry = PriceList.query.get_or_404(price_list_id)
    data = request.get_json()
    
    price = data.get('price', type=float)
    effective_date_str = data.get('effective_date')
    
    if price is None or price < 0:
        return jsonify({'error': 'Valid price is required'}), 400
    
    try:
        # Update the entry
        price_list_entry.price = price
        
        if effective_date_str:
            from datetime import datetime
            price_list_entry.effective_date = datetime.strptime(effective_date_str, '%Y-%m-%d').date()
        
        price_list_entry.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'price_list_id': price_list_entry.id,
            'price': price_list_entry.price,
            'updated_at': price_list_entry.updated_at.isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@orders.route('/api/price-list/<int:price_list_id>', methods=['DELETE'])
@require_login
def api_delete_price_list_entry(price_list_id):
    """Delete a price list entry"""
    price_list_entry = PriceList.query.get_or_404(price_list_id)
    
    try:
        db.session.delete(price_list_entry)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@orders.route('/api/customers/<int:customer_id>/price-list')
@require_login
def api_get_customer_price_list(customer_id):
    """Get all price list entries for a specific customer"""
    customer = Customer.query.get_or_404(customer_id)
    
    price_list_entries = PriceList.query.filter_by(customer_id=customer_id).join(Product).all()
    
    entries = []
    for entry in price_list_entries:
        entries.append({
            'id': entry.id,
            'product_id': entry.product_id,
            'product_name': entry.product.name,
            'scientific_name': entry.product.scientific_name or '',
            'category': entry.product.category or '',
            'price': entry.price,
            'effective_date': entry.effective_date.isoformat() if entry.effective_date else None,
            'updated_at': entry.updated_at.isoformat() if entry.updated_at else None
        })
    
    return jsonify({
        'customer_id': customer_id,
        'customer_name': customer.name,
        'entries': entries,
        'total_entries': len(entries)
    })