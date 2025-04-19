"""
Database Backup Blueprint

This blueprint provides web routes for database backup and restore operations.
"""
from flask import Blueprint

backup_bp = Blueprint('backup', __name__, url_prefix='/backup',
                      template_folder='templates')

from . import routes