# Database Backup & Restore Guide

This document provides instructions for using the database backup and restore functionality in the Plant Pricing System.

## Overview

The database backup system provides the following features:
- Create manual or scheduled backups of the PostgreSQL database
- Restore the database from previous backups
- Manage backup files (download, delete)
- View backup statistics and history

## Accessing the Backup System

There are two ways to access the backup system:

1. **Web Interface**: Navigate to the Database Backup page in the admin section of the application.
   - Available at: `/backup` or `/database-backup`
   - Requires administrator privileges

2. **Command Line**: Use the `db_backup_tool.py` script directly.
   - Example: `python db_backup_tool.py create`

## Web Interface

The web interface provides a user-friendly way to manage database backups:

### Backup Dashboard

The main backup page shows:
- Backup statistics (total count, latest backup date, total size)
- List of available backups with details
- Forms for creating new backups and cleaning old ones

### Creating a Backup

To create a new backup:
1. Navigate to the Database Backup page
2. In the "Create New Backup" section, enter an optional description
3. Click "Create Backup"
4. The system will create a new backup file and add it to the list

### Restoring from a Backup

To restore the database from a backup:
1. Find the backup you want to restore in the list
2. Click the "Restore" button next to it
3. A confirmation dialog will appear
4. Type "CONFIRM" in the text field
5. Click "Restore Database"

**Warning**: Restoring a database will overwrite the current database with the backup version. All changes made since the backup was created will be lost.

### Managing Backups

- **Download**: Click the "Download" button next to a backup to download the SQL file
- **Clean Old Backups**: Use the "Clean Old Backups" form to remove older backups, keeping only the specified number of recent ones

## Command Line Tool

The `db_backup_tool.py` script provides command-line access to backup functionality:

```bash
# Create a backup
python db_backup_tool.py create --description "Monthly backup"

# List available backups
python db_backup_tool.py list

# Restore from a backup
python db_backup_tool.py restore --file backup_20250101_120000.sql

# Clean old backups (keep only 5 most recent)
python db_backup_tool.py clean --keep 5
```

## Scheduled Backups

The system supports scheduling automatic backups at regular intervals:

### Using the Scheduler Tool

The `backup_scheduler.py` tool helps set up cron jobs for scheduled backups:

```bash
# Schedule daily backups at 2:00 AM, keeping the 7 most recent
python backup_scheduler.py --daily 2:00 --keep 7

# Schedule weekly backups on Sunday at 3:00 AM, keeping the 4 most recent
python backup_scheduler.py --weekly Sunday 3:00 --keep 4

# Schedule monthly backups on the 1st day at 4:00 AM, keeping the 12 most recent
python backup_scheduler.py --monthly 1 4:00 --keep 12

# List scheduled backup jobs
python backup_scheduler.py --list

# Remove all scheduled backup jobs
python backup_scheduler.py --remove
```

## Backup File Format

Backup files are stored in the `database_backups` directory with the following naming convention:
```
backup_YYYYMMDD_HHMMSS.sql
```

For example: `backup_20250419_120000.sql`

Each backup file contains:
- A SQL dump of the entire database schema and data
- Metadata about the backup (in comments)

## Best Practices

1. **Regular Backups**: Set up scheduled backups to run automatically
2. **Multiple Backups**: Keep several recent backups in case you need to roll back to an earlier state
3. **Test Restores**: Periodically test the restore process to ensure backups are working correctly
4. **Offsite Storage**: Download important backups and store them in a separate location
5. **Before Major Changes**: Create a backup before making significant changes to the database

## Troubleshooting

If you encounter issues with the backup system:

1. **Backup Creation Fails**:
   - Check that PostgreSQL is running and accessible
   - Verify the DATABASE_URL environment variable is set correctly
   - Ensure the backup directory is writable

2. **Restore Fails**:
   - Check that the backup file exists and is not corrupted
   - Verify that the PostgreSQL user has sufficient privileges
   - Check for disk space issues

3. **Scheduled Backups Not Running**:
   - Verify that cron is running
   - Check the cron log for errors
   - Ensure the absolute paths in the cron job are correct

## Additional Information

For more detailed information, see:
- The source code in `db_backup_tool.py`
- The scheduled backup script in `scheduled_backup.py`
- The scheduler tool in `backup_scheduler.py`