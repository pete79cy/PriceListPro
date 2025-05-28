"""
Invoice Addenda Blueprint

This module handles the creation and management of invoice addenda - 
supplementary sales documents that can be attached to invoices.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_login import login_required
from app import db
from models import InvoiceAddendum, InvoiceAddendumLine, Customer, Product
from datetime import datetime, date
from weasyprint import HTML
import logging

logger = logging.getLogger(__name__)

addenda_bp = Blueprint('addenda', __name__, url_prefix='/addenda')

@addenda_bp.route('/')
@login_required
def list_addenda():
    """List all invoice addenda"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    addenda = InvoiceAddendum.query.order_by(InvoiceAddendum.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('addenda/list.html', addenda=addenda)

@addenda_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_addendum():
    """Create a new invoice addendum"""
    if request.method == 'POST':
        try:
            customer_id = request.form.get('customer_id')
            invoice_number = request.form.get('invoice_number')
            period_from = datetime.strptime(request.form.get('period_from'), '%Y-%m-%d').date()
            period_to = datetime.strptime(request.form.get('period_to'), '%Y-%m-%d').date()
            notes = request.form.get('notes', '')
            
            # Validation
            if not customer_id or not invoice_number or not period_from or not period_to:
                flash('Please fill in all required fields', 'danger')
                return redirect(request.url)
            
            if period_from > period_to:
                flash('Start date cannot be after end date', 'danger')
                return redirect(request.url)
            
            # Create new addendum
            addendum = InvoiceAddendum(
                customer_id=customer_id,
                invoice_number=invoice_number,
                period_from=period_from,
                period_to=period_to,
                notes=notes
            )
            
            db.session.add(addendum)
            db.session.commit()
            
            flash(f'Invoice addendum for {invoice_number} created successfully!', 'success')
            return redirect(url_for('addenda.view_addendum', addendum_id=addendum.id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating addendum: {str(e)}")
            flash('Error creating addendum. Please try again.', 'danger')
    
    # Get customers for dropdown
    customers = Customer.query.order_by(Customer.name).all()
    return render_template('addenda/new.html', customers=customers)

@addenda_bp.route('/<uuid:addendum_id>')
@login_required
def view_addendum(addendum_id):
    """View a specific invoice addendum"""
    addendum = InvoiceAddendum.query.get_or_404(addendum_id)
    
    return render_template('addenda/view.html', addendum=addendum)

@addenda_bp.route('/<uuid:addendum_id>/lines', methods=['POST'])
@login_required
def add_line(addendum_id):
    """Add a new line to an addendum"""
    addendum = InvoiceAddendum.query.get_or_404(addendum_id)
    
    # Check if addendum is editable
    if addendum.status == 'locked':
        flash('Cannot modify a locked addendum', 'danger')
        return redirect(url_for('addenda.view_addendum', addendum_id=addendum_id))
    
    try:
        product_name = request.form.get('product_name', '').strip()
        product_category = request.form.get('product_category', '').strip()
        product_description = request.form.get('product_description', '').strip()
        sale_date = datetime.strptime(request.form.get('sale_date'), '%Y-%m-%d').date()
        quantity = float(request.form.get('quantity'))
        unit_price = float(request.form.get('unit_price'))
        vat_rate = float(request.form.get('vat_rate', 19.00))
        notes = request.form.get('notes', '')
        
        # Validation
        if not product_name or not sale_date or quantity <= 0 or unit_price <= 0:
            flash('Please fill in all required fields with valid values', 'danger')
            return redirect(url_for('addenda.view_addendum', addendum_id=addendum_id))
        
        # Check if sale date is within the addendum period
        if sale_date < addendum.period_from or sale_date > addendum.period_to:
            flash('Sale date must be within the addendum period', 'danger')
            return redirect(url_for('addenda.view_addendum', addendum_id=addendum_id))
        
        # Create new line
        line = InvoiceAddendumLine(
            addendum_id=addendum_id,
            product_name=product_name,
            product_category=product_category,
            product_description=product_description,
            sale_date=sale_date,
            quantity=quantity,
            unit_price=unit_price,
            vat_rate=vat_rate,
            notes=notes
        )
        
        db.session.add(line)
        db.session.commit()
        
        flash('Line added successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding line to addendum {addendum_id}: {str(e)}")
        flash('Error adding line. Please check your input and try again.', 'danger')
    
    return redirect(url_for('addenda.view_addendum', addendum_id=addendum_id))

@addenda_bp.route('/<uuid:addendum_id>/lines/<uuid:line_id>/delete', methods=['POST'])
@login_required
def delete_line(addendum_id, line_id):
    """Delete a line from an addendum"""
    addendum = InvoiceAddendum.query.get_or_404(addendum_id)
    line = InvoiceAddendumLine.query.get_or_404(line_id)
    
    # Check if addendum is editable
    if addendum.status == 'locked':
        flash('Cannot modify a locked addendum', 'danger')
        return redirect(url_for('addenda.view_addendum', addendum_id=addendum_id))
    
    # Check if line belongs to this addendum
    if line.addendum_id != addendum_id:
        flash('Invalid line for this addendum', 'danger')
        return redirect(url_for('addenda.view_addendum', addendum_id=addendum_id))
    
    try:
        db.session.delete(line)
        db.session.commit()
        flash('Line deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting line {line_id}: {str(e)}")
        flash('Error deleting line. Please try again.', 'danger')
    
    return redirect(url_for('addenda.view_addendum', addendum_id=addendum_id))

@addenda_bp.route('/<uuid:addendum_id>/lock', methods=['POST'])
@login_required
def lock_addendum(addendum_id):
    """Lock an addendum to prevent further modifications"""
    addendum = InvoiceAddendum.query.get_or_404(addendum_id)
    
    try:
        addendum.status = 'locked'
        addendum.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Addendum locked successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error locking addendum {addendum_id}: {str(e)}")
        flash('Error locking addendum. Please try again.', 'danger')
    
    return redirect(url_for('addenda.view_addendum', addendum_id=addendum_id))

@addenda_bp.route('/<uuid:addendum_id>/unlock', methods=['POST'])
@login_required
def unlock_addendum(addendum_id):
    """Unlock an addendum to allow modifications"""
    addendum = InvoiceAddendum.query.get_or_404(addendum_id)
    
    try:
        addendum.status = 'draft'
        addendum.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Addendum unlocked successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error unlocking addendum {addendum_id}: {str(e)}")
        flash('Error unlocking addendum. Please try again.', 'danger')
    
    return redirect(url_for('addenda.view_addendum', addendum_id=addendum_id))

@addenda_bp.route('/<uuid:addendum_id>/pdf')
@login_required
def export_pdf(addendum_id):
    """Export addendum as PDF"""
    addendum = InvoiceAddendum.query.get_or_404(addendum_id)
    
    try:
        # Render the HTML template
        html_content = render_template('pdf/addendum.html', addendum=addendum)
        
        # Generate PDF using WeasyPrint
        pdf = HTML(string=html_content, base_url=request.base_url).write_pdf()
        
        # Create filename
        filename = f"Addendum_{addendum.invoice_number}_{addendum.period_from}_{addendum.period_to}.pdf"
        
        return Response(
            pdf,
            headers={
                "Content-Type": "application/pdf",
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF for addendum {addendum_id}: {str(e)}")
        flash('Error generating PDF. Please try again.', 'danger')
        return redirect(url_for('addenda.view_addendum', addendum_id=addendum_id))

# API endpoints for AJAX functionality
@addenda_bp.route('/api/<uuid:addendum_id>')
@login_required
def api_get_addendum(addendum_id):
    """Get addendum data as JSON"""
    addendum = InvoiceAddendum.query.get_or_404(addendum_id)
    
    return jsonify({
        'id': str(addendum.id),
        'customer_name': addendum.customer.name,
        'invoice_number': addendum.invoice_number,
        'period_from': addendum.period_from.isoformat(),
        'period_to': addendum.period_to.isoformat(),
        'status': addendum.status,
        'notes': addendum.notes,
        'total_amount': addendum.get_total_amount(),
        'total_vat': addendum.get_total_vat(),
        'grand_total': addendum.get_grand_total(),
        'lines': [{
            'id': str(line.id),
            'product_name': line.product_name,
            'sale_date': line.sale_date.isoformat(),
            'quantity': float(line.quantity),
            'unit_price': float(line.unit_price),
            'vat_rate': float(line.vat_rate),
            'line_total': line.get_line_total(),
            'vat_amount': line.get_vat_amount(),
            'total_with_vat': line.get_total_with_vat(),
            'notes': line.notes
        } for line in addendum.lines]
    })

@addenda_bp.route('/api/products/search')
@login_required
def api_search_products():
    """Search products for autocomplete"""
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])
    
    products = Product.query.filter(
        Product.name.ilike(f'%{query}%')
    ).limit(10).all()
    
    return jsonify([{
        'id': product.id,
        'name': product.name,
        'category': product.category,
        'scientific_name': product.scientific_name,
        'pot': product.pot
    } for product in products])