from datetime import datetime, date, timedelta
from enum import Enum, auto
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import re
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from decimal import Decimal


class OrderStatusEnum(str, Enum):
    """Enum for order status values - for use as string literals"""
    NEW = "new"               # Newly created order
    PREPARING = "preparing"   # Order is being prepared
    READY = "ready"           # Order is ready for delivery
    DELIVERED = "delivered"   # Order has been delivered to customer
    CANCELLED = "cancelled"   # Order was cancelled
    
    def __str__(self):
        return self.value

# UI display labels for order statuses
ORDER_STATUS_LABELS = {
    OrderStatusEnum.NEW: "New",
    OrderStatusEnum.PREPARING: "Preparing",
    OrderStatusEnum.READY: "Ready for Delivery", 
    OrderStatusEnum.DELIVERED: "Delivered",
    OrderStatusEnum.CANCELLED: "Cancelled"
}

# Colors for UI display
ORDER_STATUS_COLORS = {
    OrderStatusEnum.NEW: "#FF9800",        # Orange
    OrderStatusEnum.PREPARING: "#2196F3",  # Blue
    OrderStatusEnum.READY: "#4CAF50",      # Green
    OrderStatusEnum.DELIVERED: "#9E9E9E",  # Gray
    OrderStatusEnum.CANCELLED: "#F44336"   # Red
}

# Valid transitions between statuses
ORDER_STATUS_TRANSITIONS = {
    OrderStatusEnum.NEW: [OrderStatusEnum.PREPARING, OrderStatusEnum.CANCELLED],
    OrderStatusEnum.PREPARING: [OrderStatusEnum.READY, OrderStatusEnum.CANCELLED],
    OrderStatusEnum.READY: [OrderStatusEnum.DELIVERED, OrderStatusEnum.CANCELLED],
    OrderStatusEnum.DELIVERED: [],  # Terminal state
    OrderStatusEnum.CANCELLED: []   # Terminal state
}

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
    # Order relationship is defined through the backref on the Order model
    
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
    REJECTED = 'REJECTED'
    COMPLETED = 'COMPLETED'
    CREATED = 'created'  # Odd casing exists in the database
    
    # Status display names for UI
    LABELS = {
        DRAFT: 'Draft',
        SENT: 'Sent',
        ACCEPTED: 'Accepted',
        REJECTED: 'Rejected',
        COMPLETED: 'Completed',
        CREATED: 'Created'
    }
    
    # Status colors for UI
    COLORS = {
        DRAFT: '#B0B0B0',  # Grey
        SENT: '#1E90FF',   # Blue
        ACCEPTED: '#4CAF50',  # Green
        REJECTED: '#DC3545',  # Red
        COMPLETED: '#8BC34A',  # Light Green
        CREATED: '#607D8B'  # Blue Grey
    }
    
    # Valid status transitions
    TRANSITIONS = {
        DRAFT: [SENT],
        SENT: [ACCEPTED, REJECTED, COMPLETED, DRAFT],
        ACCEPTED: [COMPLETED, DRAFT],
        REJECTED: [DRAFT],
        COMPLETED: [DRAFT],
        CREATED: [SENT, DRAFT]
    }
    
# The OrderStatusEnum is defined at the top of the file

# For convenience, we define UI constants for order status display
ORDER_STATUS_LABELS = {
    OrderStatusEnum.NEW.value: 'New',
    OrderStatusEnum.PREPARING.value: 'Preparing',
    OrderStatusEnum.READY.value: 'Ready',
    OrderStatusEnum.DELIVERED.value: 'Delivered',
    OrderStatusEnum.CANCELLED.value: 'Cancelled'
}

# Order status colors for UI
ORDER_STATUS_COLORS = {
    OrderStatusEnum.NEW.value: '#FF9800',  # Orange
    OrderStatusEnum.PREPARING.value: '#2196F3',  # Blue
    OrderStatusEnum.READY.value: '#4CAF50',  # Green
    OrderStatusEnum.DELIVERED.value: '#8BC34A',  # Light Green
    OrderStatusEnum.CANCELLED.value: '#F44336'  # Red
}

