"""
Database optimization script to add indexes for faster product search.
This script creates database indexes to improve search performance.
"""

import os
import sys
from sqlalchemy import text

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def create_search_indexes():
    """Create database indexes to optimize product search performance"""
    
    indexes_to_create = [
        # Product table indexes for text search
        "CREATE INDEX IF NOT EXISTS idx_product_name_gin ON product USING gin(to_tsvector('english', name))",
        "CREATE INDEX IF NOT EXISTS idx_product_name_like ON product (name varchar_pattern_ops)",
        "CREATE INDEX IF NOT EXISTS idx_product_scientific_name ON product (scientific_name varchar_pattern_ops)",
        "CREATE INDEX IF NOT EXISTS idx_product_category ON product (category varchar_pattern_ops)",
        "CREATE INDEX IF NOT EXISTS idx_product_sku ON product (sku varchar_pattern_ops)",
        
        # SupplierProduct table indexes
        "CREATE INDEX IF NOT EXISTS idx_supplier_product_name_gin ON supplier_product USING gin(to_tsvector('english', product_name))",
        "CREATE INDEX IF NOT EXISTS idx_supplier_product_name_like ON supplier_product (product_name varchar_pattern_ops)",
        "CREATE INDEX IF NOT EXISTS idx_supplier_product_scientific_name ON supplier_product (scientific_name varchar_pattern_ops)",
        
        # PriceList table indexes for JOIN optimization
        "CREATE INDEX IF NOT EXISTS idx_price_list_customer_product ON price_list (customer_id, product_id)",
        "CREATE INDEX IF NOT EXISTS idx_price_list_product_customer ON price_list (product_id, customer_id)",
        
        # Composite indexes for common queries
        "CREATE INDEX IF NOT EXISTS idx_product_active_search ON product (name, scientific_name, category) WHERE name IS NOT NULL",
    ]
    
    print("Creating database indexes for optimized product search...")
    
    with app.app_context():
        try:
            for index_sql in indexes_to_create:
                print(f"Creating index: {index_sql.split('idx_')[1].split(' ')[0] if 'idx_' in index_sql else 'unnamed'}")
                db.session.execute(text(index_sql))
            
            db.session.commit()
            print("✅ All search indexes created successfully!")
            
            # Analyze tables to update statistics
            print("Updating table statistics...")
            db.session.execute(text("ANALYZE product"))
            db.session.execute(text("ANALYZE supplier_product"))
            db.session.execute(text("ANALYZE price_list"))
            db.session.commit()
            print("✅ Table statistics updated!")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating indexes: {str(e)}")
            db.session.rollback()
            return False

def check_existing_indexes():
    """Check what indexes already exist on the relevant tables"""
    
    check_queries = [
        """
        SELECT schemaname, tablename, indexname, indexdef 
        FROM pg_indexes 
        WHERE tablename IN ('product', 'supplier_product', 'price_list')
        ORDER BY tablename, indexname
        """,
    ]
    
    print("Checking existing indexes...")
    
    with app.app_context():
        try:
            result = db.session.execute(text(check_queries[0]))
            indexes = result.fetchall()
            
            current_table = None
            for schema, table, index_name, index_def in indexes:
                if table != current_table:
                    print(f"\n{table.upper()} table indexes:")
                    current_table = table
                print(f"  - {index_name}")
            
            print(f"\nFound {len(indexes)} total indexes on search-related tables")
            return indexes
            
        except Exception as e:
            print(f"❌ Error checking indexes: {str(e)}")
            return []

def main():
    """Main function to run the optimization"""
    print("=== Product Search Performance Optimization ===\n")
    
    # Check existing indexes
    existing_indexes = check_existing_indexes()
    
    print("\n" + "="*50)
    
    # Create new indexes
    success = create_search_indexes()
    
    if success:
        print("\n✅ Search optimization completed successfully!")
        print("\nExpected improvements:")
        print("- Faster text-based product searches")
        print("- Improved customer-specific pricing lookups") 
        print("- Better performance for autocomplete functionality")
        print("- Reduced database load during peak usage")
    else:
        print("\n❌ Search optimization failed!")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)