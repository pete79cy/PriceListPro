from datetime import datetime
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
    
    # Relationships
    customer = db.relationship('Customer', backref='quotations', lazy=True)
    items = db.relationship('QuotationItem', backref='quotation', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Quotation {self.quotation_number}>'

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SupplierProduct {self.product_name} from {self.supplier.name if self.supplier else "Unknown"}>'

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