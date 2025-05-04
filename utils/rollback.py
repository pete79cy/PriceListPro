"""Rollback utilities for safely undoing imported data

This module provides functions to rollback imported data in case of errors,
ensuring data consistency and maintaining integrity of the database.
"""
import json
import logging
from app import db
from models import ImportLog, Quotation, QuotationItem

logger = logging.getLogger(__name__)

def prepare_rollback_data(data_type, entity_ids):
    """
    Prepare rollback data by capturing the current state of entities
    
    Args:
        data_type: Type of data being prepared for rollback (e.g., 'quotation')
        entity_ids: List of entity IDs to prepare rollback data for
        
    Returns:
        str: JSON string with rollback data
    """
    try:
        rollback_data = {
            'data_type': data_type,
            'entities': []
        }
        
        if data_type == 'quotation':
            for quotation_id in entity_ids:
                quotation = Quotation.query.get(quotation_id)
                if not quotation:
                    continue
                    
                # Capture quotation data
                quotation_data = {
                    'id': quotation.id,
                    'customer_id': quotation.customer_id,
                    'quotation_number': quotation.quotation_number,
                    'items': []
                }
                
                # Capture items data
                for item in quotation.items:
                    item_data = {
                        'id': item.id,
                        'quotation_id': item.quotation_id,
                        'product_id': item.product_id,
                        'description': item.description,
                        'quantity': item.quantity,
                        'selling_price': item.selling_price,
                        'position': item.position
                    }
                    quotation_data['items'].append(item_data)
                    
                rollback_data['entities'].append(quotation_data)
        
        return json.dumps(rollback_data)
    except Exception as e:
        logger.error(f"Error preparing rollback data: {str(e)}")
        return json.dumps({'error': str(e)})

def perform_rollback(import_log_id):
    """
    Perform rollback based on stored rollback data
    
    Args:
        import_log_id: ID of the import log to rollback
        
    Returns:
        bool: True if rollback successful, False otherwise
    """
    try:
        # Get the import log
        import_log = ImportLog.query.get(import_log_id)
        if not import_log or not import_log.rollback_data:
            logger.error(f"No rollback data available for import log {import_log_id}")
            return False
            
        # Parse rollback data
        rollback_data = json.loads(import_log.rollback_data)
        
        if rollback_data.get('data_type') == 'quotation':
            # For new quotations, we just delete them
            for quotation_data in rollback_data.get('entities', []):
                # Delete quotation (cascade will handle items)
                quotation = Quotation.query.get(quotation_data['id'])
                if quotation:
                    db.session.delete(quotation)
                    logger.info(f"Deleted quotation: {quotation.quotation_number} (ID: {quotation.id})")
        
        # Update import log status
        import_log.status = 'rolled_back'
        db.session.commit()
        
        logger.info(f"Successfully rolled back import {import_log_id}")
        return True
    except Exception as e:
        logger.error(f"Error during rollback of import {import_log_id}: {str(e)}")
        db.session.rollback()
        return False
