"""
Routes module for the Flask application.
"""

import logging
import os
import re
import uuid
import json
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify, session, send_file, send_from_directory, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app import app, db
from models import (
    User, FileUpload, PriceList, Invoice, Product, Customer, 
    Supplier, CustomerCategory, CustomerContact, Quotation, 
    QuotationItem, ProductUpdateRequest, CompanySettings
)
# Import statements removed for minimal test
# Import for duplicate detection intentionally removed

# Configure logger
logger = logging.getLogger(__name__)

def get_recent_activities(limit=10):
    """
    Get recent activities from various sources for dashboard display.
    
    Args:
        limit (int): Maximum number of activities to return
        
    Returns:
        list: List of activity dictionaries with timestamp, type, and details
    """
    activities = []
    
    try:
        # Get recent price lists
        price_lists = PriceList.query.order_by(PriceList.created_at.desc()).limit(5).all()
        for pl in price_lists:
            activities.append({
                'timestamp': pl.created_at,
                'type': 'price_list',
                'message': f'New price list created for {pl.customer.name if pl.customer else "Unknown"}',
                'link': url_for('view_price_list', price_list_id=pl.id)
            })
            
        # Get recent product updates
        updates = ProductUpdateRequest.query.order_by(ProductUpdateRequest.created_at.desc()).limit(5).all()
        for upd in updates:
            status_class = {
                'Pending': 'warning',
                'Approved': 'success',
                'Rejected': 'danger'
            }.get(upd.status, 'info')
            
            activities.append({
                'timestamp': upd.created_at,
                'type': 'product_update',
                'message': f'Product update request: {upd.product.name if upd.product else "Unknown"} ({upd.status})',
                'status': upd.status,
                'status_class': status_class,
                'link': url_for('product_updates')
            })
            
        # Get recent file uploads
        uploads = FileUpload.query.order_by(FileUpload.upload_date.desc()).limit(5).all()
        for upload in uploads:
            activities.append({
                'timestamp': upload.upload_date,
                'type': 'file_upload',
                'message': f'File uploaded: {upload.filename} for {upload.customer.name if upload.customer else "Unknown"}',
                'link': url_for('uploads')
            })
            
        # Get recent invoices
        invoices = Invoice.query.order_by(Invoice.created_at.desc()).limit(5).all()
        for invoice in invoices:
            activities.append({
                'timestamp': invoice.created_at,
                'type': 'invoice',
                'message': f'Invoice created: {invoice.invoice_number} for {invoice.customer.name if invoice.customer else "Unknown"}',
                'link': url_for('view_invoice', invoice_id=invoice.id)
            })
            
    except Exception as e:
        logger.error(f"Error getting activities: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        # Return an empty activities list as fallback
        return []
        
    # Sort all activities by timestamp (newest first) and limit the total
    try:
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        return activities[:limit]
    except Exception as e:
        logger.error(f"Error sorting activities: {str(e)}")
        # Return unsorted if there's a sorting error
        return activities

# Log that routes module was loaded
logger.info("Routes module loaded")

def register_routes(app):
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Helper function to check allowed file extensions
    def allowed_file(filename, extensions):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions
        
    # Context processor to add pending update count to all templates
    @app.context_processor
    def inject_pending_update_count():
        try:
            if current_user.is_authenticated:
                pending_count = ProductUpdateRequest.query.filter_by(status='Pending').count()
                return {
                    'pending_update_count': pending_count,
                    'has_pending_updates': pending_count > 0
                }
        except:
            # If there's any error (like with current_user not being available), return defaults
            pass
        return {
            'pending_update_count': 0,
            'has_pending_updates': False
        }
    
    @app.route('/', methods=['GET'])
    def index():
        # If user is already logged in, show the dashboard
        if current_user.is_authenticated:
            # Get some stats for the dashboard
            pending_update_count = ProductUpdateRequest.query.filter_by(status='Pending').count()
            
            # Get counts for the dashboard
            customer_count = Customer.query.count()
            product_count = Product.query.count()
            price_list_count = PriceList.query.count() 
            invoice_count = Invoice.query.count()
            
            # Build stats dictionary
            stats = {
                'customers': customer_count,
                'products': product_count,
                'price_lists': price_list_count,
                'invoices': invoice_count,
                'pending_updates': pending_update_count
            }
            
            # Dynamic card coloring based on thresholds
            card_classes = {
                'customers': 'bg-primary' if customer_count > 10 else 'bg-warning',
                'products': 'bg-success' if product_count > 20 else 'bg-info',
                'price_lists': 'bg-info' if price_list_count > 5 else 'bg-secondary',
                'invoices': 'bg-warning' if invoice_count > 0 else 'bg-light text-dark'
            }
            
            # Get recent activities for the dashboard
            recent_activities = get_recent_activities(limit=5)
            
            return render_template('dashboard_improved.html', 
                                  stats=stats,
                                  card_classes=card_classes,
                                  pending_update_count=pending_update_count,
                                  recent_activities=recent_activities)
        # Otherwise show the login page
        return render_template('index.html')
        
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # If user is already logged in, redirect to dashboard
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
            
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            # Validate the username and password
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                # Update last login timestamp
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                # Log the user in
                login_user(user)
                flash(f'Welcome back, {user.username}!', 'success')
                
                # Redirect to the page they were trying to access or the dashboard
                next_page = request.args.get('next')
                return redirect(next_page if next_page else url_for('dashboard'))
            else:
                flash('Invalid username or password. Please try again.', 'danger')
                
        return render_template('index.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out successfully.', 'success')
        return redirect(url_for('index'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        # Get some stats for the dashboard
        pending_update_count = ProductUpdateRequest.query.filter_by(status='Pending').count()
        
        # Get counts for the dashboard
        customer_count = Customer.query.count()
        product_count = Product.query.count()
        price_list_count = PriceList.query.count() 
        invoice_count = Invoice.query.count()
        
        # Build stats dictionary
        stats = {
            'customers': customer_count,
            'products': product_count,
            'price_lists': price_list_count,
            'invoices': invoice_count,
            'pending_updates': pending_update_count
        }
        
        # Dynamic card coloring based on thresholds
        card_classes = {
            'customers': 'bg-primary' if customer_count > 10 else 'bg-warning',
            'products': 'bg-success' if product_count > 20 else 'bg-info',
            'price_lists': 'bg-info' if price_list_count > 5 else 'bg-secondary',
            'invoices': 'bg-warning' if invoice_count > 0 else 'bg-light text-dark'
        }
        
        # Get recent activities for the dashboard
        recent_activities = get_recent_activities(limit=5)
        
        return render_template('dashboard_improved.html', 
                              stats=stats,
                              card_classes=card_classes,
                              pending_update_count=pending_update_count,
                              recent_activities=recent_activities)
    
    @app.route('/uploads', methods=['GET'])
    @login_required
    def uploads():
        customers = Customer.query.all()
        recent_uploads = FileUpload.query.order_by(FileUpload.upload_date.desc()).limit(10).all()
        return render_template('uploads.html', customers=customers, recent_uploads=recent_uploads)
    
    # Add stub routes for navigation to work
    @app.route('/customers')
    @login_required
    def customers():
        customers = Customer.query.all()
        return render_template('customers.html', customers=customers)
    
    @app.route('/products')
    @login_required
    def products():
        products = Product.query.all()
        return render_template('products.html', products=products)
    
    @app.route('/price-lists')
    @login_required
    def price_lists():
        price_lists = PriceList.query.all()
        return render_template('price_lists.html', price_lists=price_lists)
    
    @app.route('/invoices')
    @login_required
    def invoices():
        invoices = Invoice.query.all()
        return render_template('invoices.html', invoices=invoices)
    
    @app.route('/quotations')
    @login_required
    def quotations():
        quotations = Quotation.query.all()
        return render_template('quotations.html', quotations=quotations)
    
    # Stub for viewing individual items
    @app.route('/quotation/<int:quotation_id>')
    @login_required
    def view_quotation(quotation_id):
        quotation = Quotation.query.get_or_404(quotation_id)
        return render_template('view_quotation.html', quotation=quotation)
    
    @app.route('/price-list/<int:price_list_id>')
    @login_required
    def view_price_list(price_list_id):
        price_list = PriceList.query.get_or_404(price_list_id)
        return render_template('view_price_list.html', price_list=price_list)
    
    @app.route('/invoice/<int:invoice_id>')
    @login_required
    def view_invoice(invoice_id):
        invoice = Invoice.query.get_or_404(invoice_id)
        return render_template('view_invoice.html', invoice=invoice)
    
    return app
