#!/usr/bin/env python
"""
Database Backup & Restore Tool

This tool provides functionality for backing up and restoring PostgreSQL database 
data for the Plant Pricing System. It uses pg_dump for backups and psql for restores.

Features:
- Create full database backups (schema + data)
- Restore from backups
- List available backups
- Schedule automatic backups
"""
import os
import sys
import subprocess
import argparse
import logging
import datetime
import shutil
import glob
import json
from pathlib import Path
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('db_backup.log')
    ]
)
logger = logging.getLogger('db_backup_tool')

class DatabaseBackupTool:
    """Tool for backup and restore operations on the PostgreSQL database."""
    
    def __init__(self):
        """Initialize the backup tool with environment settings."""
        # Get database connection details from environment variables
        self.db_url = os.environ.get('DATABASE_URL')
        if not self.db_url:
            logger.error("DATABASE_URL environment variable not found")
            sys.exit(1)
            
        # Parse database URL components
        # Expected format: postgresql://username:password@host:port/database
        try:
            from urllib.parse import urlparse

            # Parse the URL
            parsed_url = urlparse(self.db_url)
            
            # Extract components
            self.username = parsed_url.username
            self.password = parsed_url.password
            self.host = parsed_url.hostname
            self.port = str(parsed_url.port) if parsed_url.port else '5432'
            
            # The path component contains the database name with a leading slash
            path = parsed_url.path
            if path.startswith('/'):
                path = path[1:]  # Remove leading slash
                
            # Handle query parameters if any
            if '?' in path:
                self.dbname = path.split('?')[0]
            else:
                self.dbname = path
        except Exception as e:
            logger.error(f"Failed to parse DATABASE_URL: {e}")
            sys.exit(1)
                
        # Set backup directory (create if it doesn't exist)
        self.backup_dir = os.path.join(os.getcwd(), 'database_backups')
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Metadata file to track backups
        self.metadata_file = os.path.join(self.backup_dir, 'backup_metadata.json')
        
        # Initialize metadata if it doesn't exist
        if not os.path.exists(self.metadata_file):
            self._init_metadata()
            
        logger.info(f"Backup tool initialized. Backup directory: {self.backup_dir}")
        
    def _init_metadata(self):
        """Initialize the backup metadata file."""
        metadata = {
            'backups': [],
            'last_backup': None,
            'backup_count': 0,
            'restore_history': []
        }
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info("Initialized backup metadata file")
        return metadata
        
    def _get_metadata(self):
        """Read the backup metadata."""
        try:
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
                # Ensure all required keys exist
                if 'backups' not in metadata:
                    metadata['backups'] = []
                if 'restore_history' not in metadata:
                    metadata['restore_history'] = []
                return metadata
        except Exception as e:
            logger.error(f"Failed to read metadata: {e}")
            return self._init_metadata()
            
    def _update_metadata(self, metadata):
        """Update the backup metadata file."""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
            
    def _get_env_for_pg_commands(self):
        """Create an environment dictionary with PGPASSWORD for pg_dump and psql."""
        env = os.environ.copy()
        env['PGPASSWORD'] = self.password
        return env
    
    def create_backup(self, description=None):
        """
        Create a full database backup.
        
        Args:
            description: Optional description of this backup
            
        Returns:
            str: Path to the created backup file, or None if backup failed
        """
        # Generate backup filename with timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"backup_{timestamp}.sql"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        # Create pg_dump command
        cmd = [
            'pg_dump',
            '-h', self.host,
            '-p', self.port,
            '-U', self.username,
            '--format=p',  # plain SQL format
            '--clean',     # include DROP commands before CREATE
            '--if-exists', # use IF EXISTS with DROP commands
            self.dbname
        ]
        
        logger.info(f"Creating backup: {backup_path}")
        
        try:
            # Run pg_dump and save output to file
            with open(backup_path, 'w') as f:
                result = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    env=self._get_env_for_pg_commands(),
                    check=True
                )
                
            # Get file size for metadata
            file_size = os.path.getsize(backup_path)
            
            # Update metadata
            metadata = self._get_metadata()
            backup_info = {
                'filename': backup_filename,
                'path': backup_path,
                'timestamp': timestamp,
                'datetime': datetime.datetime.now().isoformat(),
                'description': description or f"Automatic backup {timestamp}",
                'size': file_size,
                'size_formatted': self._format_size(file_size)
            }
            
            metadata['backups'].append(backup_info)
            metadata['last_backup'] = backup_info
            metadata['backup_count'] = len(metadata['backups'])
            self._update_metadata(metadata)
            
            logger.info(f"Backup completed successfully: {backup_filename} ({self._format_size(file_size)})")
            return backup_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Backup failed: {e.stderr.decode()}")
            # Remove failed backup file if it was created
            if os.path.exists(backup_path):
                os.remove(backup_path)
            return None
        except Exception as e:
            logger.error(f"Backup failed with unexpected error: {str(e)}")
            if os.path.exists(backup_path):
                os.remove(backup_path)
            return None
    
    def restore_backup(self, backup_path=None, backup_filename=None):
        """
        Restore database from a backup file.
        
        Args:
            backup_path: Full path to backup file
            backup_filename: Just the filename in the backup directory
            
        Returns:
            bool: True if restoration was successful, False otherwise
        """
        if backup_filename and not backup_path:
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
        if not backup_path or not os.path.exists(backup_path):
            logger.error(f"Backup file not found: {backup_path}")
            return False
            
        logger.info(f"Restoring from backup: {backup_path}")
        
        # First, create a pre-restore backup as a safety measure
        safety_backup_path = self.create_backup(description="Automatic pre-restore safety backup")
        if not safety_backup_path:
            logger.warning("Failed to create safety backup before restore. Proceeding anyway.")
            
        # Create psql command for restoration
        cmd = [
            'psql',
            '-h', self.host,
            '-p', self.port,
            '-U', self.username,
            '-d', self.dbname,
            '-f', backup_path
        ]
        
        try:
            # Run psql command to restore
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=self._get_env_for_pg_commands(),
                check=True
            )
            
            logger.info("Database restore completed successfully")
            
            # Update metadata with restoration event
            metadata = self._get_metadata()
            restore_info = {
                'event': 'restore',
                'backup_used': os.path.basename(backup_path),
                'timestamp': datetime.datetime.now().isoformat(),
                'success': True
            }
            
            if 'restore_history' not in metadata:
                metadata['restore_history'] = []
                
            metadata['restore_history'].append(restore_info)
            self._update_metadata(metadata)
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Restore failed: {e.stderr.decode()}")
            
            # Update metadata with failed restoration event
            metadata = self._get_metadata()
            restore_info = {
                'event': 'restore',
                'backup_used': os.path.basename(backup_path),
                'timestamp': datetime.datetime.now().isoformat(),
                'success': False,
                'error': e.stderr.decode()
            }
            
            if 'restore_history' not in metadata:
                metadata['restore_history'] = []
                
            metadata['restore_history'].append(restore_info)
            self._update_metadata(metadata)
            
            return False
        except Exception as e:
            logger.error(f"Restore failed with unexpected error: {str(e)}")
            return False
    
    def list_backups(self, count=None):
        """
        List available backups, newest first.
        
        Args:
            count: Number of backups to list, or None for all
            
        Returns:
            list: List of backup info dictionaries
        """
        metadata = self._get_metadata()
        backups = metadata.get('backups', [])
        
        # Sort by timestamp, newest first
        backups.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        if count:
            backups = backups[:count]
            
        return backups
        
    def _format_size(self, size_bytes):
        """Format file size from bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def clean_old_backups(self, keep=10):
        """
        Remove old backups, keeping only the specified number.
        
        Args:
            keep: Number of recent backups to keep
            
        Returns:
            int: Number of backups removed
        """
        metadata = self._get_metadata()
        backups = metadata.get('backups', [])
        
        if len(backups) <= keep:
            logger.info(f"Only {len(backups)} backups exist, none will be removed")
            return 0
            
        # Sort by timestamp, newest first
        backups.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Keep newest, delete the rest
        keep_backups = backups[:keep]
        delete_backups = backups[keep:]
        
        deleted_count = 0
        for backup in delete_backups:
            path = backup.get('path')
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    deleted_count += 1
                    logger.info(f"Deleted old backup: {os.path.basename(path)}")
                except Exception as e:
                    logger.error(f"Failed to delete backup {path}: {str(e)}")
        
        # Update metadata
        metadata['backups'] = keep_backups
        metadata['backup_count'] = len(keep_backups)
        self._update_metadata(metadata)
        
        logger.info(f"Cleaned up {deleted_count} old backups, keeping {len(keep_backups)} most recent")
        return deleted_count

    def get_backup_stats(self):
        """
        Get statistics about backups.
        
        Returns:
            dict: Backup statistics
        """
        metadata = self._get_metadata()
        backups = metadata.get('backups', [])
        
        # Calculate total size
        total_size = sum(b.get('size', 0) for b in backups)
        
        # Get oldest and newest backup dates
        if backups:
            dates = [datetime.datetime.fromisoformat(b.get('datetime', '')) 
                    for b in backups if 'datetime' in b]
            oldest = min(dates) if dates else None
            newest = max(dates) if dates else None
        else:
            oldest = None
            newest = None
            
        return {
            'count': len(backups),
            'total_size': total_size,
            'total_size_formatted': self._format_size(total_size),
            'oldest': oldest.isoformat() if oldest else None,
            'newest': newest.isoformat() if newest else None,
        }


def main():
    """Command-line interface for the backup tool."""
    parser = argparse.ArgumentParser(description='Database Backup and Restore Tool')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create a database backup')
    backup_parser.add_argument('--description', help='Description of this backup')
    
    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore database from backup')
    restore_parser.add_argument('--file', help='Backup filename to restore from')
    restore_parser.add_argument('--latest', action='store_true', help='Restore from the latest backup')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available backups')
    list_parser.add_argument('--count', type=int, help='Number of backups to list')
    
    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Remove old backups')
    clean_parser.add_argument('--keep', type=int, default=10, help='Number of recent backups to keep')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show backup statistics')
    
    args = parser.parse_args()
    
    # Create backup tool instance
    tool = DatabaseBackupTool()
    
    if args.command == 'backup':
        tool.create_backup(args.description)
        
    elif args.command == 'restore':
        if args.latest:
            backups = tool.list_backups(count=1)
            if backups:
                tool.restore_backup(backup_filename=backups[0].get('filename'))
            else:
                logger.error("No backups found to restore")
        elif args.file:
            tool.restore_backup(backup_filename=args.file)
        else:
            logger.error("Either --file or --latest must be specified for restore")
            
    elif args.command == 'list':
        backups = tool.list_backups(args.count)
        print(f"Found {len(backups)} backups:")
        for i, backup in enumerate(backups, 1):
            dt = backup.get('datetime', 'Unknown date')
            desc = backup.get('description', 'No description')
            size = backup.get('size_formatted', 'Unknown size')
            filename = backup.get('filename', 'Unknown filename')
            print(f"{i}. {filename} - {dt} - {size} - {desc}")
            
    elif args.command == 'clean':
        tool.clean_old_backups(keep=args.keep)
        
    elif args.command == 'stats':
        stats = tool.get_backup_stats()
        print(f"Backup Statistics:")
        print(f"Total backups: {stats['count']}")
        print(f"Total size: {stats['total_size_formatted']}")
        print(f"Oldest backup: {stats['oldest']}")
        print(f"Newest backup: {stats['newest']}")
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()