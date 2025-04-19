# Database Backup and Restore Guide

This guide explains how to use the database backup and restore tools that are part of the Plant Pricing System.

## Overview

The backup system provides:
- Web interface for manual backups and restores
- Command-line tools for advanced usage
- Scheduled backup capabilities

## Web Interface

The backup web interface is accessible to administrators at `/backup` in the application.

### Features
- Create manual backups with descriptions
- View all available backups 
- Download backup files
- Restore from any available backup
- Clean up old backups to save space

### Usage
1. Navigate to `/backup` in your application
2. Use the "Create New Backup" form to create a new backup
3. View existing backups in the table below
4. Use the "Download" button to save backups locally
5. Use the "Restore" button and confirm to restore from a backup
6. Use "Clean Old Backups" to keep only a specific number of recent backups

## Command-Line Tools

The system includes several command-line tools for backing up and restoring the database.

### db_backup_tool.py

This is the core tool that handles backup and restore operations.

```
Usage:
python db_backup_tool.py backup [--description "Optional description"]
python db_backup_tool.py restore --file backup_20250419_123045.sql
python db_backup_tool.py restore --latest
python db_backup_tool.py list [--count 5]
python db_backup_tool.py clean [--keep 10]
python db_backup_tool.py stats
```

### scheduled_backup.py

Run this script to create a one-time backup, typically scheduled via cron.

```
Usage:
python scheduled_backup.py [--keep 10] [--description "Scheduled backup"]
```

### backup_scheduler.py

Use this tool to configure automated backups on Linux systems with cron.

```
Usage:
# Schedule daily backup at 2:00 AM, keeping the last 7 backups
python backup_scheduler.py --daily 2:00 --keep 7

# Schedule weekly backup on Sunday at 3:00 AM
python backup_scheduler.py --weekly "Sunday 3:00" --keep 4

# Schedule monthly backup on the 1st at 4:00 AM
python backup_scheduler.py --monthly "1 4:00" --keep 12

# List currently scheduled backups
python backup_scheduler.py --list

# Remove all scheduled backups
python backup_scheduler.py --remove
```

## Backup Storage

All backups are stored in the `database_backups` directory as plain SQL files. These files contain:
- Database schema (tables, indexes, constraints)
- All data in SQL format
- DROP statements to clean the database before restoration

## Best Practices

1. **Regular Backups**: Schedule regular backups (daily or weekly) depending on how frequently your data changes
2. **Multiple Retention Periods**: Keep daily backups for a week, weekly backups for a month, and monthly backups for a year
3. **Test Restorations**: Periodically test the restore process to ensure backups are valid
4. **Off-site Storage**: Download important backups and store them in a different location
5. **Pre-update Backups**: Always create a backup before updating the application or making major changes

## Troubleshooting

### Backup Fails
- Check the logs in `db_backup.log`
- Ensure the DATABASE_URL environment variable is correctly set
- Verify the PostgreSQL server is running and accessible
- Check if there's enough disk space

### Restore Fails
- Check the logs in `db_backup.log`
- Verify the backup file exists and is not corrupted
- Ensure the DATABASE_URL points to a valid database 
- Check if the user has sufficient permissions in PostgreSQL

### Scheduled Backups Not Running
- Check `scheduled_backup.log` for errors
- Verify cron is running (`systemctl status cron`)
- Check crontab is properly configured (`crontab -l`)
- Ensure the script has execution permissions

## Backup File Format

Backup files follow this naming pattern:
```
backup_YYYYMMDD_HHMMSS.sql
```

For example: `backup_20250419_123045.sql` was created on April 19, 2025 at 12:30:45.

## Security Considerations

- Backup files contain all your data, so keep them secure
- The web interface restricts access to administrators only
- Consider encrypting sensitive backups before storing them long-term
- Database credentials are never stored in backup files