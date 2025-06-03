"""
API routes for daily orders management
Provides smart product search, pricing, and order item management
"""

from flask import jsonify, request
from flask_login import login_required
from sqlalchemy import or_, and_
from datetime import datetime, date

from . import orders
from models import db, Product, Customer, PriceList, OrderItem, Order, SupplierProduct
from .routes import get_customer_price, update_customer_price_list


@orders.route('/api/search/products')
@login_required
def api_search_products():
    """Smart product search with fuzzy matching and customer-specific pricing"""
    query = request.args.get('q', '').strip()
    customer_id = request.args.get('customer_id', type=int)
    limit = request.args.get('limit', 20, type=int)
    
    if not query or len(query) < 2:
        return jsonify([])
    
    # Search in multiple fields with fuzzy matching
    search_filter = or_(
        Product.name.ilike(f'%{query}%'),
        Product.scientific_name.ilike(f'%{query}%'),
        Product.category.ilike(f'%{query}%'),
        Product.description.ilike(f'%{query}%'),
        Product.sku.ilike(f'%{query}%')
    )
    
    products = Product.query.filter(search_filter).limit(limit).all()
    
    # Also search in supplier products for additional matches
    supplier_products = SupplierProduct.query.filter(
        or_(
            SupplierProduct.product_name.ilike(f'%{query}%'),
            SupplierProduct.scientific_name.ilike(f'%{query}%')
        )
    ).limit(limit).all()
    
    results = []
    
    # Add regular products
    for product in products:
        price = get_customer_price(customer_id, product.id) if customer_id else 0.0
        
        # Get customer-specific price list entry
        price_list_entry = None
        if customer_id:
            price_list_entry = PriceList.query.filter_by(
                customer_id=customer_id,
                product_id=product.id
            ).first()
        
        results.append({
            'id': product.id,
            'name': product.name,
            'scientific_name': product.scientific_name or '',
            'category': product.category or '',
            'pot': product.pot or '',
            'sku': product.sku or '',
            'description': product.description or '',
            'price': price,
            'has_customer_price': price_list_entry is not None,
            'price_list_id': price_list_entry.id if price_list_entry else None,
            'type': 'product'
        })
    
    # Add supplier products that don't match existing products
    for supplier_product in supplier_products:
        # Check if we already have this as a regular product
        existing = any(p['name'].lower() == supplier_product.product_name.lower() for p in results)
        if not existing:
            results.append({
                'id': f'supplier_{supplier_product.id}',
                'name': supplier_product.product_name,
                'scientific_name': supplier_product.scientific_name or '',
                'category': 'Supplier Product',
                'pot': supplier_product.pot_size or '',
                'sku': '',
                'description': f'From {supplier_product.supplier.name}' if supplier_product.supplier else '',
                'price': supplier_product.price,
                'has_customer_price': False,
                'price_list_id': None,
                'type': 'supplier_product',
                'supplier_id': supplier_product.supplier_id,
                'supplier_name': supplier_product.supplier.name if supplier_product.supplier else ''
            })
    
    # Sort results by relevance (exact matches first, then partial matches)
    def relevance_score(item):
        name = item['name'].lower()
        query_lower = query.lower()
        
        if name == query_lower:
            return 0  # Exact match
        elif name.startswith(query_lower):
            return 1  # Starts with query
        elif query_lower in name:
            return 2  # Contains query
        else:
            return 3  # Other matches
    
    results.sort(key=relevance_score)
    
    return jsonify(results[:limit])


@orders.route('/api/products/<int:product_id>/price')
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
def api_get_vat_rates():
    """Get available VAT rates"""
    return jsonify([
        {'rate': 5.0, 'label': '5% (Reduced Rate)', 'description': 'Plants and food products'},
        {'rate': 19.0, 'label': '19% (Standard Rate)', 'description': 'Standard goods and services'},
        {'rate': 0.0, 'label': '0% (Exempt)', 'description': 'Tax-exempt items'}
    ])