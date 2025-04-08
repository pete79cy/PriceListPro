"""
Debug routes to help fix the missing item #14 issue in quotation PDFs.
Add these routes to your main routes.py file.
"""

from flask import send_from_directory, redirect, url_for, flash, request
from flask_login import login_required
from app import app, db
from models import Quotation
from utils.enhanced_pdf_generator import generate_enhanced_pdf
import os
import traceback
from utils.logger import logger

# Add these route functions to your routes.py file

@app.route('/quotation/<int:quotation_id>/export/fixed')
@login_required
def export_quotation_fixed(quotation_id):
    """Export a quotation as PDF using the enhanced generator to fix missing items"""
    quotation = Quotation.query.get_or_404(quotation_id)
    
    try:
        # Generate the PDF using enhanced generator
        pdf_path = generate_enhanced_pdf(quotation, app.config['UPLOAD_FOLDER'], use_modern_template=True)
        
        # Send the file to the client
        return send_from_directory(
            directory=app.config['UPLOAD_FOLDER'],
            path=os.path.basename(pdf_path),
            as_attachment=True,
            download_name=f"Fixed_Quotation_{quotation.quotation_number}.pdf"
        )
        
    except Exception as e:
        logger.error(f"Error exporting quotation with enhanced generator: {str(e)}")
        logger.error(traceback.format_exc())
        flash(f"Error generating fixed PDF: {str(e)}", 'danger')
        return redirect(url_for('view_quotation', quotation_id=quotation_id))

@app.route('/quotation/<int:quotation_id>/export/debug')
@login_required
def export_quotation_debug(quotation_id):
    """Export a quotation with debug visuals to identify missing items"""
    quotation = Quotation.query.get_or_404(quotation_id)
    
    try:
        # Generate the PDF using enhanced generator with debug mode
        pdf_path = generate_enhanced_pdf(quotation, app.config['UPLOAD_FOLDER'], 
                                         use_modern_template=True, debug=True)
        
        # Send the file to the client
        return send_from_directory(
            directory=app.config['UPLOAD_FOLDER'],
            path=os.path.basename(pdf_path),
            as_attachment=True,
            download_name=f"Debug_Quotation_{quotation.quotation_number}.pdf"
        )
        
    except Exception as e:
        logger.error(f"Error exporting debug quotation: {str(e)}")
        logger.error(traceback.format_exc())
        flash(f"Error generating debug PDF: {str(e)}", 'danger')
        return redirect(url_for('view_quotation', quotation_id=quotation_id))