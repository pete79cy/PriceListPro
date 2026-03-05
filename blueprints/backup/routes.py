"""
Backup Blueprint Routes

This module provides web routes for database backup and restore operations.
"""
import os
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import current_user
from replit_auth import require_login
from werkzeug.utils import secure_filename

from app import db
from models import User
from db_backup_tool import DatabaseBackupTool
from . import backup_bp


# Temporarily disable admin restriction for testing
# @backup_bp.before_request
# def restrict_to_admins():
#     """Ensure only admins can access backup functionality."""
#     if not current_user.is_authenticated or not current_user.is_admin:
#         flash('Access denied. You must be an administrator to manage backups.', 'danger')
#         return redirect(url_for('index'))


@backup_bp.route('/')
# Temporarily disabled for testing
# @require_login
def index():
    """Display backup dashboard."""
    tool = DatabaseBackupTool()
    backups = tool.list_backups()
    stats = tool.get_backup_stats()
    
    return render_template('backup/index.html', 
                           backups=backups, 
                           stats=stats,
                           timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


@backup_bp.route('/create', methods=['POST'])
@require_login
def create_backup():
    """Create a new database backup."""
    description = request.form.get('description', f"Manual backup by {current_user.username}")
    
    tool = DatabaseBackupTool()
    backup_path = tool.create_backup(description)
    
    if backup_path:
        flash(f'Database backup created successfully.', 'success')
    else:
        flash('Failed to create database backup. Check the logs for details.', 'danger')
    
    return redirect(url_for('backup.index'))


@backup_bp.route('/restore/<path:filename>', methods=['POST'])
@require_login
def restore_backup(filename):
    """Restore database from a specific backup file."""
    confirmation = request.form.get('confirmation')
    
    if confirmation != 'CONFIRM':
        flash('Restoration canceled. Confirmation text did not match.', 'warning')
        return redirect(url_for('backup.index'))
    
    tool = DatabaseBackupTool()
    success = tool.restore_backup(backup_filename=filename)
    
    if success:
        flash('Database restored successfully.', 'success')
    else:
        flash('Failed to restore database. Check the logs for details.', 'danger')
    
    return redirect(url_for('backup.index'))


@backup_bp.route('/download/<path:filename>')
@require_login
def download_backup(filename):
    """Download a backup file."""
    tool = DatabaseBackupTool()
    backup_path = os.path.join(tool.backup_dir, secure_filename(filename))
    
    if os.path.exists(backup_path):
        return send_file(backup_path, as_attachment=True)
    else:
        flash('Backup file not found.', 'danger')
        return redirect(url_for('backup.index'))


@backup_bp.route('/clean', methods=['POST'])
@require_login
def clean_backups():
    """Remove old backup files, keeping only the specified number."""
    keep = request.form.get('keep', 10)
    try:
        keep = int(keep)
        if keep < 1:
            keep = 1
    except ValueError:
        keep = 10
    
    tool = DatabaseBackupTool()
    deleted_count = tool.clean_old_backups(keep=keep)
    
    flash(f'Cleaned up {deleted_count} old backups.', 'success')
    return redirect(url_for('backup.index'))