# Valid order status transitions
ORDER_STATUS_TRANSITIONS = {
    OrderStatusEnum.NEW.value: [OrderStatusEnum.PREPARING.value, OrderStatusEnum.CANCELLED.value],
    OrderStatusEnum.PREPARING.value: [OrderStatusEnum.READY.value, OrderStatusEnum.NEW.value, OrderStatusEnum.CANCELLED.value],
    OrderStatusEnum.READY.value: [OrderStatusEnum.DELIVERED.value, OrderStatusEnum.PREPARING.value, OrderStatusEnum.CANCELLED.value],
    OrderStatusEnum.DELIVERED.value: [OrderStatusEnum.NEW.value, OrderStatusEnum.CANCELLED.value],
    OrderStatusEnum.CANCELLED.value: [OrderStatusEnum.NEW.value]
}

# The Order class is defined later in the file
    
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
    # Store status as string in the database
    status = db.Column(db.String(20), nullable=False, default="new")  # OrderStatus.NEW.value
    delivery_date = db.Column(db.Date, nullable=True)  # Requested delivery date
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # Use backref='customer_orders' to avoid conflicts with the 'orders' name
    customer = db.relationship('Customer', foreign_keys=[customer_id], backref='customer_orders', lazy=True)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Order {self.order_number}>'
        
    def get_status_label(self):
        """Get the human-readable status label"""
        # Convert string status to enum for lookup
        try:
            status_enum = OrderStatusEnum(self.status)
            return ORDER_STATUS_LABELS.get(status_enum, self.status)
        except ValueError:
            return self.status
        
    def get_status_color(self):
        """Get the color code for the status"""
        try:
            status_enum = OrderStatusEnum(self.status)
            return ORDER_STATUS_COLORS.get(status_enum, '#000000')
        except ValueError:
            return '#000000'
        
    def can_transition_to(self, target_status):
        """Check if the order can transition to the target status"""
        try:
            current_status_enum = OrderStatusEnum(self.status)
            # If target_status is already enum, use its value for comparison
            target_value = target_status.value if isinstance(target_status, OrderStatusEnum) else target_status
            target_enum = OrderStatusEnum(target_value)
            return target_enum in ORDER_STATUS_TRANSITIONS.get(current_status_enum, [])
        except ValueError:
            return False
    
    @property
    def subtotal(self):
        """Calculate the subtotal for the order (sum of all items)"""
        return sum(item.quantity * item.price for item in self.items) if self.items else 0.0
    
    @property
    def total_items(self):
        """Get the total number of items in this order"""
        return sum(item.quantity for item in self.items) if self.items else 0
    
    @property
    def vat_amount(self):
        """Calculate VAT amount (for delivery notes that include VAT)"""
        # Default VAT rate - this could be configurable
        vat_rate = 0.24  # 24% VAT
        return self.subtotal * vat_rate
    
    @property
    def total(self):
        """Calculate the total with VAT for the order"""
        return self.subtotal + self.vat_amount
        
    def transition_to(self, target_status):
        """
        Transition the order to a new status if allowed
        Returns True if transition was successful, False otherwise
        """
        if not self.can_transition_to(target_status):
            return False
        
        # Store status value (string) in the database    
        self.status = target_status.value if isinstance(target_status, OrderStatusEnum) else target_status
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
    vat_rate = db.Column(db.Float, nullable=False, default=19.0)  # Default VAT rate 19%
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
        
    def get_vat_amount(self):
        """Calculate the VAT amount for this item"""
        return self.get_total() * (self.vat_rate / 100)

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

class DeliveryAdjustmentType:
    """Types of delivery adjustments"""
    RETURN = 'return'
    ADDITIONAL = 'additional'
    REPLACEMENT = 'replacement'
    
    LABELS = {
        RETURN: 'Product Return',
        ADDITIONAL: 'Additional Delivery',
        REPLACEMENT: 'Product Replacement'
    }
    
    COLORS = {
        RETURN: '#dc3545',      # Red
        ADDITIONAL: '#28a745',  # Green
        REPLACEMENT: '#ffc107'  # Yellow
    }

