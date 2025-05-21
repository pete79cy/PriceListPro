from datetime import datetime, date, timedelta
from enum import Enum
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class CustomerCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customers = db.relationship('Customer', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<CustomerCategory {self.name}>'

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('customer_category.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    price_lists = db.relationship('PriceList', backref='customer', lazy=True)
    invoices = db.relationship('Invoice', backref='customer', lazy=True)
    contacts = db.relationship('CustomerContact', backref='customer', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Customer {self.name}>'

class CustomerContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    contact_date = db.Column(db.DateTime, default=datetime.utcnow)
    contact_type = db.Column(db.String(50), nullable=False)  # e.g. phone, email, meeting
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CustomerContact {self.contact_type} on {self.contact_date}>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    scientific_name = db.Column(db.String(150), nullable=True)
    pot = db.Column(db.String(50), nullable=True)
    # Using a partial unique index in the database (unique only for non-NULL values)
    # This allows multiple products with NULL SKU values
    sku = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    price_lists = db.relationship('PriceList', backref='product', lazy=True)
    invoice_items = db.relationship('InvoiceItem', backref='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.name}>'

class PriceList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    effective_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    source_file = db.Column(db.String(255), nullable=True)  # Name of the Excel file it came from
    
    def __repr__(self):
        return f'<PriceList Customer: {self.customer_id}, Product: {self.product_id}, Price: {self.price}>'

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    invoice_number = db.Column(db.String(50), nullable=False, unique=True)
    invoice_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(10), nullable=False, default='€')  # Euro is the default currency
    file_path = db.Column(db.String(255), nullable=True)  # Path to the stored PDF
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'

class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    description = db.Column(db.String(200), nullable=False)
    scientific_name = db.Column(db.String(150), nullable=True)  # Store scientific name if present
    pot_size = db.Column(db.String(50), nullable=True)  # Store pot size if present
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    vat = db.Column(db.Float, nullable=True)
    vat_percentage = db.Column(db.Float, nullable=True)  # Store VAT percentage if applicable
    total = db.Column(db.Float, nullable=True)
    
    def __repr__(self):
        return f'<InvoiceItem {self.description}>'

class FileUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)  # 'excel' or 'pdf'
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)
    processing_notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<FileUpload {self.filename}>'

class ProductUpdateRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    price_list_id = db.Column(db.Integer, db.ForeignKey('price_list.id'), nullable=True)
    old_price = db.Column(db.Float, nullable=False)
    new_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')  # 'Pending', 'Approved', 'Rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    source_file = db.Column(db.String(255), nullable=True)  # Where the update came from
    
    # Relationships
    product = db.relationship('Product', backref='update_requests', lazy=True)
    price_list = db.relationship('PriceList', backref='update_requests', lazy=True)
    
    def __repr__(self):
        return f'<ProductUpdateRequest Product: {self.product_id}, Old: {self.old_price}, New: {self.new_price}, Status: {self.status}>'

class QuotationStatus:
    """Enum-like class for quotation statuses"""
    DRAFT = 'DRAFT'
    SENT = 'SENT'
    ACCEPTED = 'ACCEPTED'
    COMPLETED = 'COMPLETED'
    CREATED = 'created'  # Odd casing exists in the database
    
    # Status display names for UI
    LABELS = {
        DRAFT: 'Draft',
        SENT: 'Sent',
        ACCEPTED: 'Accepted',
        COMPLETED: 'Completed',
        CREATED: 'Created'
    }
    
    # Status colors for UI
    COLORS = {
        DRAFT: '#B0B0B0',  # Grey
        SENT: '#1E90FF',   # Blue
        ACCEPTED: '#4CAF50',  # Green
        COMPLETED: '#8BC34A',  # Light Green
        CREATED: '#607D8B'  # Blue Grey
    }
    
    # Valid status transitions
    TRANSITIONS = {
        DRAFT: [SENT],
        SENT: [ACCEPTED, COMPLETED, DRAFT],
        ACCEPTED: [COMPLETED, DRAFT],
        COMPLETED: [DRAFT],
        CREATED: [SENT, DRAFT]
    }
    
class OrderStatus:
    """Enum-like class for order statuses"""
    NEW = 'NEW'
    PREPARING = 'PREPARING'
    READY = 'READY'
    DELIVERED = 'DELIVERED'
    
    # Status display names for UI
    LABELS = {
        NEW: 'New',
        PREPARING: 'Preparing',
        READY: 'Ready',
        DELIVERED: 'Delivered'
    }
    
    # Status colors for UI
    COLORS = {
        NEW: '#FF9800',  # Orange
        PREPARING: '#2196F3',  # Blue
        READY: '#4CAF50',  # Green
        DELIVERED: '#8BC34A',  # Light Green
    }
    
    # Valid status transitions
    TRANSITIONS = {
        NEW: [PREPARING],
        PREPARING: [READY, NEW],
        READY: [DELIVERED, PREPARING],
        DELIVERED: [NEW]  # Allow reopening completed orders if needed
    }
    
class Quotation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    quotation_number = db.Column(db.String(50), nullable=False, unique=True)
    quotation_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    total_amount = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(10), nullable=False, default='€')  # Euro is the default currency
    notes = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(255), nullable=True)  # Path to the stored PDF (if generated)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default=QuotationStatus.DRAFT)
    valid_until = db.Column(db.Date, nullable=True)  # Date until when the quotation is valid
    viewed_at = db.Column(db.DateTime, nullable=True)  # When the customer viewed the quotation
    accepted_at = db.Column(db.DateTime, nullable=True)  # When the customer accepted the quotation
    rejected_at = db.Column(db.DateTime, nullable=True)  # When the customer rejected the quotation
    order_id = db.Column(db.String(50), nullable=True)  # Reference to the created order
    
    # Relationships
    customer = db.relationship('Customer', backref='quotations', lazy=True)
    items = db.relationship('QuotationItem', backref='quotation', lazy=True, cascade="all, delete-orphan", 
                           order_by="QuotationItem.position")
    
    def __repr__(self):
        return f'<Quotation {self.quotation_number}>'
        
    def get_status_label(self):
        """Get the human-readable status label"""
        return QuotationStatus.LABELS.get(self.status, self.status)
        
    def get_status_color(self):
        """Get the color code for the status"""
        return QuotationStatus.COLORS.get(self.status, '#000000')
        
    def can_transition_to(self, target_status):
        """Check if the quotation can transition to the target status"""
        return target_status in QuotationStatus.TRANSITIONS.get(self.status, [])
        
    def transition_to(self, target_status):
        """
        Transition the quotation to a new status if allowed
        Returns True if transition was successful, False otherwise
        """
        if not self.can_transition_to(target_status):
            return False
            
        # Update status timestamp based on the transition
        now = datetime.utcnow()
        
        if target_status == 'SENT':
            # When marked as sent, set viewed_at time
            self.viewed_at = now
        elif target_status == 'ACCEPTED':
            self.accepted_at = now
        elif target_status == 'COMPLETED':
            # When completed, make sure accepted_at is set if it wasn't already
            if not self.accepted_at:
                self.accepted_at = now
            
        self.status = target_status
        self.updated_at = now
        return True
        
    def is_editable(self):
        """Check if the quotation is in an editable state"""
        return self.status == QuotationStatus.DRAFT
        
    def is_old(self):
        """Check if the quotation is more than 30 days old since being sent"""
        # If not in SENT status, it's not considered old
        if self.status != 'SENT':
            return False
            
        # If no valid_until date, we can't determine if it's old
        if not self.valid_until:
            return False
            
        # Check if current date is past the valid_until date
        current_date = datetime.utcnow().date()
        return current_date > self.valid_until

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    contact_person = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_inhouse = db.Column(db.Boolean, default=False)  # Flag for in-house production
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products = db.relationship('SupplierProduct', backref='supplier', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Supplier {self.name}>'
        
    def to_dict(self):
        """Convert supplier object to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "contact_person": self.contact_person,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "notes": self.notes,
            "is_inhouse": self.is_inhouse,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "product_count": len(self.products) if self.products else 0
        }

class SupplierProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    scientific_name = db.Column(db.String(150), nullable=True)
    height = db.Column(db.String(50), nullable=True)
    pot_size = db.Column(db.String(50), nullable=True)
    price = db.Column(db.Float, nullable=False)
    cost_price = db.Column(db.Float, nullable=True)  # What we pay for the item
    last_detected = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    flagged_duplicate = db.Column(db.Boolean, default=False)  # Flag for potential duplicates
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SupplierProduct {self.product_name} from {self.supplier.name if self.supplier else "Unknown"}>'
        
class Order(db.Model):
    """Model for daily plant orders with mobile-friendly input"""
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=OrderStatus.NEW)
    delivery_date = db.Column(db.Date, nullable=True)  # Requested delivery date
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('Customer', backref='orders', lazy=True)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Order {self.order_number}>'
        
    def get_status_label(self):
        """Get the human-readable status label"""
        return OrderStatus.LABELS.get(self.status, self.status)
        
    def get_status_color(self):
        """Get the color code for the status"""
        return OrderStatus.COLORS.get(self.status, '#000000')
        
    def can_transition_to(self, target_status):
        """Check if the order can transition to the target status"""
        return target_status in OrderStatus.TRANSITIONS.get(self.status, [])
        
    def transition_to(self, target_status):
        """
        Transition the order to a new status if allowed
        Returns True if transition was successful, False otherwise
        """
        if not self.can_transition_to(target_status):
            return False
            
        self.status = target_status
        self.updated_at = datetime.utcnow()
        return True
    
    def is_due_today(self):
        """Check if the order is due for delivery today"""
        if not self.delivery_date:
            return False
        return self.delivery_date == date.today()
    
    def is_due_tomorrow(self):
        """Check if the order is due for delivery tomorrow"""
        if not self.delivery_date:
            return False
        return self.delivery_date == date.today() + timedelta(days=1)
    
    def is_due_this_week(self):
        """Check if the order is due within the next 7 days"""
        if not self.delivery_date:
            return False
        today = date.today()
        next_week = today + timedelta(days=7)
        return today <= self.delivery_date <= next_week
        
class OrderItem(db.Model):
    """Model for individual items within an order"""
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    price_list_id = db.Column(db.Integer, db.ForeignKey('price_list.id'), nullable=True)
    plant_name = db.Column(db.String(200), nullable=False)
    size = db.Column(db.String(50), nullable=True)  # Size/pot size
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)
    updated_price_list = db.Column(db.Boolean, default=False)  # Flag if this order updated the price list
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', backref='order_items', lazy=True)
    price_list = db.relationship('PriceList', backref='order_items', lazy=True)
    
    def __repr__(self):
        return f'<OrderItem {self.plant_name} x {self.quantity}>'
        
    def get_total(self):
        """Calculate the total price for this item"""
        return self.quantity * self.price

class QuotationItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quotation_id = db.Column(db.Integer, db.ForeignKey('quotation.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    description = db.Column(db.String(200), nullable=False)
    scientific_name = db.Column(db.String(150), nullable=True)
    pot_size = db.Column(db.String(50), nullable=True)
    height = db.Column(db.String(50), nullable=True)  # Plant height (e.g., "30cm", "150/200cm")
    quantity = db.Column(db.Float, nullable=False, default=1)
    selling_price = db.Column(db.Float, nullable=False)
    vat_rate = db.Column(db.Float, nullable=False, default=19.0)  # Default VAT rate of 19%
    supplier = db.Column(db.String(255), nullable=True)  # Supplier name 
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=True)  # Link to supplier
    cost_price = db.Column(db.Float, nullable=True)  # What we pay for the item
    total = db.Column(db.Float, nullable=True)  # Total price (selling_price * quantity)
    position = db.Column(db.Integer, default=0)  # Position for ordering items in the quotation
    
    # Relationships
    product = db.relationship('Product', backref='quotation_items', lazy=True)
    supplier_ref = db.relationship('Supplier', backref='quotation_items', lazy=True)
    
    def __repr__(self):
        return f'<QuotationItem {self.description}>'

class CompanySettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True, default="Your Company Name")
    address_line1 = db.Column(db.String(255), nullable=True, default="Address Line 1")
    address_line2 = db.Column(db.String(255), nullable=True, default="Address Line 2")
    phone = db.Column(db.String(50), nullable=True, default="+49 123 456789")
    email = db.Column(db.String(100), nullable=True, default="info@example.com")
    logo_path = db.Column(db.String(255), nullable=True)
    pdf_orientation = db.Column(db.String(20), nullable=True, default="portrait")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<CompanySettings {self.name}>'