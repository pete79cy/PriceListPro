# Quotation Migration Tools

This set of tools allows you to export quotations from the current system and import them into a new version of the application.

## 1. Export Quotations

The `export_quotations.py` script exports quotations and their related data from the database to JSON files.

### Usage:

```bash
# Export all quotations
python export_quotations.py

# Export all quotations to a specific directory
python export_quotations.py --output-dir /path/to/export/directory

# Export quotations for a specific customer
python export_quotations.py --customer-id 123

# Export a specific quotation
python export_quotations.py --quotation-id 456
```

The script creates a JSON file in the specified output directory (defaults to an 'exports' folder in the current directory). The exported file includes:

- Quotation data (number, date, amounts, etc.)
- Customer information
- All quotation items with their details
- Product and supplier references

## 2. Import Quotations

The `import_quotations.py` script imports quotations from JSON files created by the export tool.

### Usage:

```bash
# Test import without making changes (dry run)
python import_quotations.py --file exports/quotations_export_20250430_123456.json --dry-run

# Import quotations for real
python import_quotations.py --file exports/quotations_export_20250430_123456.json

# Import and save a detailed report
python import_quotations.py --file exports/quotations_export_20250430_123456.json --report import_report.txt
```

The import process:

1. Loads quotations from the JSON file
2. Checks if each quotation already exists in the target system (by quotation number)
3. Finds or maps customers, products, and suppliers in the target system
4. Creates new quotations and items
5. Provides a detailed report of what was imported

### Dry Run Mode

Use the `--dry-run` flag to test the import without actually saving changes to the database. This is useful for verifying that the import will work correctly before making any changes.

## 3. Important Notes

1. **Customer Matching**: The import tool tries to match customers by name and ID. If a customer isn't found, the quotation will be skipped.

2. **Product and Supplier Matching**: The tool attempts to match products and suppliers by ID first, then by name. If they're not found, the quotation item will still be imported without those references.

3. **Database Backup**: Always create a backup of your database before performing an import:
   ```bash
   python db_backup_tool.py backup --description "Pre-quotation import backup"
   ```

4. **Logs**: Both tools maintain detailed logs in `quotation_export.log` and `quotation_import.log` files.

5. **Error Handling**: If errors occur during import, they are logged, and the process continues with the next quotation.

## 4. Example Migration Workflow

Here's a recommended workflow for migrating quotations:

1. Create a database backup:
   ```bash
   python db_backup_tool.py backup --description "Pre-migration backup"
   ```

2. Export all quotations from the source system:
   ```bash
   python export_quotations.py --output-dir migration_data
   ```

3. Set up the new system and ensure all customers, products, and suppliers are migrated first.

4. Test import on the new system:
   ```bash
   python import_quotations.py --file migration_data/quotations_export_*.json --dry-run
   ```

5. Review the output and fix any issues.

6. Perform the actual import:
   ```bash
   python import_quotations.py --file migration_data/quotations_export_*.json --report migration_report.txt
   ```

7. Verify the imported quotations in the new system.

## 5. Troubleshooting

- **Missing Dependencies**: Ensure both systems have the same package dependencies installed.
- **Model Differences**: If the data models differ significantly between the old and new systems, you may need to modify the import script.
- **ID Conflicts**: The import creates new IDs for all imported data to avoid conflicts.
- **Large Datasets**: For very large datasets, consider importing in smaller batches by customer or date range.