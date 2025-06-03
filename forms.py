from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, IntegerField, FloatField, BooleanField
from wtforms.validators import DataRequired, Optional, NumberRange
from models import Customer, Product, OrderStatusEnum, ORDER_STATUS_LABELS

class EnhancedOrderForm(FlaskForm):
    """Enhanced form for creating and editing orders"""
    customer_id = SelectField('Customer', 
                            coerce=int, 
                            validators=[DataRequired(message="Please select a customer")],
                            choices=[])
    
    delivery_date = DateField('Delivery Date', 
                            validators=[Optional()],
                            description="Optional delivery date")
    
    notes = TextAreaField('Order Notes', 
                        validators=[Optional()],
                        description="Additional notes for this order")
    
    status = SelectField('Status',
                       validators=[Optional()],
                       choices=[])
    
    def __init__(self, *args, **kwargs):
        super(EnhancedOrderForm, self).__init__(*args, **kwargs)
        
        # Populate customer choices
        customers = Customer.query.order_by(Customer.name).all()
        self.customer_id.choices = [(0, '-- Select Customer --')] + [
            (customer.id, customer.name) for customer in customers
        ]
        
        # Populate status choices (will be updated via JavaScript for existing orders)
        self.status.choices = [
            (status.value, label) for status, label in ORDER_STATUS_LABELS.items()
        ]

class OrderItemForm(FlaskForm):
    """Form for individual order items"""
    product_id = SelectField('Product', 
                           coerce=int, 
                           validators=[Optional()],
                           choices=[])
    
    plant_name = StringField('Plant Name', 
                           validators=[DataRequired()],
                           description="Name of the plant or product")
    
    size = StringField('Size/Pot', 
                     validators=[Optional()],
                     description="Size, pot size, or other specifications")
    
    quantity = IntegerField('Quantity', 
                          validators=[DataRequired(), NumberRange(min=1)],
                          default=1)
    
    price = FloatField('Unit Price (€)', 
                     validators=[DataRequired(), NumberRange(min=0)],
                     description="Price per unit in euros")
    
    vat_rate = SelectField('VAT Rate', 
                         coerce=float,
                         validators=[DataRequired()],
                         choices=[
                             (5.0, '5% (Plants)'),
                             (19.0, '19% (Standard)'),
                             (0.0, '0% (Exempt)')
                         ],
                         default=19.0)
    
    notes = TextAreaField('Item Notes', 
                        validators=[Optional()],
                        description="Additional notes for this item")
    
    update_price_list = BooleanField('Update Customer Price List',
                                   default=False,
                                   description="Update the customer's price list with this price")
    
    def __init__(self, *args, **kwargs):
        super(OrderItemForm, self).__init__(*args, **kwargs)
        
        # Populate product choices
        products = Product.query.order_by(Product.name).all()
        self.product_id.choices = [(0, '-- Select Product --')] + [
            (product.id, f"{product.name} - {product.scientific_name or ''}") 
            for product in products
        ]

class PriceListUpdateForm(FlaskForm):
    """Form for updating customer price lists"""
    customer_id = SelectField('Customer', 
                            coerce=int, 
                            validators=[DataRequired()],
                            choices=[])
    
    product_id = SelectField('Product', 
                           coerce=int, 
                           validators=[DataRequired()],
                           choices=[])
    
    price = FloatField('New Price (€)', 
                     validators=[DataRequired(), NumberRange(min=0)],
                     description="New price for this customer-product combination")
    
    def __init__(self, *args, **kwargs):
        super(PriceListUpdateForm, self).__init__(*args, **kwargs)
        
        # Populate choices
        customers = Customer.query.order_by(Customer.name).all()
        self.customer_id.choices = [(0, '-- Select Customer --')] + [
            (customer.id, customer.name) for customer in customers
        ]
        
        products = Product.query.order_by(Product.name).all()
        self.product_id.choices = [(0, '-- Select Product --')] + [
            (product.id, f"{product.name} - {product.scientific_name or ''}") 
            for product in products
        ]