class DeliveryAdjustment(db.Model):
    """Model for tracking returns and additional deliveries after initial order/quotation delivery"""
    id = db.Column(db.Integer, primary_key=True)
    # Can be linked to either an order or a quotation
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True)
    quotation_id = db.Column(db.Integer, db.ForeignKey('quotation.id'), nullable=True)
    adjustment_type = db.Column(db.String(20), nullable=False)  # 'return', 'additional', 'replacement'
    adjustment_number = db.Column(db.String(50), nullable=False, unique=True)
    adjustment_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    reason = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, confirmed, processed
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order = db.relationship('Order', backref='delivery_adjustments', lazy=True)
    quotation = db.relationship('Quotation', backref='delivery_adjustments', lazy=True)
    items = db.relationship('DeliveryAdjustmentItem', backref='adjustment', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<DeliveryAdjustment {self.adjustment_number}>'
    
    def get_type_label(self):
        """Get human-readable type label"""
        return DeliveryAdjustmentType.LABELS.get(self.adjustment_type, self.adjustment_type)
    
    def get_type_color(self):
        """Get color for the adjustment type"""
        return DeliveryAdjustmentType.COLORS.get(self.adjustment_type, '#6c757d')
    
    @property
    def total_value(self):
        """Calculate total value of the adjustment (absolute value)"""
        if not self.items:
            return 0.0
        return sum(item.quantity * item.unit_price for item in self.items)
    
    @property
    def signed_total_value(self):
        """Calculate signed total value based on adjustment type"""
        if not self.items:
            return 0.0
        
        base_total = sum(item.quantity * item.unit_price for item in self.items)
        
        # Returns should be negative (subtract from invoice)
        if self.adjustment_type == DeliveryAdjustmentType.RETURN:
            return -base_total
        # Additional deliveries and replacements should be positive (add to invoice)
        else:
            return base_total
    
    @property
    def parent_document(self):
        """Get the parent document (order or quotation)"""
        return self.order if self.order else self.quotation
    
    @property
    def parent_type(self):
        """Get the type of parent document"""
        return 'order' if self.order else 'quotation'
    
    @staticmethod
    def generate_adjustment_number(adjustment_type):
        """Generate unique adjustment number"""
        year = datetime.now().year
        prefix_map = {
            DeliveryAdjustmentType.RETURN: 'RET',
            DeliveryAdjustmentType.ADDITIONAL: 'ADD',
            DeliveryAdjustmentType.REPLACEMENT: 'REP'
        }
        prefix = prefix_map.get(adjustment_type, 'ADJ')
        
        # Get the highest number for this type and year
        last_adjustment = DeliveryAdjustment.query.filter(
            DeliveryAdjustment.adjustment_number.like(f'{prefix}-{year}-%')
        ).order_by(DeliveryAdjustment.adjustment_number.desc()).first()
        
        if last_adjustment:
            # Extract the sequence number and increment
            parts = last_adjustment.adjustment_number.split('-')
            if len(parts) >= 3:
                try:
                    sequence = int(parts[2]) + 1
                except (ValueError, IndexError):
                    sequence = 1
            else:
                sequence = 1
        else:
            sequence = 1
        
        return f'{prefix}-{year}-{sequence:04d}'

class DeliveryAdjustmentItem(db.Model):
    """Individual items in a delivery adjustment"""
    id = db.Column(db.Integer, primary_key=True)
    adjustment_id = db.Column(db.Integer, db.ForeignKey('delivery_adjustment.id'), nullable=False)
    order_item_id = db.Column(db.Integer, db.ForeignKey('order_item.id'), nullable=True)  # Reference to original order item
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    plant_name = db.Column(db.String(200), nullable=False)
    size = db.Column(db.String(50), nullable=True)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    vat_rate = db.Column(db.Float, nullable=False, default=19.0)
    reason = db.Column(db.Text, nullable=True)  # Specific reason for this item
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    order_item = db.relationship('OrderItem', backref='adjustments', lazy=True)
    product = db.relationship('Product', backref='adjustment_items', lazy=True)
    
    def __repr__(self):
        return f'<DeliveryAdjustmentItem {self.plant_name} x {self.quantity}>'
    
    def get_total(self):
        """Calculate total for this adjustment item"""
        return self.quantity * self.unit_price
    
    def get_vat_amount(self):
        """Calculate VAT amount for this item"""
        return self.get_total() * (self.vat_rate / 100)

class FinalProformaInvoice(db.Model):
    """Final proforma invoice combining original order/quotation with all adjustments"""
    id = db.Column(db.Integer, primary_key=True)
    # Can be linked to either an order or a quotation
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True)
    quotation_id = db.Column(db.Integer, db.ForeignKey('quotation.id'), nullable=True)
    invoice_number = db.Column(db.String(50), nullable=False, unique=True)
    invoice_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    original_total = db.Column(db.Float, nullable=False)  # Original order/quotation total
    adjustments_total = db.Column(db.Float, nullable=False, default=0.0)  # Sum of all adjustments
    final_total = db.Column(db.Float, nullable=False)  # Final amount after adjustments
    currency = db.Column(db.String(10), nullable=False, default='€')
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='draft')  # draft, sent, paid
    file_path = db.Column(db.String(255), nullable=True)  # Path to generated PDF
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order = db.relationship('Order', backref='final_proforma_invoice', uselist=False, lazy=True)
    quotation = db.relationship('Quotation', backref='final_proforma_invoice', uselist=False, lazy=True)
    
    def __repr__(self):
        return f'<FinalProformaInvoice {self.invoice_number}>'
    
    @staticmethod
    def generate_invoice_number():
        """Generate unique final proforma invoice number"""
        year = datetime.now().year
        prefix = 'FPI'  # Final Proforma Invoice
        
        # Get the highest number for this year
        last_invoice = FinalProformaInvoice.query.filter(
            FinalProformaInvoice.invoice_number.like(f'{prefix}-{year}-%')
        ).order_by(FinalProformaInvoice.invoice_number.desc()).first()
        
        if last_invoice:
            # Extract sequence number and increment
            parts = last_invoice.invoice_number.split('-')
            if len(parts) >= 3:
                try:
                    sequence = int(parts[2]) + 1
                except (ValueError, IndexError):
                    sequence = 1
            else:
                sequence = 1
        else:
            sequence = 1
        
        return f'{prefix}-{year}-{sequence:04d}'
    
    @property
    def parent_document(self):
        """Get the parent document (order or quotation)"""
        return self.order if self.order else self.quotation
    
    @property
    def parent_type(self):
        """Get the type of parent document"""
        return 'order' if self.order else 'quotation'
    
    def calculate_totals(self):
        """Calculate and update totals based on order/quotation and adjustments"""
        # Original total (from order or quotation)
        if self.order:
            self.original_total = self.order.total if self.order else 0.0
            parent_adjustments = self.order.delivery_adjustments
        elif self.quotation:
            # Calculate quotation total from items
            self.original_total = sum(item.selling_price * item.quantity for item in self.quotation.items) if self.quotation.items else 0.0
            parent_adjustments = self.quotation.delivery_adjustments
        else:
            self.original_total = 0.0
            parent_adjustments = []
        
        # Calculate adjustments total
        adjustments_total = 0.0
        if parent_adjustments:
            for adjustment in parent_adjustments:
                if adjustment.status == 'confirmed':
                    if adjustment.adjustment_type == DeliveryAdjustmentType.RETURN:
                        # Returns reduce the total (negative value)
                        adjustments_total -= adjustment.total_value
                    else:
                        # Additional deliveries and replacements add to total
                        adjustments_total += adjustment.total_value
        
        self.adjustments_total = adjustments_total
        self.final_total = self.original_total + adjustments_total

