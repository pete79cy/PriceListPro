# Feature Flags and Rollback System

## Overview

This document describes the feature flag system implemented for the Plant Pricing System. Feature flags allow for controlled rollout of new features, enabling testing in production without affecting all users.

## Available Feature Flags

| Flag Name | Environment Variable | Description |
|-----------|---------------------|-------------|
| QUOTATION_IMPORT | FEATURE_QUOTE_IMPORT | Controls access to the quotation import functionality |

## Managing Feature Flags

Feature flags can be managed using the `set_feature_flag.py` script. This script provides a command-line interface for listing, enabling, and disabling feature flags.

### Listing Feature Flags

```bash
python set_feature_flag.py --list
```

This will display all available feature flags, their descriptions, and current values.

### Enabling a Feature Flag

```bash
python set_feature_flag.py --enable QUOTATION_IMPORT
```

This will enable the specified feature flag by setting the corresponding environment variable to 'true'.

### Disabling a Feature Flag

```bash
python set_feature_flag.py --disable QUOTATION_IMPORT
```

This will disable the specified feature flag by setting the corresponding environment variable to 'false'.

## Database Migrations

Some features require database schema changes. These are implemented as non-destructive SQL migrations that can be run safely on production databases.

### Applying Migrations

Migrations can be applied using the `apply_migration.py` script:

```bash
python apply_migration.py
```

This will apply the SQL migration for the import logs table, which is necessary for the quotation import feature.

Alternatively, you can run the SQL migration directly:

```bash
psql $DATABASE_URL -f migrations/20250505_add_import_logs.sql
```

## Import Rollback System

The rollback system provides a safety mechanism for undoing problematic imports. It tracks all import operations and allows administrators to roll back changes if issues are detected.

### Import Logs

All import operations are logged in the `import_logs` table. This table stores metadata about the import, including the user who performed it, the number of successful/failed records, and rollback data.

### Rolling Back Imports

To roll back an import, use the `rollback_import.py` script:

```bash
# List recent imports
python rollback_import.py --list

# Roll back a specific import by ID
python rollback_import.py --rollback [IMPORT_ID]
```

You can also roll back imports through the web interface by visiting the Import Logs page (`/quotations/import/logs`) and clicking the "Rollback" button next to a specific import.

## Web Interface

The feature-flagged functionality is available at:

- `/quotations/import` - Main import page
- `/quotations/import/logs` - Import logs and rollback interface

However, these routes are only accessible when the QUOTATION_IMPORT feature flag is enabled.

## Deployment Process

1. Apply database migrations: `python apply_migration.py`
2. Deploy code changes
3. Keep feature flag disabled initially: `python set_feature_flag.py --disable QUOTATION_IMPORT`
4. Test with feature flag enabled in development/staging
5. Enable feature for specific users or gradually roll out: `python set_feature_flag.py --enable QUOTATION_IMPORT`
6. Monitor logs and rollback if necessary
