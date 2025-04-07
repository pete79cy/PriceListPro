"""
Script to update the QuotationItem table in the database by adding supplier_id column.
"""
from app import app, db
from sqlalchemy import text

def add_supplier_id_column():
    """Add supplier_id column to quotation_item table if it doesn't exist"""
    with app.app_context():
        # Check if the column exists
        query = text("""
        SELECT EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name='quotation_item' AND column_name='supplier_id'
        );
        """)
        
        result = db.session.execute(query).scalar()
        
        if not result:
            print("Adding supplier_id column to quotation_item table...")
            add_column_query = text("""
            ALTER TABLE quotation_item 
            ADD COLUMN supplier_id INTEGER REFERENCES supplier(id);
            """)
            db.session.execute(add_column_query)
            db.session.commit()
            print("Column added successfully!")
        else:
            print("supplier_id column already exists in quotation_item table.")


if __name__ == "__main__":
    add_supplier_id_column()