# Order model is already defined earlier in the file
    
    def __repr__(self):
        return f'<Order {self.order_number}>'
    
    @staticmethod
    def generate_order_number():
        """Generate a unique order number with format ORD-YYYY-XXXX"""
        year = datetime.now().year
        
        # Get the highest order number for the current year
        last_order = Order.query.filter(
            Order.order_number.like(f'ORD-{year}-%')
        ).order_by(db.desc(Order.order_number)).first()
        
        if last_order:
            # Extract the number portion and increment
            try:
                num = int(last_order.order_number.split('-')[-1])
                new_num = num + 1
            except (ValueError, IndexError):
                new_num = 1
        else:
            new_num = 1
            
        # Format with 4 digits
        return f'ORD-{year}-{new_num:04d}'
    
    def get_status_label(self):
        """Get human-readable status label"""
        return OrderStatus.LABELS.get(self.status, "Unknown")
    
    def get_status_color(self):
        """Get color code for the status for UI display"""
        return OrderStatus.COLORS.get(self.status, "#999999")
    
    def can_transition_to(self, new_status):
        """Check if order can transition to a new status"""
        # Define valid transitions between statuses
        valid_transitions = {
            OrderStatus.NEW: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
            OrderStatus.PREPARING: [OrderStatus.READY, OrderStatus.CANCELLED],
            OrderStatus.READY: [OrderStatus.DELIVERED, OrderStatus.CANCELLED],
            OrderStatus.DELIVERED: [],  # Terminal state
            OrderStatus.CANCELLED: []   # Terminal state
        }
        
        return new_status in valid_transitions.get(self.status, [])
    
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


