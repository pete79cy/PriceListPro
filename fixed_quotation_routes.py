"""
Routes for generating fixed quotation PDFs that address all known issues:
1. Missing items (esp. #10, #14) in the output
2. HTML entity encoding in headers (like &amp; instead of &)
3. Layout and spacing problems
4. VAT calculation display for multiple rates

Add these routes to your routes.py file.
"""

import os
import traceback
import logging
from flask import send_from_directory, flash, redirect, url_for
from flask_login import login_required
from app import app, db
from models import Quotation
from utils.fixed_pdf_generator import generate_fixed_quotation_pdf

# Configure logger
logger = logging.getLogger(__name__)

@app.route('/quotation/<int:quotation_id>/export/fixed')
@login_required
def export_quotation_fixed(quotation_id):
    """Export a quotation as PDF using the fixed generator to solve all known issues"""
    try:
        # Get the quotation
        quotation = Quotation.query.get_or_404(quotation_id)
        
        # Create directory for PDF output
        output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'fixed_quotations')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate PDF using our fixed generator
        output_path = generate_fixed_quotation_pdf(
            quotation=quotation,
            upload_folder=output_dir,
            use_modern_template=True,
            debug=False
        )
        
        if not output_path:
            flash("Error generating PDF - please contact support", "danger")
            return redirect(url_for('view_quotation', quotation_id=quotation_id))
        
        # Return the PDF file
        filename = os.path.basename(output_path)
        return send_from_directory(directory=output_dir, path=filename, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error exporting fixed quotation PDF: {str(e)}")
        logger.error(traceback.format_exc())
        flash(f"Error generating PDF: {str(e)}", "danger")
        return redirect(url_for('view_quotation', quotation_id=quotation_id))

@app.route('/quotation/<int:quotation_id>/export/fixed-debug')
@login_required
def export_quotation_fixed_debug(quotation_id):
    """Export a quotation with debug visuals to identify rendering issues"""
    try:
        # Get the quotation
        quotation = Quotation.query.get_or_404(quotation_id)
        
        # Create directory for PDF output
        output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'fixed_quotations')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate PDF using our fixed generator with debug mode enabled
        output_path = generate_fixed_quotation_pdf(
            quotation=quotation,
            upload_folder=output_dir,
            use_modern_template=True,
            debug=True
        )
        
        if not output_path:
            flash("Error generating debug PDF - please contact support", "danger")
            return redirect(url_for('view_quotation', quotation_id=quotation_id))
        
        # Return the PDF file
        filename = os.path.basename(output_path)
        return send_from_directory(directory=output_dir, path=filename, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error exporting fixed debug quotation PDF: {str(e)}")
        logger.error(traceback.format_exc())
        flash(f"Error generating debug PDF: {str(e)}", "danger")
        return redirect(url_for('view_quotation', quotation_id=quotation_id))

# Function to register these routes in your main routes.py
def register_fixed_quotation_routes(app):
    """Register the fixed quotation PDF routes with your Flask app"""
    # The routes are already registered when this file is imported
    # This function is just for documentation clarity
    logger.info("Fixed quotation PDF routes registered")