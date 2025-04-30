#!/usr/bin/env python
"""
Direct Database Export Script for Quotations

This script directly exports quotations from the database to JSON format
without relying on the Flask app context, which can sometimes be slow to load.
"""
import os
import sys
import json
import logging
import argparse
import datetime
import psycopg2
import psycopg2.extras
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('quotation_export_direct.log')
    ]
)
logger = logging.getLogger('quotation_export_direct')

def get_db_connection():
    """Get a connection to the PostgreSQL database using DATABASE_URL."""
    try:
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            logger.error("DATABASE_URL environment variable not found")
            sys.exit(1)
        
        conn = psycopg2.connect(db_url)
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        sys.exit(1)

def export_all_quotations(output_dir=None):
    """
    Export all quotations directly from the database.
    
    Args:
        output_dir: Directory to save the export file
        
    Returns:
        str: Path to the export file
    """
    conn = get_db_connection()
    try:
        # Create a cursor with dictionary results
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get all quotations
        cursor.execute("""
            SELECT q.*, c.name as customer_name, c.email as customer_email, c.phone as customer_phone
            FROM quotation q
            JOIN customer c ON q.customer_id = c.id
            ORDER BY q.id
        """)
        quotations = cursor.fetchall()
        
        logger.info(f"Found {len(quotations)} quotations to export")
        
        # Initialize the export data structure
        export_data = {
            'metadata': {
                'export_date': datetime.datetime.now().isoformat(),
                'quotation_count': len(quotations),
                'version': '1.0',
                'description': 'Quotation data export for migration'
            },
            'quotations': []
        }
        
        # Process each quotation
        for quotation in quotations:
            # Get items for this quotation
            cursor.execute("""
                SELECT i.*, p.name as product_name, p.scientific_name as product_scientific_name,
                       s.name as supplier_name, s.email as supplier_email
                FROM quotation_item i
                LEFT JOIN product p ON i.product_id = p.id
                LEFT JOIN supplier s ON i.supplier_id = s.id
                WHERE i.quotation_id = %s
                ORDER BY i.position, i.id
            """, (quotation['id'],))
            items = cursor.fetchall()
            
            # Convert quotation to dict (already dict due to RealDictCursor)
            quotation_data = dict(quotation)
            
            # Convert datetime objects to strings
            for key, value in quotation_data.items():
                if isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
                    quotation_data[key] = value.isoformat()
            
            # Add customer data
            quotation_data['customer'] = {
                'id': quotation['customer_id'],
                'name': quotation['customer_name'],
                'email': quotation['customer_email'],
                'phone': quotation['customer_phone']
            }
            
            # Remove redundant fields
            for field in ['customer_name', 'customer_email', 'customer_phone']:
                if field in quotation_data:
                    del quotation_data[field]
            
            # Add items
            quotation_data['items'] = []
            for item in items:
                item_data = dict(item)
                
                # Convert datetime objects to strings
                for key, value in item_data.items():
                    if isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
                        item_data[key] = value.isoformat()
                
                # Add product data if available
                if item['product_id']:
                    item_data['product_data'] = {
                        'id': item['product_id'],
                        'name': item['product_name'],
                        'scientific_name': item['product_scientific_name']
                    }
                
                # Add supplier data if available
                if item['supplier_id']:
                    item_data['supplier_data'] = {
                        'id': item['supplier_id'],
                        'name': item['supplier_name'],
                        'email': item['supplier_email']
                    }
                
                # Remove redundant fields
                for field in ['product_name', 'product_scientific_name', 'supplier_name', 'supplier_email']:
                    if field in item_data:
                        del item_data[field]
                
                quotation_data['items'].append(item_data)
            
            export_data['quotations'].append(quotation_data)
        
        # Generate export filename with timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        export_filename = f"quotations_export_{timestamp}.json"
        
        # Ensure export directory exists
        if output_dir:
            export_dir = Path(output_dir)
        else:
            export_dir = Path(os.getcwd()) / 'exports'
        
        os.makedirs(export_dir, exist_ok=True)
        export_path = export_dir / export_filename
        
        # Write export data to JSON file
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully exported {len(quotations)} quotations to {export_path}")
        return str(export_path)
    
    except Exception as e:
        logger.error(f"Error exporting quotations: {e}")
        return None
    
    finally:
        conn.close()

