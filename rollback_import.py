#!/usr/bin/env python
"""
Rollback Import Tool

This script provides a command-line interface for rolling back imports
that may have caused data issues. It works with the ImportLog model
to identify and revert potentially problematic imports.
"""
import sys
import json
import logging
import argparse
from datetime import datetime, timedelta
from app import app, db
from models import ImportLog, Quotation, QuotationItem
from utils.rollback import perform_rollback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('rollback_import')

def list_recent_imports(days=7, status=None):
    """
    List recent imports from the ImportLog table
    
    Args:
        days: Number of days to look back
        status: Filter by status, or None for all
        
    Returns:
        list: List of ImportLog objects
    """
    try:
        with app.app_context():
            # Build query
            query = db.select(ImportLog)
            
            if days:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                query = query.where(ImportLog.created_at >= cutoff_date)
                
            if status:
                query = query.where(ImportLog.status == status)
                
            # Execute query and get results
            logs = db.session.execute(query).scalars().all()
            return logs
            
    except Exception as e:
        logger.error(f"Error listing imports: {str(e)}")
        return []

def rollback_import_by_id(import_id):
    """
    Roll back an import by its ID
    
    Args:
        import_id: ID of the import to roll back
        
    Returns:
        bool: True if rollback successful, False otherwise
    """
    try:
        with app.app_context():
            # Perform the rollback
            success = perform_rollback(import_id)
            
            if success:
                logger.info(f"Successfully rolled back import {import_id}")
            else:
                logger.error(f"Failed to roll back import {import_id}")
                
            return success
            
    except Exception as e:
        logger.error(f"Error during rollback of import {import_id}: {str(e)}")
        return False

def main():
    """
    Command-line interface for the rollback tool
    """
    parser = argparse.ArgumentParser(description='Roll back imports')
    parser.add_argument('--list', action='store_true', help='List recent imports')
    parser.add_argument('--days', type=int, default=7, help='Number of days to look back')
    parser.add_argument('--status', help='Filter by status (e.g., success, partial, failed)')
    parser.add_argument('--rollback', type=int, help='Roll back a specific import by ID')
    
    args = parser.parse_args()
    
    if args.list:
        imports = list_recent_imports(days=args.days, status=args.status)
        
        if imports:
            print(f"\nRecent imports (last {args.days} days):")
            print("-" * 80)
            print(f"{'ID':<5} {'Status':<12} {'Date':<20} {'Type':<20} {'Filename':<30}")
            print("-" * 80)
            
            for imp in imports:
                date_str = imp.created_at.strftime('%Y-%m-%d %H:%M:%S')
                print(f"{imp.id:<5} {imp.status:<12} {date_str:<20} {imp.import_type:<20} {imp.filename[:30]:<30}")
                
            print("\nTo roll back an import: python rollback_import.py --rollback [ID]")
        else:
            print(f"No imports found in the last {args.days} days")
            
        return 0
        
    elif args.rollback is not None:
        print(f"Rolling back import {args.rollback}...")
        success = rollback_import_by_id(args.rollback)
        
        if success:
            print(f"Successfully rolled back import {args.rollback}")
            return 0
        else:
            print(f"Failed to roll back import {args.rollback}")
            return 1
            
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())
