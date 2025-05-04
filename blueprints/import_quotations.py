"""Blueprint for quotation import feature

This blueprint provides routes for importing quotations from external sources.
It is feature-flagged for controlled rollout.
"""
import os
import json
import uuid
import logging
import traceback
from datetime import datetime
from flask import (
    Blueprint, render_template, request, flash, redirect, 
    url_for, current_app, jsonify, session
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from models import Quotation, QuotationItem, Customer, ImportLog
from utils.feature_flags import is_feature_enabled
from utils.rollback import prepare_rollback_data, perform_rollback

# Configure logging
logger = logging.getLogger(__name__)

# Create the blueprint
import_quotations_bp = Blueprint('import_quotations', __name__)

# Guard all routes with feature flag
@import_quotations_bp.before_request
def check_feature_flag():
    """Check if the quotation import feature is enabled"""
    if not is_feature_enabled('QUOTATION_IMPORT'):
        # Feature is disabled, return 404
        flash('The requested feature is not available.', 'warning')
        return redirect(url_for('quotations'))

@import_quotations_bp.route('/import', methods=['GET'])
@login_required
def import_quotations():
    """Display the import quotations page"""
    # Clear any data from previous imports
    if 'quotation_data' in session:
        del session['quotation_data']
    
    customers = Customer.query.order_by(Customer.name).all()
    return render_template('import_quotations.html', customers=customers)

@import_quotations_bp.route('/import/upload', methods=['POST'])
@login_required
def upload_import_file():
    """Handle file upload and initial processing"""
    try:
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(url_for('import_quotations.import_quotations'))
            
        file = request.files['file']
        customer_id = request.form.get('customer_id')
        file_type = request.form.get('file_type')
        
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('import_quotations.import_quotations'))
            
        if not customer_id:
            flash('Please select a customer', 'danger')
            return redirect(url_for('import_quotations.import_quotations'))
            
        # Create an import log entry
        import_log = ImportLog(
            filename=file.filename,
            import_type=f'quotation_{file_type}',
            imported_by=current_user.id,
            status='pending'
        )
        db.session.add(import_log)
        db.session.commit()
        
        # Generate unique filename and save file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Process the file and store data in session
        # This will be expanded in the complete implementation
        session['import_file_path'] = file_path
        session['import_customer_id'] = customer_id
        session['import_log_id'] = import_log.id
        
        flash('File uploaded successfully. Please review and confirm the import.', 'success')
        return redirect(url_for('import_quotations.review_import'))
        
    except Exception as e:
        logger.error(f"Error uploading import file: {str(e)}")
        logger.error(traceback.format_exc())
        flash(f"Error uploading file: {str(e)}", 'danger')
        return redirect(url_for('import_quotations.import_quotations'))

@import_quotations_bp.route('/import/review', methods=['GET'])
@login_required
def review_import():
    """Review imported data before final import"""
    # Check if we have import data in session
    if not all(key in session for key in ['import_file_path', 'import_customer_id', 'import_log_id']):
        flash('No import data available. Please upload a file first.', 'warning')
        return redirect(url_for('import_quotations.import_quotations'))
    
    # In the complete implementation, we would parse the file here
    # For now, just display a placeholder
    customer = Customer.query.get(session['import_customer_id'])
    if not customer:
        flash('Customer not found', 'danger')
        return redirect(url_for('import_quotations.import_quotations'))
        
    return render_template('review_import.html', 
                           customer=customer, 
                           file_path=session['import_file_path'])

@import_quotations_bp.route('/import/confirm', methods=['POST'])
@login_required
def confirm_import():
    """Confirm and finalize the import"""
    # Check if we have import data in session
    if not all(key in session for key in ['import_file_path', 'import_customer_id', 'import_log_id']):
        flash('No import data available. Please upload a file first.', 'warning')
        return redirect(url_for('import_quotations.import_quotations'))
    
    try:
        # Get the import log
        import_log = ImportLog.query.get(session['import_log_id'])
        if not import_log:
            flash('Import log not found', 'danger')
            return redirect(url_for('import_quotations.import_quotations'))
            
        # In the complete implementation, we would process the data here
        # For now, just update the import log
        import_log.status = 'success'
        import_log.success_count = 1
        db.session.commit()
        
        # Clear session data
        for key in ['import_file_path', 'import_customer_id', 'import_log_id']:
            if key in session:
                del session[key]
        
        flash('Import completed successfully!', 'success')
        return redirect(url_for('quotations'))
        
    except Exception as e:
        logger.error(f"Error confirming import: {str(e)}")
        logger.error(traceback.format_exc())
        flash(f"Error during import: {str(e)}", 'danger')
        
        # Mark the import as failed
        if 'import_log_id' in session:
            try:
                import_log = ImportLog.query.get(session['import_log_id'])
                if import_log:
                    import_log.status = 'failed'
                    import_log.error_message = str(e)
                    db.session.commit()
            except Exception as log_err:
                logger.error(f"Error updating import log: {str(log_err)}")
        
        return redirect(url_for('import_quotations.import_quotations'))

@import_quotations_bp.route('/import/rollback/<int:import_log_id>', methods=['POST'])
@login_required
def rollback_import(import_log_id):
    """Rollback an import"""
    try:
        # Check if the import log exists
        import_log = ImportLog.query.get_or_404(import_log_id)
        
        # Only allow rollback of successful or partially successful imports
        if import_log.status not in ['success', 'partial']:
            flash('Cannot rollback this import', 'warning')
            return redirect(url_for('quotations'))
            
        # Perform the rollback
        if perform_rollback(import_log_id):
            flash('Import successfully rolled back', 'success')
        else:
            flash('Error rolling back the import', 'danger')
            
        return redirect(url_for('quotations'))
        
    except Exception as e:
        logger.error(f"Error rolling back import: {str(e)}")
        logger.error(traceback.format_exc())
        flash(f"Error rolling back import: {str(e)}", 'danger')
        return redirect(url_for('quotations'))

@import_quotations_bp.route('/import/logs', methods=['GET'])
@login_required
def view_import_logs():
    """View import logs"""
    logs = ImportLog.query.order_by(ImportLog.created_at.desc()).all()
    return render_template('import_logs.html', logs=logs)
