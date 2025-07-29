"""
Flask-Admin integration for the application.
This module provides an admin dashboard for managing application data.
"""
import logging
from datetime import datetime
from flask import redirect, url_for, flash, abort, request, render_template
from flask_admin import Admin, AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_required
from app import app, db
from models import (
    Customer, CustomerCategory, CustomerContact,
    Product, PriceList, Invoice, InvoiceItem
)

# Set up logging
logger = logging.getLogger(__name__)

class SecureModelView(ModelView):
    """Base class for all model views that require authentication"""
    def is_accessible(self):
        """Check if the current user has access to this admin view"""
        return current_user.is_authenticated and current_user.is_admin
    
    def inaccessible_callback(self, name, **kwargs):
        """Redirect to login page if user doesn't have access"""
        flash('You need to be logged in as an admin to access that page.', 'danger')
        return redirect(url_for('login', next=request.url))

class CustomerModelView(SecureModelView):
    """Customer model admin view with custom fields and formatting"""
    column_list = ('name', 'category', 'email', 'phone', 'created_at', 'updated_at')
    column_labels = {
        'name': 'Customer Name',
        'category': 'Category',
        'email': 'Email Address',
        'phone': 'Phone Number',
        'created_at': 'Created',
        'updated_at': 'Last Updated'
    }
    column_searchable_list = ('name', 'email', 'phone')
    column_filters = ('created_at',)
    column_formatters = {
        'created_at': lambda v, c, m, p: m.created_at.strftime('%Y-%m-%d') if m.created_at else '',
        'updated_at': lambda v, c, m, p: m.updated_at.strftime('%Y-%m-%d') if m.updated_at else ''
    }
    form_excluded_columns = ('price_lists', 'invoices', 'contacts', 'created_at', 'updated_at')
    
    # We'll set form_choices dynamically to avoid application context issues
    def create_form(self):
        """Create the form with dynamic choices"""
        # Get categories within application context
        form = super(CustomerModelView, self).create_form()
        form.category_id.choices = [(c.id, c.name) for c in CustomerCategory.query.order_by(CustomerCategory.name).all()]
        return form
    
    def edit_form(self, obj):
        """Edit the form with dynamic choices"""
        # Get categories within application context
        form = super(CustomerModelView, self).edit_form(obj)
        form.category_id.choices = [(c.id, c.name) for c in CustomerCategory.query.order_by(CustomerCategory.name).all()]
        return form
    
    create_template = 'admin/customer_create.html'
    edit_template = 'admin/customer_edit.html'

class CustomerCategoryModelView(SecureModelView):
    """Customer category model admin view"""
    column_list = ('name', 'description', 'created_at')
    column_labels = {
        'name': 'Category Name',
        'description': 'Description',
        'created_at': 'Created'
    }
    column_searchable_list = ('name', 'description')
    column_formatters = {
        'created_at': lambda v, c, m, p: m.created_at.strftime('%Y-%m-%d') if m.created_at else ''
    }
    form_excluded_columns = ('customers', 'created_at', 'updated_at')

class CustomerContactModelView(SecureModelView):
    """Customer contact model admin view"""
    column_list = ('customer', 'contact_date', 'contact_type', 'notes')
    column_labels = {
        'customer': 'Customer',
        'contact_date': 'Contact Date',
        'contact_type': 'Type',
        'notes': 'Notes'
    }
    column_searchable_list = ('contact_type', 'notes')
    column_filters = ('contact_date', 'contact_type')
    column_formatters = {
        'contact_date': lambda v, c, m, p: m.contact_date.strftime('%Y-%m-%d %H:%M') if m.contact_date else ''
    }
    form_excluded_columns = ('created_at', 'updated_at')
    
    # Static form choices for contact type - no database query needed
    form_choices = {
        'contact_type': [
            ('phone', 'Phone Call'),
            ('email', 'Email'),
            ('meeting', 'Meeting'),
            ('other', 'Other')
        ]
    }
    
    def create_form(self):
        """Create form with customer choices dynamically loaded"""
        form = super(CustomerContactModelView, self).create_form()
        form.customer_id.choices = [(c.id, c.name) for c in Customer.query.order_by(Customer.name).all()]
        return form
        
    def edit_form(self, obj):
        """Edit form with customer choices dynamically loaded"""
        form = super(CustomerContactModelView, self).edit_form(obj)
        form.customer_id.choices = [(c.id, c.name) for c in Customer.query.order_by(Customer.name).all()]
        return form

class CustomerStatsView(BaseView):
    """Custom view for displaying customer statistics"""
    @expose('/')
    @login_required
    def index(self):
        """Main page for customer statistics"""
        if not current_user.is_admin:
            flash('You need to be logged in as an admin to access that page.', 'danger')
            return redirect(url_for('login'))
        
        customers = Customer.query.order_by(Customer.name).all()
        
        # Calculate stats for each customer
        stats = []
        total_invoices = 0
        total_order_value = 0
        
        for customer in customers:
            invoices = customer.invoices
            price_lists = customer.price_lists
            
            # Calculate customer statistics
            total_customer_invoices = len(invoices)
            total_invoices += total_customer_invoices
            
            # Determine last order date
            last_order = None
            if invoices:
                invoice_dates = [i.invoice_date for i in invoices if i.invoice_date]
                if invoice_dates:
                    last_order = max(invoice_dates)
            
            # Calculate average order value
            avg_order_value = 0
            if total_customer_invoices > 0:
                total_customer_spend = sum(i.total_amount or 0 for i in invoices)
                total_order_value += total_customer_spend
                avg_order_value = total_customer_spend / total_customer_invoices
            
            stats.append({
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'category': customer.category.name if customer.category else None,
                'total_invoices': total_customer_invoices,
                'total_price_lists': len(price_lists),
                'last_order': last_order,
                'avg_order_value': avg_order_value
            })
        
        # Calculate overall statistics
        avg_per_customer = total_order_value / len(customers) if customers else 0
        
        return self.render('admin/customer_stats.html', 
                          stats=stats, 
                          total_invoices=total_invoices,
                          total_order_value=total_order_value,
                          avg_per_customer=avg_per_customer)

# Initialize Admin with a function to be called within app context
def init_admin_views(app, db):
    """Initialize the admin with the Flask app and database"""
    # Create admin
    admin = Admin(app, name='Admin Dashboard', template_mode='bootstrap3',
                 index_view=AdminIndexView(name='Dashboard', template='admin/index.html'))
    
    # Add views
    admin.add_view(CustomerModelView(Customer, db.session, name='Customers'))
    admin.add_view(CustomerCategoryModelView(CustomerCategory, db.session, name='Categories'))
    admin.add_view(CustomerContactModelView(CustomerContact, db.session, name='Contacts'))
    admin.add_view(CustomerStatsView(name='Statistics', endpoint='stats'))
    
    # Add views for other models if desired
    # admin.add_view(SecureModelView(Product, db.session, name='Products'))
    # admin.add_view(SecureModelView(Invoice, db.session, name='Invoices'))
    
    logger.info("Flask-Admin integration initialized")
    return admin

# Create a global admin object that will be initialized later
admin = None