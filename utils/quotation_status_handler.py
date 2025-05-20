"""
Quotation Status Handler Utility

This module provides functionality for managing quotation statuses,
including automatic expiration handling and other status-related utilities.
"""

import logging
from datetime import datetime, timedelta
from app import db
from models import Quotation, QuotationStatus

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_expired_quotations():
    """
    Check for quotations that have passed their valid_until date
    and automatically mark them as expired.
    
    Returns:
        int: Number of quotations marked as expired
    """
    try:
        # Get current date
        today = datetime.utcnow().date()
        
        # Find quotations that should be expired
        expired_quotations = Quotation.query.filter(
            Quotation.valid_until < today,
            Quotation.status.in_([QuotationStatus.SUBMITTED, QuotationStatus.UNDER_REVIEW])
        ).all()
        
        count = 0
        for quotation in expired_quotations:
            # Set to expired if the transition is allowed
            if quotation.transition_to(QuotationStatus.EXPIRED):
                count += 1
                logger.info(f"Marked quotation {quotation.quotation_number} as expired (valid until: {quotation.valid_until})")
        
        if count > 0:
            db.session.commit()
            logger.info(f"Expired {count} quotations")
        
        return count
    except Exception as e:
        logger.error(f"Error checking expired quotations: {str(e)}")
        db.session.rollback()
        return 0

def get_quotation_statistics():
    """
    Get statistics about quotations by status
    
    Returns:
        dict: Counts by status and other stats
    """
    try:
        stats = {}
        
        # Total quotations
        stats['total'] = Quotation.query.count()
        
        # Quotations by status
        for status in QuotationStatus.LABELS.keys():
            count = Quotation.query.filter_by(status=status).count()
            stats[status.lower()] = count
        
        # Quotations expiring soon (next 7 days)
        today = datetime.utcnow().date()
        next_week = today + timedelta(days=7)
        stats['expiring_soon'] = Quotation.query.filter(
            Quotation.valid_until.between(today, next_week),
            Quotation.status.in_([QuotationStatus.SUBMITTED, QuotationStatus.UNDER_REVIEW])
        ).count()
        
        # Recent activity
        stats['recently_accepted'] = Quotation.query.filter(
            Quotation.status == QuotationStatus.ACCEPTED,
            Quotation.accepted_at >= (datetime.utcnow() - timedelta(days=7))
        ).count()
        
        # Conversion rate (accepted / (accepted + rejected))
        accepted = stats.get(QuotationStatus.ACCEPTED.lower(), 0)
        rejected = stats.get(QuotationStatus.REJECTED.lower(), 0)
        
        if (accepted + rejected) > 0:
            stats['conversion_rate'] = round(accepted / (accepted + rejected) * 100, 1)
        else:
            stats['conversion_rate'] = 0
            
        return stats
        
    except Exception as e:
        logger.error(f"Error getting quotation statistics: {str(e)}")
        return {
            'total': Quotation.query.count(),
            'error': str(e)
        }