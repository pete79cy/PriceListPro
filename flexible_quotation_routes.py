"""
Routes for generating flexible quotation PDFs.
These routes allow selecting which fields to include in the quotation PDF.

Add these routes to your routes.py file.
"""

import os
import json
import traceback
import logging
from flask import render_template, request, redirect, url_for, jsonify, send_from_directory, flash
from flask_login import login_required, current_user
from app import app, db
from models import Quotation
from utils.flexible_pdf_generator import generate_flexible_quotation_pdf, DEFAULT_ITEM_FIELDS, AVAILABLE_ITEM_FIELDS

# Configure logger
logger = logging.getLogger(__name__)

@app.route('/quotation/<int:quotation_id>/export/flexible', methods=['GET', 'POST'])
@login_required
def export_flexible_quotation(quotation_id):
    """
    Export a quotation as PDF with flexible field selection.
    
    GET: Show field selection form
    POST: Generate PDF with selected fields
    """
    try:
        # Get the quotation
        quotation = Quotation.query.get_or_404(quotation_id)
        
        if request.method == 'GET':
            # Render form to select fields
            return render_template(
                'flexible_quotation_form.html',
                quotation=quotation,
                default_fields=DEFAULT_ITEM_FIELDS,
                available_fields=AVAILABLE_ITEM_FIELDS,
                is_admin=getattr(current_user, 'is_admin', False)
            )
        else:
            # Process field selection
            selected_fields = request.form.getlist('fields')
            orientation = request.form.get('orientation', 'portrait')
            include_admin = request.form.get('include_admin') == 'yes' and getattr(current_user, 'is_admin', False)
            use_modern = request.form.get('style', 'modern') == 'modern'
            
            # Create directory for PDF output
            output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'flexible_quotations')
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate PDF using our flexible generator
            output_path = generate_flexible_quotation_pdf(
                quotation=quotation,
                selected_fields=selected_fields,
                upload_folder=output_dir,
                orientation=orientation,
                include_admin_fields=include_admin,
                use_modern_style=use_modern,
                debug=False
            )
            
            if not output_path:
                flash("Error generating PDF - please contact support", "danger")
                return redirect(url_for('view_quotation', quotation_id=quotation_id))
            
            # Return the PDF file
            filename = os.path.basename(output_path)
            return send_from_directory(directory=output_dir, path=filename, as_attachment=True)
            
    except Exception as e:
        logger.error(f"Error exporting flexible quotation PDF: {str(e)}")
        logger.error(traceback.format_exc())
        flash(f"Error generating PDF: {str(e)}", "danger")
        return redirect(url_for('view_quotation', quotation_id=quotation_id))

@app.route('/quotation/<int:quotation_id>/export/flexible-api', methods=['POST'])
@login_required
def export_flexible_quotation_api(quotation_id):
    """
    API endpoint to generate a flexible quotation PDF with JSON field configuration.
    
    POST: JSON payload with field configuration
    Returns: JSON with PDF URL or error
    """
    try:
        # Get the quotation
        quotation = Quotation.query.get_or_404(quotation_id)
        
        # Get JSON payload
        payload = request.get_json()
        if not payload:
            return jsonify({'error': 'No JSON payload provided'}), 400
            
        # Extract configuration
        selected_fields = payload.get('fields', None)
        orientation = payload.get('orientation', 'portrait')
        include_admin = payload.get('include_admin', False) and getattr(current_user, 'is_admin', False)
        use_modern = payload.get('style', 'modern') == 'modern'
        
        # Create directory for PDF output
        output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'flexible_quotations')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate PDF using our flexible generator
        output_path = generate_flexible_quotation_pdf(
            quotation=quotation,
            selected_fields=selected_fields,
            upload_folder=output_dir,
            orientation=orientation,
            include_admin_fields=include_admin,
            use_modern_style=use_modern,
            debug=False
        )
        
        if not output_path:
            return jsonify({'error': 'Failed to generate PDF'}), 500
        
        # Return the PDF URL
        filename = os.path.basename(output_path)
        pdf_url = url_for('download_flexible_quotation', filename=filename, _external=True)
        
        return jsonify({
            'success': True,
            'pdf_url': pdf_url,
            'filename': filename
        })
            
    except Exception as e:
        logger.error(f"Error in flexible quotation API: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/download/flexible-quotation/<filename>')
@login_required
def download_flexible_quotation(filename):
    """Download a generated flexible quotation PDF by filename"""
    output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'flexible_quotations')
    return send_from_directory(directory=output_dir, path=filename, as_attachment=True)

@app.route('/api/quotation-fields')
@login_required
def get_quotation_fields():
    """API endpoint to get available quotation fields"""
    fields = {
        'default': DEFAULT_ITEM_FIELDS,
        'available': [f for f in AVAILABLE_ITEM_FIELDS if not f.get('admin_only') or getattr(current_user, 'is_admin', False)]
    }
    return jsonify(fields)

# Function to register these routes in your main routes.py
def register_flexible_quotation_routes(app):
    """Register the flexible quotation PDF routes with your Flask app"""
    # The routes are already registered when this file is imported
    # This function is just for documentation clarity
    logger.info("Flexible quotation PDF routes registered")