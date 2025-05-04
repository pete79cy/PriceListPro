#!/usr/bin/env python
"""
Apply database migration for import logs table.

This script applies the SQL migration defined in migrations/20250505_add_import_logs.sql
to add the import_logs table to the database.
"""
import os
import logging
import subprocess
from app import app, db

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('migration')

def apply_migration(migration_file):
    """
    Apply a SQL migration file to the database
    
    Args:
        migration_file: Path to the SQL migration file
        
    Returns:
        bool: True if migration successful, False otherwise
    """
    try:
        # Get the database URL from environment or app config
        database_url = os.environ.get("DATABASE_URL") or app.config.get("SQLALCHEMY_DATABASE_URI")
        if not database_url:
            logger.error("Database URL not found in environment or app config")
            return False
            
        # Check if migration file exists
        if not os.path.exists(migration_file):
            logger.error(f"Migration file not found: {migration_file}")
            return False
            
        logger.info(f"Applying migration: {migration_file}")
        
        # Apply migration using psql
        result = subprocess.run(
            ["psql", database_url, "-f", migration_file],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"Migration applied successfully")
            logger.info(f"Output: {result.stdout}")
            return True
        else:
            logger.error(f"Error applying migration: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error applying migration: {str(e)}")
        return False

def main():
    """
    Apply migrations and create Python model
    """
    # Path to migration file
    migration_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                               "migrations", "20250505_add_import_logs.sql")
    
    # Apply migration
    success = apply_migration(migration_file)
    if success:
        # Check if model exists and can connect to the database
        with app.app_context():
            try:
                from models import ImportLog
                logger.info("ImportLog model exists, checking database...")
                
                # Try to execute a simple query
                db.session.execute(db.select(ImportLog).limit(1))
                logger.info("ImportLog table exists and is accessible")
                return 0
            except Exception as e:
                logger.error(f"Error accessing ImportLog table: {str(e)}")
                return 1
    else:
        logger.error("Migration failed. Check the error logs.")
        return 1

if __name__ == "__main__":
    exit(main())
