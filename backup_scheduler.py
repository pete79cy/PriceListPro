#!/usr/bin/env python
"""
Backup Scheduler Tool

This tool helps set up scheduled database backups using cron on Linux systems.
It creates a cron job that runs the scheduled_backup.py script at specified intervals.

Usage:
    python backup_scheduler.py --help
    python backup_scheduler.py --daily 2:00 --keep 7
    python backup_scheduler.py --weekly Sunday 3:00 --keep 4
    python backup_scheduler.py --monthly 1 4:00 --keep 12
"""
import os
import sys
import argparse
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('backup_scheduler.log')
    ]
)
logger = logging.getLogger('backup_scheduler')

def get_current_crontab():
    """Get the current user's crontab content."""
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            # Some systems return non-zero if crontab is empty
            return ""
    except Exception as e:
        logger.error(f"Failed to get current crontab: {str(e)}")
        return ""

def save_crontab(content):
    """Save the provided content as the user's crontab."""
    try:
        # Write content to temporary file
        temp_file = '/tmp/new_crontab'
        with open(temp_file, 'w') as f:
            f.write(content)
        
        # Install the new crontab
        result = subprocess.run(['crontab', temp_file], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("Crontab updated successfully")
            return True
        else:
            logger.error(f"Failed to update crontab: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Failed to save crontab: {str(e)}")
        return False

def create_backup_cronjob(frequency, time_spec, keep_count, description=None):
    """
    Create a cron job for database backups.
    
    Args:
        frequency: 'daily', 'weekly', or 'monthly'
        time_spec: For daily: 'HH:MM', for weekly: 'DAY HH:MM', for monthly: 'DATE HH:MM'
        keep_count: Number of backups to keep
        description: Optional description for backups
        
    Returns:
        bool: True if the cron job was created successfully, False otherwise
    """
    # Get current directory for script paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backup_script = os.path.join(current_dir, 'scheduled_backup.py')
    
    # Parse time specs
    if frequency == 'daily':
        try:
            hour, minute = time_spec.split(':')
            cron_time = f"{minute} {hour} * * *"
            desc = description or f"Daily backup at {time_spec}"
        except ValueError:
            logger.error("Daily time spec must be in format 'HH:MM'")
            return False
            
    elif frequency == 'weekly':
        try:
            day, time = time_spec.split(' ', 1)
            hour, minute = time.split(':')
            # Convert day name to number (0-6, Sunday is 0)
            days = {'sunday': 0, 'monday': 1, 'tuesday': 2, 'wednesday': 3, 
                    'thursday': 4, 'friday': 5, 'saturday': 6}
            day_num = days.get(day.lower(), None)
            if day_num is None:
                logger.error(f"Invalid day name: {day}. Use full day name like 'Sunday'")
                return False
            cron_time = f"{minute} {hour} * * {day_num}"
            desc = description or f"Weekly backup on {day} at {time}"
        except ValueError:
            logger.error("Weekly time spec must be in format 'DAY HH:MM' (e.g., 'Sunday 3:00')")
            return False
            
    elif frequency == 'monthly':
        try:
            date, time = time_spec.split(' ', 1)
            hour, minute = time.split(':')
            if not (1 <= int(date) <= 28):
                logger.error("Monthly date must be between 1 and 28")
                return False
            cron_time = f"{minute} {hour} {date} * *"
            desc = description or f"Monthly backup on day {date} at {time}"
        except ValueError:
            logger.error("Monthly time spec must be in format 'DATE HH:MM' (e.g., '1 4:00')")
            return False
    else:
        logger.error(f"Invalid frequency: {frequency}")
        return False
    
    # Construct the backup command
    desc_arg = f"--description \"{desc}\"" if desc else ""
    keep_arg = f"--keep {keep_count}"
    backup_cmd = f"cd {current_dir} && python {backup_script} {keep_arg} {desc_arg}"
    
    # Create the full cron line
    cron_line = f"{cron_time} {backup_cmd} >> {current_dir}/scheduled_backup.log 2>&1"
    
    # Get current crontab and add the new line
    current_crontab = get_current_crontab()
    
    # Check if a similar backup job already exists
    if backup_script in current_crontab:
        logger.warning("A backup job already exists in crontab. Adding a new one.")
    
    # Add a comment before the job for identification
    new_crontab = current_crontab.strip() + f"\n\n# Database backup - {desc}\n{cron_line}\n"
    
    # Save the new crontab
    if save_crontab(new_crontab):
        logger.info(f"Scheduled {frequency} backup at {time_spec}")
        return True
    else:
        return False

def remove_backup_cronjobs():
    """Remove all database backup cron jobs."""
    current_crontab = get_current_crontab()
    new_crontab = []
    removed = 0
    
    # Go through each line in the current crontab
    for line in current_crontab.splitlines():
        if 'scheduled_backup.py' not in line and '# Database backup' not in line:
            new_crontab.append(line)
        else:
            removed += 1
    
    # Save the new crontab
    if removed > 0:
        if save_crontab('\n'.join(new_crontab)):
            logger.info(f"Removed {removed} backup jobs from crontab")
            return True
        else:
            return False
    else:
        logger.info("No backup jobs found in crontab")
        return True

def list_backup_cronjobs():
    """List all database backup cron jobs."""
    current_crontab = get_current_crontab()
    jobs = []
    
    # Find backup jobs in crontab
    capturing = False
    current_job = []
    
    for line in current_crontab.splitlines():
        if '# Database backup' in line:
            capturing = True
            current_job = [line]
        elif capturing and line.strip():
            current_job.append(line)
            if 'scheduled_backup.py' in line:
                jobs.append('\n'.join(current_job))
                capturing = False
        elif capturing and not line.strip():
            if current_job:
                jobs.append('\n'.join(current_job))
            capturing = False
    
    # Check if we were still capturing
    if capturing and current_job:
        jobs.append('\n'.join(current_job))
    
    return jobs

def main():
    """Command-line interface for the backup scheduler."""
    parser = argparse.ArgumentParser(description='Database Backup Scheduler')
    
    # Schedule type - only one can be selected
    schedule_group = parser.add_mutually_exclusive_group(required=True)
    schedule_group.add_argument('--daily', metavar='HH:MM',
                               help='Schedule daily backup at specified time (e.g., "2:00")')
    schedule_group.add_argument('--weekly', metavar='DAY HH:MM',
                               help='Schedule weekly backup on specified day and time (e.g., "Sunday 3:00")')
    schedule_group.add_argument('--monthly', metavar='DATE HH:MM',
                               help='Schedule monthly backup on specified date and time (e.g., "1 4:00")')
    schedule_group.add_argument('--list', action='store_true',
                               help='List current backup schedules')
    schedule_group.add_argument('--remove', action='store_true',
                               help='Remove all scheduled backups')
    
    # Optional arguments
    parser.add_argument('--keep', type=int, default=10,
                       help='Number of backups to keep (default: 10)')
    parser.add_argument('--description', 
                       help='Custom description for the backup')
    
    args = parser.parse_args()
    
    if args.list:
        jobs = list_backup_cronjobs()
        if jobs:
            print(f"Found {len(jobs)} scheduled backup job(s):")
            for i, job in enumerate(jobs, 1):
                print(f"\n--- Job {i} ---")
                print(job)
        else:
            print("No scheduled backup jobs found.")
        return 0
        
    if args.remove:
        if remove_backup_cronjobs():
            print("All scheduled backup jobs removed.")
            return 0
        else:
            print("Failed to remove backup jobs.")
            return 1
    
    # Handle schedule creation
    if args.daily:
        if create_backup_cronjob('daily', args.daily, args.keep, args.description):
            print(f"Daily backup scheduled at {args.daily}")
            return 0
    elif args.weekly:
        if create_backup_cronjob('weekly', args.weekly, args.keep, args.description):
            print(f"Weekly backup scheduled on {args.weekly}")
            return 0
    elif args.monthly:
        if create_backup_cronjob('monthly', args.monthly, args.keep, args.description):
            print(f"Monthly backup scheduled at {args.monthly}")
            return 0
    
    print("Failed to schedule backup.")
    return 1

if __name__ == "__main__":
    sys.exit(main())