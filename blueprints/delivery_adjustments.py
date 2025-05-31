"""
Delivery Adjustments Blueprint

This module handles product returns, additional deliveries, and replacements
after the initial order delivery, along with final proforma invoice generation.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required
from app import db
from models import (Order, Quotation, DeliveryAdjustment, DeliveryAdjustmentItem, 
                   DeliveryAdjustmentType, FinalProformaInvoice, Product, OrderItem, QuotationItem)
from datetime import datetime, date
import logging

# Create the blueprint
delivery_adjustments = Blueprint('delivery_adjustments', __name__, url_prefix='/delivery-adjustments')

@delivery_adjustments.route('/')
@login_required
def index():
    """List all delivery adjustments"""
    adjustments = DeliveryAdjustment.query.order_by(DeliveryAdjustment.created_at.desc()).all()
    return render_template('delivery_adjustments/index.html', adjustments=adjustments)

@delivery_adjustments.route('/order/<int:order_id>')
@login_required
def view_order_adjustments(order_id):
    """View all adjustments for a specific order"""
    order = Order.query.get_or_404(order_id)
    return render_template('delivery_adjustments/order_adjustments.html', order=order)

@delivery_adjustments.route('/new/order/<int:order_id>')
@login_required
def new_order_adjustment(order_id):
    """Create a new delivery adjustment for an order"""
    order = Order.query.get_or_404(order_id)
    
    # Check if order is delivered
    if order.status != 'delivered':
        flash('Can only create adjustments for delivered orders', 'warning')
        return redirect(url_for('orders.view_order', order_id=order_id))
    
    return render_template('delivery_adjustments/new.html', document=order, document_type='order',
                         adjustment_types=DeliveryAdjustmentType)

@delivery_adjustments.route('/new/quotation/<int:quotation_id>')
@login_required
def new_quotation_adjustment(quotation_id):
    """Create a new delivery adjustment for a quotation"""
    quotation = Quotation.query.get_or_404(quotation_id)
    
    # Check if quotation is completed/delivered
    if quotation.status not in ['COMPLETED', 'ACCEPTED']:
        flash('Can only create adjustments for completed quotations', 'warning')
        return redirect(url_for('quotation.view_quotation', quotation_id=quotation_id))
    
    return render_template('delivery_adjustments/new.html', document=quotation, document_type='quotation',
                         adjustment_types=DeliveryAdjustmentType)

@delivery_adjustments.route('/create/order/<int:order_id>', methods=['POST'])
@login_required
def create_order_adjustment(order_id):
    """Create a new delivery adjustment for an order"""
    order = Order.query.get_or_404(order_id)
    
    try:
        # Get form data
        adjustment_type = request.form.get('adjustment_type')
        reason = request.form.get('reason', '').strip()
        notes = request.form.get('notes', '').strip()
        
        # Validate adjustment type
        if adjustment_type not in [DeliveryAdjustmentType.RETURN, 
                                 DeliveryAdjustmentType.ADDITIONAL, 
                                 DeliveryAdjustmentType.REPLACEMENT]:
            flash('Invalid adjustment type', 'danger')
            return redirect(url_for('delivery_adjustments.new_order_adjustment', order_id=order_id))
        
        # Generate adjustment number
        adjustment_number = DeliveryAdjustment.generate_adjustment_number(adjustment_type)
        
        # Create the adjustment
        adjustment = DeliveryAdjustment(
            order_id=order_id,
            adjustment_type=adjustment_type,
            adjustment_number=adjustment_number,
            reason=reason,
            notes=notes
        )
        
        db.session.add(adjustment)
        db.session.commit()
        
        flash(f'Delivery adjustment {adjustment_number} created successfully', 'success')
        return redirect(url_for('delivery_adjustments.edit_adjustment', adjustment_id=adjustment.id))
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating delivery adjustment: {e}")
        flash('Error creating delivery adjustment', 'danger')
        return redirect(url_for('delivery_adjustments.new_order_adjustment', order_id=order_id))

@delivery_adjustments.route('/create/quotation/<int:quotation_id>', methods=['POST'])
@login_required
def create_quotation_adjustment(quotation_id):
    """Create a new delivery adjustment for a quotation"""
    quotation = Quotation.query.get_or_404(quotation_id)
    
    try:
        # Get form data
        adjustment_type = request.form.get('adjustment_type')
        reason = request.form.get('reason', '').strip()
        notes = request.form.get('notes', '').strip()
        
        # Validate adjustment type
        if adjustment_type not in [DeliveryAdjustmentType.RETURN, 
                                 DeliveryAdjustmentType.ADDITIONAL, 
                                 DeliveryAdjustmentType.REPLACEMENT]:
            flash('Invalid adjustment type', 'danger')
            return redirect(url_for('delivery_adjustments.new_quotation_adjustment', quotation_id=quotation_id))
        
        # Generate adjustment number
        adjustment_number = DeliveryAdjustment.generate_adjustment_number(adjustment_type)
        
        # Create the adjustment
        adjustment = DeliveryAdjustment(
            quotation_id=quotation_id,
            adjustment_type=adjustment_type,
            adjustment_number=adjustment_number,
            reason=reason,
            notes=notes
        )
        
        db.session.add(adjustment)
        db.session.commit()
        
        flash(f'Delivery adjustment {adjustment_number} created successfully', 'success')
        return redirect(url_for('delivery_adjustments.edit_adjustment', adjustment_id=adjustment.id))
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating delivery adjustment: {e}")
        flash('Error creating delivery adjustment', 'danger')
        return redirect(url_for('delivery_adjustments.new_quotation_adjustment', quotation_id=quotation_id))

@delivery_adjustments.route('/<int:adjustment_id>')
@login_required
def view_adjustment(adjustment_id):
    """View a specific delivery adjustment"""
    adjustment = DeliveryAdjustment.query.get_or_404(adjustment_id)
    return render_template('delivery_adjustments/view.html', adjustment=adjustment)

@delivery_adjustments.route('/<int:adjustment_id>/edit')
@login_required
def edit_adjustment(adjustment_id):
    """Edit a delivery adjustment"""
    adjustment = DeliveryAdjustment.query.get_or_404(adjustment_id)
    
    # Can only edit pending adjustments
    if adjustment.status != 'pending':
        flash('Can only edit pending adjustments', 'warning')
        return redirect(url_for('delivery_adjustments.view_adjustment', adjustment_id=adjustment_id))
    
    return render_template('delivery_adjustments/edit.html', adjustment=adjustment)

@delivery_adjustments.route('/<int:adjustment_id>/add-item', methods=['POST'])
@login_required
def add_item(adjustment_id):
    """Add an item to a delivery adjustment"""
    adjustment = DeliveryAdjustment.query.get_or_404(adjustment_id)
    
    if adjustment.status != 'pending':
        flash('Can only add items to pending adjustments', 'warning')
        return redirect(url_for('delivery_adjustments.view_adjustment', adjustment_id=adjustment_id))
    
    try:
        # Get form data
        plant_name = request.form.get('plant_name', '').strip()
        size = request.form.get('size', '').strip()
        quantity = float(request.form.get('quantity', 0))
        unit_price = float(request.form.get('unit_price', 0))
        vat_rate = float(request.form.get('vat_rate', 19.0))
        reason = request.form.get('reason', '').strip()
        order_item_id = request.form.get('order_item_id') or None
        
        # Validation
        if not plant_name or quantity <= 0 or unit_price < 0:
            flash('Plant name, quantity, and unit price are required', 'danger')
            return redirect(url_for('delivery_adjustments.edit_adjustment', adjustment_id=adjustment_id))
        
        # Create adjustment item
        item = DeliveryAdjustmentItem(
            adjustment_id=adjustment_id,
            order_item_id=int(order_item_id) if order_item_id else None,
            plant_name=plant_name,
            size=size,
            quantity=quantity,
            unit_price=unit_price,
            vat_rate=vat_rate,
            reason=reason
        )
        
        db.session.add(item)
        db.session.commit()
        
        flash('Item added successfully', 'success')
        
    except ValueError:
        flash('Invalid quantity or price values', 'danger')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding adjustment item: {e}")
        flash('Error adding item', 'danger')
    
    return redirect(url_for('delivery_adjustments.edit_adjustment', adjustment_id=adjustment_id))

@delivery_adjustments.route('/<int:adjustment_id>/remove-item/<int:item_id>', methods=['POST'])
@login_required
def remove_item(adjustment_id, item_id):
    """Remove an item from a delivery adjustment"""
    adjustment = DeliveryAdjustment.query.get_or_404(adjustment_id)
    item = DeliveryAdjustmentItem.query.filter_by(id=item_id, adjustment_id=adjustment_id).first_or_404()
    
    if adjustment.status != 'pending':
        flash('Can only remove items from pending adjustments', 'warning')
        return redirect(url_for('delivery_adjustments.view_adjustment', adjustment_id=adjustment_id))
    
    try:
        db.session.delete(item)
        db.session.commit()
        flash('Item removed successfully', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error removing adjustment item: {e}")
        flash('Error removing item', 'danger')
    
    return redirect(url_for('delivery_adjustments.edit_adjustment', adjustment_id=adjustment_id))

@delivery_adjustments.route('/<int:adjustment_id>/confirm', methods=['POST'])
@login_required
def confirm_adjustment(adjustment_id):
    """Confirm a delivery adjustment"""
    adjustment = DeliveryAdjustment.query.get_or_404(adjustment_id)
    
    if adjustment.status != 'pending':
        flash('Adjustment is not in pending status', 'warning')
        return redirect(url_for('delivery_adjustments.view_adjustment', adjustment_id=adjustment_id))
    
    if not adjustment.items:
        flash('Cannot confirm adjustment without items', 'warning')
        return redirect(url_for('delivery_adjustments.edit_adjustment', adjustment_id=adjustment_id))
    
    try:
        adjustment.status = 'confirmed'
        adjustment.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash(f'Delivery adjustment {adjustment.adjustment_number} confirmed', 'success')
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error confirming adjustment: {e}")
        flash('Error confirming adjustment', 'danger')
    
    return redirect(url_for('delivery_adjustments.view_adjustment', adjustment_id=adjustment_id))

@delivery_adjustments.route('/final-invoice/<int:order_id>')
@login_required
def view_final_invoice(order_id):
    """View or create final proforma invoice for an order"""
    order = Order.query.get_or_404(order_id)
    
    # Check if final invoice already exists
    final_invoice = FinalProformaInvoice.query.filter_by(order_id=order_id).first()
    
    if not final_invoice:
        # Check if there are any confirmed adjustments
        confirmed_adjustments = [adj for adj in order.delivery_adjustments if adj.status == 'confirmed']
        
        if not confirmed_adjustments and order.status == 'delivered':
            # No adjustments, just use original proforma
            flash('No delivery adjustments found. Use original proforma invoice.', 'info')
            return redirect(url_for('orders.view_order', order_id=order_id))
        
        return render_template('delivery_adjustments/create_final_invoice.html', 
                             order=order, confirmed_adjustments=confirmed_adjustments)
    
    return render_template('delivery_adjustments/final_invoice.html', 
                         order=order, final_invoice=final_invoice)

@delivery_adjustments.route('/create-final-invoice/<int:order_id>', methods=['POST'])
@login_required
def create_final_invoice(order_id):
    """Create final proforma invoice"""
    order = Order.query.get_or_404(order_id)
    
    # Check if final invoice already exists
    existing_invoice = FinalProformaInvoice.query.filter_by(order_id=order_id).first()
    if existing_invoice:
        flash('Final proforma invoice already exists for this order', 'warning')
        return redirect(url_for('delivery_adjustments.view_final_invoice', order_id=order_id))
    
    try:
        # Generate invoice number
        invoice_number = FinalProformaInvoice.generate_invoice_number()
        
        # Create final invoice
        final_invoice = FinalProformaInvoice(
            order_id=order_id,
            invoice_number=invoice_number,
            notes=request.form.get('notes', '').strip()
        )
        
        # Calculate totals
        final_invoice.calculate_totals()
        
        db.session.add(final_invoice)
        db.session.commit()
        
        flash(f'Final proforma invoice {invoice_number} created successfully', 'success')
        return redirect(url_for('delivery_adjustments.view_final_invoice', order_id=order_id))
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating final invoice: {e}")
        flash('Error creating final proforma invoice', 'danger')
        return redirect(url_for('delivery_adjustments.view_final_invoice', order_id=order_id))

@delivery_adjustments.route('/api/order-items/<int:order_id>')
@login_required
def api_get_order_items(order_id):
    """Get order items for autocomplete in adjustments"""
    order = Order.query.get_or_404(order_id)
    items = []
    
    for item in order.items:
        items.append({
            'id': item.id,
            'plant_name': item.plant_name,
            'size': item.size or '',
            'quantity': item.quantity,
            'price': item.price,
            'vat_rate': item.vat_rate
        })
    
    return jsonify(items)