import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_from_directory
from replit_auth import require_login
from app import db
from models import Quotation, Customer

quotation_bp = Blueprint('quotation', __name__, url_prefix='/quotation')

@quotation_bp.route('/customize_fields', methods=['GET', 'POST'])
@require_login
def customize_fields():
    """Customize which fields to include in quotation PDF"""
    quotation_fields = [
        # Customer fields
        {'name': 'customer_name', 'label': 'Customer Name', 'default': True, 'category': 'Customer'},
        {'name': 'customer_email', 'label': 'Customer Email', 'default': False, 'category': 'Customer'},
        {'name': 'customer_phone', 'label': 'Customer Phone', 'default': False, 'category': 'Customer'},
        {'name': 'customer_address', 'label': 'Customer Address', 'default': False, 'category': 'Customer'},
        
        # Quotation fields
        {'name': 'quotation_number', 'label': 'Quotation Number', 'default': True, 'category': 'Quotation'},
        {'name': 'quotation_date', 'label': 'Quotation Date', 'default': True, 'category': 'Quotation'},
        {'name': 'notes', 'label': 'Notes', 'default': True, 'category': 'Quotation'},
        
        # Item fields
        {'name': 'product_name', 'label': 'Product Name', 'default': True, 'category': 'Items'},
        {'name': 'product_scientific_name', 'label': 'Scientific Name', 'default': False, 'category': 'Items'},
        {'name': 'product_pot_size', 'label': 'Pot Size', 'default': True, 'category': 'Items'},
        {'name': 'product_height', 'label': 'Height', 'default': False, 'category': 'Items'},
        {'name': 'product_quantity', 'label': 'Quantity', 'default': True, 'category': 'Items'},
        {'name': 'product_price', 'label': 'Price', 'default': True, 'category': 'Items'},
        {'name': 'product_total', 'label': 'Item Total', 'default': True, 'category': 'Items'},
        
        # Totals fields
        {'name': 'subtotal', 'label': 'Subtotal', 'default': True, 'category': 'Totals'},
        {'name': 'vat', 'label': 'VAT', 'default': True, 'category': 'Totals'},
        {'name': 'total', 'label': 'Grand Total', 'default': True, 'category': 'Totals'},
        
        # Company fields
        {'name': 'company_name', 'label': 'Company Name', 'default': True, 'category': 'Company'},
        {'name': 'company_address', 'label': 'Company Address', 'default': True, 'category': 'Company'},
        {'name': 'company_phone', 'label': 'Company Phone', 'default': True, 'category': 'Company'},
        {'name': 'company_email', 'label': 'Company Email', 'default': True, 'category': 'Company'}
    ]
    
    # Get quotation_id if provided (to return to after customization)
    quotation_id = request.args.get('quotation_id')
    
    if request.method == 'POST':
        selected_fields = request.form.getlist('fields')
        session['quotation_fields'] = selected_fields  # Store selected fields in the session
        
        flash('Quotation fields customized successfully!', 'success')
        
        # If quotation_id is provided, redirect back to that quotation's page
        if quotation_id:
            return redirect(url_for('view_quotation', quotation_id=quotation_id))
        
        # Otherwise redirect to the quotations list
        return redirect(url_for('quotations'))
    
    # If we have saved settings, use them
    if 'quotation_fields' in session:
        saved_fields = session['quotation_fields']
        for field in quotation_fields:
            field['default'] = field['name'] in saved_fields
    
    return render_template('quotation/customize_fields.html', 
                          fields=quotation_fields, 
                          quotation_id=quotation_id)

@quotation_bp.route('/<int:quotation_id>/export/custom')
@require_login
def export_custom(quotation_id):
    """Export a quotation as PDF using custom field selection"""
    from utils.custom_pdf_generator import generate_custom_pdf
    
    # Get the quotation
    quotation = Quotation.query.get_or_404(quotation_id)
    
    # Get the selected fields from session
    fields = session.get('quotation_fields', [])
    
    # If no fields are selected, use defaults
    if not fields:
        flash('No fields selected for the PDF. Using default fields.', 'warning')
        fields = ['customer_name', 'quotation_number', 'quotation_date', 
                 'product_name', 'product_quantity', 'product_price', 'product_total',
                 'subtotal', 'vat', 'total']
    
    # Generate PDF with selected fields
    pdf_path = generate_custom_pdf(quotation, fields)
    
    if pdf_path:
        # Parse the filename from path
        filename = pdf_path.split('/')[-1]
        # Return the file directly instead of redirecting
        return send_from_directory(os.path.join(os.getcwd(), 'static', 'pdf'), filename, as_attachment=True)
    else:
        flash('Error generating PDF', 'danger')
        return redirect(url_for('view_quotation', quotation_id=quotation_id))