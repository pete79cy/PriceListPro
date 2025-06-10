"""
Migration script to add internal_notes field to Quotation model.

This script adds an internal_notes column to the quotation table
to store internal communication notes about customer interactions.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def run_migration():
    """Add internal_notes field to Quotation table"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("Error: DATABASE_URL environment variable not set")
        return False
    
    try:
        # Create database engine
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            # Check if the column already exists
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'quotation' 
                AND column_name = 'internal_notes'
            """))
            
            if result.fetchone():
                print("Column 'internal_notes' already exists in quotation table")
                return True
            
            # Add the internal_notes column
            print("Adding internal_notes column to quotation table...")
            connection.execute(text("""
                ALTER TABLE quotation 
                ADD COLUMN internal_notes TEXT
            """))
            
            # Commit the transaction
            connection.commit()
            print("Successfully added internal_notes column to quotation table")
            return True
            
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)