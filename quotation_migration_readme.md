# Quotation Migration Guide

This guide explains how to export quotations from the current system and import them into a new system. The migration process uses a JSON-based export format that preserves all relationships between quotations, items, customers, products, and suppliers.

## Overview

The migration process consists of three main steps:

1. **Export** - Extract quotation data from the source system into JSON files
2. **Transfer** - Move the JSON files to the target system
3. **Import** - Load the quotation data into the target system

## Prerequisites

- Access to both source and target systems
- Python 3.8 or higher on both systems
- Required Python packages:
  - `psycopg2-binary`
  - `flask`
  - `flask-sqlalchemy`

## Step 1: Export Quotations

The export process is handled by the `export_quotations_direct.py` script, which connects directly to the database to extract quotations and related data.

### Export Options

The script provides several export options:

- Export all quotations
- Export quotations for a specific customer
- List quotations (without exporting)

### Usage

```bash
# List quotations without exporting
python export_quotations_direct.py --list

# Export all quotations
python export_quotations_direct.py --all

# Export quotations for a specific customer
python export_quotations_direct.py --customer-id <customer_id>

# Specify custom output directory
python export_quotations_direct.py --all --output-dir /path/to/output
```

### Export File Format

The exported data is saved as a JSON file with the following structure:

```json
{
  "metadata": {
    "export_date": "2025-04-30T20:02:46.861065",
    "quotation_count": 16,
    "version": "1.0",
    "description": "Quotation data export for migration"
  },
  "quotations": [
    {
      "id": 11,
      "customer_id": 9,
      "quotation_number": "PAK-2025-001",
      "quotation_date": "2025-04-05",
      "total_amount": 1510.20,
      "currency": "€",
      "notes": "",
      "status": "COMPLETED",
      "customer": {
        "id": 9,
        "name": "Customer Name",
        "email": "customer@example.com",
        "phone": "+1234567890"
      },
      "items": [
        {
          "id": 630,
          "quotation_id": 11,
          "description": "Item description",
          "quantity": 10,
          "unit_price": 15.50,
          "unit": "pcs",
          "position": 0,
          "product_data": {
            "id": 123,
            "name": "Product Name",
            "scientific_name": "Scientific Name"
          },
          "supplier_data": {
            "id": 45,
            "name": "Supplier Name",
            "email": "supplier@example.com"
          }
        }
        // More items...
      ]
    }
    // More quotations...
  ]
}
```

## Step 2: Transfer Files

Transfer the exported JSON files from the source system to the target system using one of these methods:

- Download the files via the web interface
- Use SCP or SFTP to transfer files directly between servers
- Use a cloud storage service (Google Drive, Dropbox, etc.)

## Step 3: Import Quotations

The import process is handled by the `import_quotations.py` script, which loads the JSON data into the target system.

### Import Options

The script provides options for handling existing quotations:

- Skip existing quotations (default)
- Update existing quotations (use `--force` flag)

### Usage

```bash
# Import quotations, skipping existing ones
python import_quotations.py path/to/export/file.json

# Import and update existing quotations
python import_quotations.py path/to/export/file.json --force
```

### Import Process

The import process follows these steps:

1. Parse the export file
2. For each quotation:
   - Find or create the customer
   - Find or create the quotation
   - For each item:
     - Find or create the product
     - Find or create the supplier
     - Create the quotation item
3. Commit all changes to the database

### Entity Resolution

During import, the script attempts to match existing entities using these strategies:

1. **Customers**:
   - First, try to match by ID
   - If not found, try to match by name
   - If still not found, create a new customer

2. **Products**:
   - First, try to match by ID
   - If not found, try to match by name
   - If still not found, create a new product

3. **Suppliers**:
   - First, try to match by ID
   - If not found, try to match by name
   - If still not found, create a new supplier

4. **Quotations**:
   - Try to match by quotation number
   - If found and `--force` is not used, skip the quotation
   - If found and `--force` is used, update the existing quotation
   - If not found, create a new quotation

## Troubleshooting

### Export Issues

- **Database Connection Errors**: Ensure the `DATABASE_URL` environment variable is correctly set
- **Permission Errors**: Ensure the user has the necessary permissions to read from the database
- **Missing Data**: Verify that the quotations exist in the source system

### Import Issues

- **Parsing Errors**: Verify that the JSON file is valid
- **Missing Dependencies**: Ensure all required packages are installed
- **Duplicate Entities**: Use the `--force` flag to update existing entities
- **Database Schema Mismatches**: Ensure the target system's schema is compatible with the import script

## Data Validation

After migration, validate the imported data:

1. Compare the count of quotations in both systems
2. Check that all customers, products, and suppliers were migrated
3. Verify a sample of quotations to ensure all data was properly migrated
4. Check that all relationships (quotation to items, items to products/suppliers) are preserved

## Advanced Topics

### Partial Migrations

To migrate only a subset of quotations, use one of these approaches:

1. Export quotations for specific customers:
   ```bash
   python export_quotations_direct.py --customer-id <customer_id>
   ```

2. Filter quotations on the target system after import:
   ```python
   # Example: Filter by date
   from datetime import datetime
   start_date = datetime(2024, 1, 1)
   filtered_quotations = Quotation.query.filter(Quotation.quotation_date >= start_date).all()
   ```

### Handling Large Datasets

For very large datasets, consider these approaches:

1. **Batch Processing**: Split exports into multiple files by customer or date range
2. **Incremental Migration**: Migrate newer quotations first, then older ones
3. **Parallel Processing**: Use multiple processes to handle different parts of the dataset