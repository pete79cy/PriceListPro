"""
Database cleanup utilities for the plant pricing system.
Provides functions to manage and clean up database records.
"""

import os
import logging
from datetime import datetime

from app import db
from models import Invoice, InvoiceItem, FileUpload

# Set up logger
logger = logging.getLogger('plant_pricing_system')

def delete_all_invoices():
    """
    Delete all invoices and related records from the database.
    
    Returns:
        tuple: (success, message, deleted_count)
    """
    try:
        # Get a list of all invoice files to delete
        invoices = Invoice.query.all()
        file_paths = [inv.file_path for inv in invoices if inv.file_path]
        
        # Count of items to be deleted
        invoice_count = len(invoices)
        
        # Delete invoice items first
        item_count = InvoiceItem.query.delete()
        
        # Then delete invoices
        Invoice.query.delete()
        
        # Delete upload records related to invoices
        upload_count = FileUpload.query.filter_by(file_type='pdf').delete()
        
        # Commit the changes
        db.session.commit()
        
        # Delete files from disk
        files_deleted = 0
        for file_path in file_paths:
            try:
                os.remove(file_path)
                files_deleted += 1
            except (OSError, FileNotFoundError) as e:
                logger.warning(f"Could not delete file at {file_path}: {str(e)}")
        
        message = f"Successfully deleted {invoice_count} invoices, {item_count} invoice items, and {upload_count} upload records. Removed {files_deleted} files from storage."
        logger.info(message)
        
        return True, message, invoice_count
    except Exception as e:
        db.session.rollback()
        error_message = f"Error deleting invoices: {str(e)}"
        logger.error(error_message)
        return False, error_message, 0