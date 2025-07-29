from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from models import Customer, CustomerCategory

customer_bp = Blueprint('customer_form', __name__, url_prefix='/customer_form')

@customer_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_customer():
    """Create a new customer with the provided information"""
    # Get all categories for the dropdown
    categories = CustomerCategory.query.order_by(CustomerCategory.name).all()
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        category_id = request.form.get('category_id')
        
        # Basic validation
        if not name:
            flash('Customer name is required', 'danger')
            return render_template('customer/create_customer.html', categories=categories)
        
        # Create new customer
        new_customer = Customer(
            name=name,
            email=email,
            phone=phone,
            address=address,
            category_id=category_id if category_id else None
        )
        
        db.session.add(new_customer)
        try:
            db.session.commit()
            flash('Customer created successfully!', 'success')
            return redirect(url_for('customers'))  # Redirect to customers list
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating customer: {str(e)}', 'danger')
    
    return render_template('customer/create_customer.html', categories=categories)