# OrderItem model is already defined earlier in the file
    
    # OrderItem relationships and methods are defined above


# PriceList model is already defined earlier in the file
    
    # PriceList relationships and methods are defined above


class PriceListItem(db.Model):
    """Individual items in a customer's price list"""
    id = db.Column(db.Integer, primary_key=True)
    price_list_id = db.Column(db.Integer, db.ForeignKey('price_list.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    name = db.Column(db.String(200), nullable=False)  # Plant name
    size = db.Column(db.String(50), nullable=True)    # Size or pot size
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', backref='price_list_items', lazy=True)
    
    def __repr__(self):
        return f'<PriceListItem {self.name} - {self.price}>'


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


class InvoiceAddendum(db.Model):
    """Invoice Addendum - supplementary sales document that can be attached to invoices"""
    __tablename__ = "invoice_addenda"
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    invoice_number = db.Column(db.String(30), nullable=False)  # Reference to the external invoice
    period_from = db.Column(db.Date, nullable=False)
    period_to = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='draft')  # draft, locked
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = db.relationship("Customer", backref="invoice_addenda", lazy=True)
    lines = db.relationship("InvoiceAddendumLine", back_populates="addendum",
                          cascade="all, delete-orphan", order_by="InvoiceAddendumLine.sale_date")
    
    def __repr__(self):
        return f'<InvoiceAddendum {self.invoice_number} - {self.customer.name if self.customer else "No Customer"}>'
    
    def get_total_amount(self):
        """Calculate total amount for this addendum"""
        total = Decimal('0.00')
        for line in self.lines:
            line_total = line.quantity * line.unit_price
            total += line_total
        return float(total)
    
    def get_total_vat(self):
        """Calculate total VAT for this addendum"""
        total_vat = Decimal('0.00')
        for line in self.lines:
            line_total = line.quantity * line.unit_price
            vat_amount = line_total * (line.vat_rate / Decimal('100'))
            total_vat += vat_amount
        return float(total_vat)
    
    def get_grand_total(self):
        """Calculate grand total including VAT"""
        return self.get_total_amount() + self.get_total_vat()


class InvoiceAddendumLine(db.Model):
    """Individual line items in an invoice addendum"""
    __tablename__ = "invoice_addendum_lines"
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    addendum_id = db.Column(UUID(as_uuid=True), db.ForeignKey("invoice_addenda.id"), nullable=False)
    # Independent product fields - not connected to main product database
    product_name = db.Column(db.String(200), nullable=False)
    product_category = db.Column(db.String(100), nullable=True)
    product_description = db.Column(db.Text, nullable=True)
    sale_date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Numeric(10, 2), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    vat_rate = db.Column(db.Numeric(4, 2), nullable=False, default=19.00)  # 5.00 or 19.00
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    addendum = db.relationship("InvoiceAddendum", back_populates="lines")
    
    def __repr__(self):
        return f'<InvoiceAddendumLine {self.product_name} - {self.quantity}>'
    
    def get_line_total(self):
        """Calculate total for this line (quantity * unit_price)"""
        return float(self.quantity * self.unit_price)
    
    def get_vat_amount(self):
        """Calculate VAT amount for this line"""
        line_total = self.quantity * self.unit_price
        vat_amount = line_total * (self.vat_rate / Decimal('100'))
        return float(vat_amount)
    
    def get_total_with_vat(self):
        """Calculate total including VAT for this line"""
        return self.get_line_total() + self.get_vat_amount()