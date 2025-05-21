"""
Fix OrderItem schema issues in the PostgreSQL database.

This script directly modifies the database schema to add the missing price_list_id column.
"""
import os
import psycopg2
from psycopg2 import sql

def run_migration():
    """Add price_list_id column to the order_item table"""
    # Get PostgreSQL connection details from environment
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL environment variable not set")
        return False
    
    conn = None
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Check if the column exists
        check_sql = """
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = 'order_item' AND column_name = 'price_list_id'
        );
        """
        cur.execute(check_sql)
        column_exists = cur.fetchone()[0]
        
        if not column_exists:
            print("Adding price_list_id column to order_item table...")
            # Add the column
            add_column_sql = """
            ALTER TABLE order_item 
            ADD COLUMN price_list_id INTEGER REFERENCES price_list(id);
            """
            cur.execute(add_column_sql)
            print("Successfully added price_list_id column to order_item table")
        else:
            print("price_list_id column already exists in order_item table")
        
        # Close the cursor and connection
        cur.close()
        return True
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    print("Starting OrderItem schema fix...")
    success = run_migration()
    print("Migration completed" if success else "Migration failed")