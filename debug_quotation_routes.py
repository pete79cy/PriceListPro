"""
Debug routes to help fix the missing item #10 issue in quotation PDFs.
Add these routes to your main routes.py file.
"""

import os
import traceback
import logging
from flask import send_from_directory, flash, redirect, url_for
from flask_login import login_required
from app import app, db
from models import Quotation
from utils.enhanced_pdf_generator_v2 import generate_quotation_pdf_v2

logger = logging.getLogger(__name__)

@app.route('/quotation/<int:quotation_id>/export/fixed-v2')
@login_required
def export_quotation_fixed_v2(quotation_id):
    """Export a quotation as PDF using the enhanced generator to fix missing items"""
    quotation = Quotation.query.get_or_404(quotation_id)
    
    try:
        # Generate the PDF using enhanced generator with item #10 fixes
        pdf_path = generate_quotation_pdf_v2(
            quotation, 
            app.config['UPLOAD_FOLDER'], 
            use_modern_template=True,
            debug=False
        )
        
        # Send the file to the client
        return send_from_directory(
            directory=app.config['UPLOAD_FOLDER'],
            path=os.path.basename(pdf_path),
            as_attachment=True,
            download_name=f"Fixed_Quotation_{quotation.quotation_number}.pdf"
        )
        
    except Exception as e:
        logger.error(f"Error exporting quotation with enhanced generator v2: {str(e)}")
        logger.error(traceback.format_exc())
        flash(f"Error generating fixed PDF: {str(e)}", 'danger')
        return redirect(url_for('view_quotation', quotation_id=quotation_id))

@app.route('/quotation/<int:quotation_id>/export/debug-v2')
@login_required
def export_quotation_debug_v2(quotation_id):
    """Export a quotation with debug visuals to identify missing item #10"""
    quotation = Quotation.query.get_or_404(quotation_id)
    
    try:
        # Generate the PDF with debugging features and item #10 highlighting
        pdf_path = generate_quotation_pdf_v2(
            quotation, 
            app.config['UPLOAD_FOLDER'], 
            use_modern_template=True,
            debug=True
        )
        
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

# Add these routes to the main routes.py file