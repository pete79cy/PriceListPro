"""
Enhanced Quotation PDF Routes

This module provides routes for generating quotation PDFs with advanced WeasyPrint pagination control.
These routes implement a complete solution to the missing row issues by:
1. Using better CSS controls for page breaks
2. Implementing item pagination to ensure proper layout
3. Providing debug options for troubleshooting

Add these routes to your routes.py file.
"""

import os
import traceback
import logging
from flask import send_from_directory, flash, redirect, url_for
from flask_login import login_required
from app import app, db
from models import Quotation
from utils.enhanced_weasprint_pdf_generator import generate_enhanced_quotation_pdf

# Configure logger
logger = logging.getLogger(__name__)

@app.route('/quotation/<int:quotation_id>/export/enhanced')
@login_required
def export_quotation_enhanced(quotation_id):
    """Export a quotation as PDF using the enhanced WeasyPrint generator with pagination control"""
    try:
        # Get the quotation
        quotation = Quotation.query.get_or_404(quotation_id)
        
        # Create directory for PDF output
        output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'enhanced_quotations')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate PDF using our enhanced generator
        output_path = generate_enhanced_quotation_pdf(
            quotation=quotation,
            upload_folder=output_dir,
            use_modern_template=True,
            debug=False,
            paginate=True
        )
        
        if not output_path:
            flash("Error generating PDF - please contact support", "danger")
            return redirect(url_for('view_quotation', quotation_id=quotation_id))
        
        # Return the PDF file
        filename = os.path.basename(output_path)
        return send_from_directory(directory=output_dir, path=filename, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error exporting enhanced quotation PDF: {str(e)}")
        logger.error(traceback.format_exc())
        flash(f"Error generating PDF: {str(e)}", "danger")
        return redirect(url_for('view_quotation', quotation_id=quotation_id))

@app.route('/quotation/<int:quotation_id>/export/enhanced-debug')
@login_required
def export_quotation_enhanced_debug(quotation_id):
    """Export a quotation with debug visuals to identify rendering issues"""
    try:
        # Get the quotation
        quotation = Quotation.query.get_or_404(quotation_id)
        
        # Create directory for PDF output
        output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'enhanced_quotations')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate PDF using our enhanced generator with debug mode enabled
        output_path = generate_enhanced_quotation_pdf(
            quotation=quotation,
            upload_folder=output_dir,
            use_modern_template=True,
            debug=True,
            paginate=True
        )
        
        if not output_path:
            flash("Error generating debug PDF - please contact support", "danger")
            return redirect(url_for('view_quotation', quotation_id=quotation_id))
        
        # Return the PDF file
        filename = os.path.basename(output_path)
        return send_from_directory(directory=output_dir, path=filename, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error exporting enhanced debug quotation PDF: {str(e)}")
        logger.error(traceback.format_exc())
        flash(f"Error generating debug PDF: {str(e)}", "danger")
        return redirect(url_for('view_quotation', quotation_id=quotation_id))

@app.route('/quotation/<int:quotation_id>/export/enhanced-nopaginate')
@login_required
def export_quotation_enhanced_nopaginate(quotation_id):
    """Export a quotation using enhanced CSS without explicit pagination"""
    try:
        # Get the quotation
        quotation = Quotation.query.get_or_404(quotation_id)
        
        # Create directory for PDF output
        output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'enhanced_quotations')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate PDF using our enhanced generator without pagination
        output_path = generate_enhanced_quotation_pdf(
            quotation=quotation,
            upload_folder=output_dir,
            use_modern_template=True,
            debug=False,
            paginate=False
        )
        
        if not output_path:
            flash("Error generating PDF - please contact support", "danger")
            return redirect(url_for('view_quotation', quotation_id=quotation_id))
        
        # Return the PDF file
        filename = os.path.basename(output_path)
        return send_from_directory(directory=output_dir, path=filename, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error exporting enhanced quotation PDF: {str(e)}")
        logger.error(traceback.format_exc())
        flash(f"Error generating PDF: {str(e)}", "danger")
        return redirect(url_for('view_quotation', quotation_id=quotation_id))

# Function to register all enhanced routes in your main routes.py file
def register_enhanced_quotation_routes(app):
    """
    Register the enhanced quotation routes in your application.
    Call this function in your app.py after registering all other blueprints.
    
    Example:
        from enhanced_quotation_routes import register_enhanced_quotation_routes
        register_enhanced_quotation_routes(app)
    """
    # Routes are already registered via @app.route decorators
    logger.info("Enhanced quotation routes registered successfully")
    
    return True