#!/usr/bin/env python
"""
Routes for quotation export/import functionality
"""
import os
import json
import datetime
from pathlib import Path
from flask import Blueprint, render_template, redirect, url_for, flash, send_from_directory, request, jsonify
from flask_login import login_required
from app import app, db
from models import Quotation, QuotationItem, Customer, Supplier, Product

# Create a blueprint for export/import routes
quotation_export_bp = Blueprint('quotation_export', __name__)

@quotation_export_bp.route('/export-all', methods=['GET'])
@login_required
def export_all_quotations():
    """Export all quotations as JSON"""
    try:
        # Get all quotations
        quotations = Quotation.query.all()
        
        # Initialize the export data structure
        export_data = {
            'metadata': {
                'export_date': datetime.datetime.now().isoformat(),
                'quotation_count': len(quotations),
                'version': '1.0',
                'description': 'Quotation data export for migration'
            },
            'quotations': []
        }
        
        # Process each quotation
        for quotation in quotations:
            # Add the serialized quotation to the export data
            quotation_data = serialize_quotation(quotation)
            export_data['quotations'].append(quotation_data)
        
        # Generate export filename with timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        export_filename = f"quotations_export_{timestamp}.json"
        
        # Ensure export directory exists
        export_dir = Path(app.config['UPLOAD_FOLDER']) / 'exports'
        os.makedirs(export_dir, exist_ok=True)
        export_path = export_dir / export_filename
        
        # Write export data to JSON file
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        # Send the file to the client
        return send_from_directory(
            directory=export_dir,
            path=export_filename,
            as_attachment=True,
            download_name=export_filename
        )
    
    except Exception as e:
        app.logger.error(f"Error exporting quotations: {str(e)}")
        flash(f"Error exporting quotations: {str(e)}", 'danger')
        return redirect(url_for('index'))

@quotation_export_bp.route('/export-customer/<int:customer_id>', methods=['GET'])
@login_required
def export_customer_quotations(customer_id):
    """Export quotations for a specific customer as JSON"""
    try:
        # Get the customer
        customer = Customer.query.get_or_404(customer_id)
        
        # Get all quotations for this customer
        quotations = Quotation.query.filter_by(customer_id=customer_id).all()
        
        # Initialize the export data structure
        export_data = {
            'metadata': {
                'export_date': datetime.datetime.now().isoformat(),
                'quotation_count': len(quotations),
                'version': '1.0',
                'description': f'Quotation export for customer {customer.name}'
            },
            'quotations': []
        }
        
        # Process each quotation
        for quotation in quotations:
            # Add the serialized quotation to the export data
            quotation_data = serialize_quotation(quotation)
            export_data['quotations'].append(quotation_data)
        
        # Generate export filename with customer name and timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_customer_name = customer.name.replace(' ', '_').replace('/', '_')[:30]
        export_filename = f"quotations_{safe_customer_name}_{timestamp}.json"
        
        # Ensure export directory exists
        export_dir = Path(app.config['UPLOAD_FOLDER']) / 'exports'
        os.makedirs(export_dir, exist_ok=True)
        export_path = export_dir / export_filename
        
        # Write export data to JSON file
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        # Send the file to the client
        return send_from_directory(
            directory=export_dir,
            path=export_filename,
            as_attachment=True,
            download_name=export_filename
        )
    
    except Exception as e:
        app.logger.error(f"Error exporting customer quotations: {str(e)}")
        flash(f"Error exporting customer quotations: {str(e)}", 'danger')
        return redirect(url_for('view_customer', customer_id=customer_id))

@quotation_export_bp.route('/export-quotation/<int:quotation_id>', methods=['GET'])
@login_required
def export_single_quotation(quotation_id):
    """Export a single quotation as JSON"""
    try:
        # Get the quotation
        quotation = Quotation.query.get_or_404(quotation_id)
        
        # Initialize the export data structure
        export_data = {
            'metadata': {
                'export_date': datetime.datetime.now().isoformat(),
                'quotation_count': 1,
                'version': '1.0',
                'description': f'Single quotation export for quotation {quotation.quotation_number}'
            },
            'quotations': [serialize_quotation(quotation)]
        }
        
        # Generate export filename with quotation number and timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_quotation_number = quotation.quotation_number.replace('/', '_')
        export_filename = f"quotation_{safe_quotation_number}_{timestamp}.json"
        
        # Ensure export directory exists
        export_dir = Path(app.config['UPLOAD_FOLDER']) / 'exports'
        os.makedirs(export_dir, exist_ok=True)
        export_path = export_dir / export_filename
        
        # Write export data to JSON file
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        # Send the file to the client
        return send_from_directory(
            directory=export_dir,
            path=export_filename,
            as_attachment=True,
            download_name=export_filename
        )
    
    except Exception as e:
        app.logger.error(f"Error exporting quotation: {str(e)}")
        flash(f"Error exporting quotation: {str(e)}", 'danger')
        return redirect(url_for('view_quotation', quotation_id=quotation_id))

def serialize_quotation(quotation):
    """
    Serialize a quotation object to a dictionary for JSON export.
    
    Args:
        quotation: The Quotation object to serialize
        
    Returns:
        dict: Serialized quotation data
    """
    # Basic quotation data
    quotation_data = {
        'id': quotation.id,
        'quotation_number': quotation.quotation_number,
        'quotation_date': quotation.quotation_date.isoformat() if quotation.quotation_date else None,
        'total_amount': quotation.total_amount,
        'currency': quotation.currency,
        'notes': quotation.notes,
        'created_at': quotation.created_at.isoformat() if quotation.created_at else None,
        'updated_at': quotation.updated_at.isoformat() if quotation.updated_at else None,
        'file_path': quotation.file_path,
        'customer': {
            'id': quotation.customer.id,
            'name': quotation.customer.name,
            'email': quotation.customer.email,
            'phone': quotation.customer.phone,
            # Add more customer fields as needed
        },
        'items': []
    }
    
    # Serialize each quotation item
    for item in quotation.items:
        item_data = {
            'id': item.id,
            'description': item.description,
            'scientific_name': item.scientific_name,
            'pot_size': item.pot_size,
            'height': item.height,
            'quantity': item.quantity,
            'selling_price': item.selling_price,
            'vat_rate': item.vat_rate,
            'supplier': item.supplier,
            'cost_price': item.cost_price,
            'total': item.total,
            'position': item.position,
            'product_id': item.product_id
        }
        
        # Add supplier data if available
        if item.supplier_ref:
            item_data['supplier_data'] = {
                'id': item.supplier_ref.id,
                'name': item.supplier_ref.name,
                'email': item.supplier_ref.email
                # Add more supplier fields as needed
            }
        
        # Add product data if available
        if item.product:
            item_data['product_data'] = {
                'id': item.product.id,
                'name': item.product.name,
                'scientific_name': item.product.scientific_name if hasattr(item.product, 'scientific_name') else None
                # Add more product fields as needed
            }
        
        quotation_data['items'].append(item_data)
    
    return quotation_data

def register_export_routes(app):
    """Register the quotation export routes with the Flask app"""
    app.register_blueprint(quotation_export_bp, url_prefix='/quotation')