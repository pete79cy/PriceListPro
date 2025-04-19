#!/usr/bin/env python
"""
Scheduled Database Backup Script

This script is designed to be run via a scheduler (e.g., cron) to create 
regular database backups. It automatically removes old backups to save space.

Example usage:
    # Create a daily backup at 2:00 AM and keep last 7 backups
    0 2 * * * /path/to/python /path/to/scheduled_backup.py --keep 7
"""
import os
import sys
import argparse
import logging
from datetime import datetime
from db_backup_tool import DatabaseBackupTool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scheduled_backup.log')
    ]
)
logger = logging.getLogger('scheduled_backup')

def main():
    """Run scheduled backup process."""
    parser = argparse.ArgumentParser(description='Create scheduled database backup')
    parser.add_argument('--keep', type=int, default=10, 
                        help='Number of most recent backups to keep')
    parser.add_argument('--description', type=str,
                        help='Optional description for this backup')
    args = parser.parse_args()
    
    # Validate args
    if args.keep < 1:
        logger.warning("Invalid value for 'keep'. Using default of 10.")
        args.keep = 10
    
    # Set default description if not provided
    if not args.description:
        args.description = f"Scheduled backup - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    logger.info(f"Starting scheduled backup. Will keep last {args.keep} backups.")
    
    try:
        # Create backup tool instance
        tool = DatabaseBackupTool()
        
        # Create backup
        backup_path = tool.create_backup(args.description)
        
        if backup_path:
            logger.info(f"Backup created successfully: {backup_path}")
            
            # Clean up old backups
            deleted = tool.clean_old_backups(keep=args.keep)
            logger.info(f"Cleaned up {deleted} old backup(s)")
            
            return 0  # Success
        else:
            logger.error("Backup creation failed")
            return 1  # Error
    
    except Exception as e:
        logger.error(f"Backup process failed with error: {str(e)}")
        return 1  # Error

if __name__ == "__main__":
    sys.exit(main())