def export_customer_quotations(customer_id, output_dir=None):
    """
    Export quotations for a specific customer.
    
    Args:
        customer_id: ID of the customer
        output_dir: Directory to save the export file
        
    Returns:
        str: Path to the export file
    """
    conn = get_db_connection()
    try:
        # Create a cursor with dictionary results
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Check if customer exists
        cursor.execute("SELECT * FROM customer WHERE id = %s", (customer_id,))
        customer = cursor.fetchone()
        
        if not customer:
            logger.error(f"Customer with ID {customer_id} not found")
            return None
        
        # Get quotations for this customer
        cursor.execute("""
            SELECT q.*
            FROM quotation q
            WHERE q.customer_id = %s
            ORDER BY q.id
        """, (customer_id,))
        quotations = cursor.fetchall()
        
        logger.info(f"Found {len(quotations)} quotations for customer {customer['name']}")
        
        # Initialize the export data structure
        export_data = {
            'metadata': {
                'export_date': datetime.datetime.now().isoformat(),
                'quotation_count': len(quotations),
                'version': '1.0',
                'description': f'Quotation export for customer {customer["name"]}'
            },
            'quotations': []
        }
        
        # Process each quotation
        for quotation in quotations:
            # Get items for this quotation
            cursor.execute("""
                SELECT i.*, p.name as product_name, p.scientific_name as product_scientific_name,
                       s.name as supplier_name, s.email as supplier_email
                FROM quotation_item i
                LEFT JOIN product p ON i.product_id = p.id
                LEFT JOIN supplier s ON i.supplier_id = s.id
                WHERE i.quotation_id = %s
                ORDER BY i.position, i.id
            """, (quotation['id'],))
            items = cursor.fetchall()
            
            # Convert quotation to dict (already dict due to RealDictCursor)
            quotation_data = dict(quotation)
            
            # Convert datetime objects to strings
            for key, value in quotation_data.items():
                if isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
                    quotation_data[key] = value.isoformat()
            
            # Add customer data
            quotation_data['customer'] = {
                'id': customer['id'],
                'name': customer['name'],
                'email': customer['email'],
                'phone': customer['phone']
            }
            
            # Add items
            quotation_data['items'] = []
            for item in items:
                item_data = dict(item)
                
                # Convert datetime objects to strings
                for key, value in item_data.items():
                    if isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
                        item_data[key] = value.isoformat()
                
                # Add product data if available
                if item['product_id']:
                    item_data['product_data'] = {
                        'id': item['product_id'],
                        'name': item['product_name'],
                        'scientific_name': item['product_scientific_name']
                    }
                
                # Add supplier data if available
                if item['supplier_id']:
                    item_data['supplier_data'] = {
                        'id': item['supplier_id'],
                        'name': item['supplier_name'],
                        'email': item['supplier_email']
                    }
                
                # Remove redundant fields
                for field in ['product_name', 'product_scientific_name', 'supplier_name', 'supplier_email']:
                    if field in item_data:
                        del item_data[field]
                
                quotation_data['items'].append(item_data)
            
            export_data['quotations'].append(quotation_data)
        
        # Generate export filename with customer name and timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_customer_name = customer['name'].replace(' ', '_').replace('/', '_')[:30]
        export_filename = f"quotations_{safe_customer_name}_{timestamp}.json"
        
        # Ensure export directory exists
        if output_dir:
            export_dir = Path(output_dir)
        else:
            export_dir = Path(os.getcwd()) / 'exports'
        
        os.makedirs(export_dir, exist_ok=True)
        export_path = export_dir / export_filename
        
        # Write export data to JSON file
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully exported {len(quotations)} quotations for customer {customer['name']} to {export_path}")
        return str(export_path)
    
    except Exception as e:
        logger.error(f"Error exporting customer quotations: {e}")
        return None
    
    finally:
        conn.close()

def list_quotations():
    """List quotations in the database to help with migration planning."""
    conn = get_db_connection()
    try:
        # Create a cursor with dictionary results
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get a count of quotations
        cursor.execute("SELECT COUNT(*) FROM quotation")
        count = cursor.fetchone()['count']
        
        print(f"Found {count} quotations in the database.")
        
        if count > 0:
            # Get sample quotations
            cursor.execute("""
                SELECT q.id, q.quotation_number, q.quotation_date, q.total_amount, q.currency,
                       c.name as customer_name,
                       (SELECT COUNT(*) FROM quotation_item WHERE quotation_id = q.id) as item_count
                FROM quotation q
                JOIN customer c ON q.customer_id = c.id
                ORDER BY q.id
                LIMIT 10
            """)
            quotations = cursor.fetchall()
            
            print("\nSample quotations:")
            print('-' * 80)
            print(f"{'ID':<5} {'Number':<15} {'Date':<12} {'Customer':<30} {'Items':<5} {'Total':<10}")
            print('-' * 80)
            
            for q in quotations:
                # Format the date
                date_str = q['quotation_date'].strftime('%Y-%m-%d') if q['quotation_date'] else 'N/A'
                
                # Format the total amount
                total = f"{q['currency']}{q['total_amount']:.2f}" if q['total_amount'] else 'N/A'
                
                print(f"{q['id']:<5} {q['quotation_number']:<15} {date_str:<12} {q['customer_name'][:30]:<30} {q['item_count']:<5} {total:<10}")
                
            if count > 10:
                print(f"\n... and {count - 10} more quotations.")
        
        return count > 0
    
    except Exception as e:
        logger.error(f"Error listing quotations: {e}")
        print(f"Error: {str(e)}")
        return False
    
    finally:
        conn.close()

def main():
    """Main function for command-line operation."""
    parser = argparse.ArgumentParser(description='Export quotations to JSON for migration')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--list', action='store_true', help='List quotations (no export)')
    group.add_argument('--all', action='store_true', help='Export all quotations')
    group.add_argument('--customer-id', type=int, help='Export quotations for a specific customer')
    
    parser.add_argument('--output-dir', help='Directory to save export files')
    
    args = parser.parse_args()
    
    try:
        if args.list:
            list_quotations()
            return 0
            
        elif args.all:
            export_path = export_all_quotations(args.output_dir)
            if export_path:
                print(f"Successfully exported all quotations to: {export_path}")
                return 0
            else:
                print("Failed to export quotations")
                return 1
        
        elif args.customer_id:
            export_path = export_customer_quotations(args.customer_id, args.output_dir)
            if export_path:
                print(f"Successfully exported customer quotations to: {export_path}")
                return 0
            else:
                print(f"Failed to export quotations for customer ID {args.customer_id}")
                return 1
        
        else:
            # Default: list quotations
            list_quotations()
            return 0
    
    except Exception as e:
        logger.error(f"Error during export: {str(e)}")
        print(f"Error: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())