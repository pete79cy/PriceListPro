"""
Bulk Excel export utility for quotations.
This module provides functionality to export multiple quotations as individual Excel files.
"""

import os
import logging
import zipfile
import tempfile
from datetime import datetime
import uuid

from models import Quotation
from utils.excel_generator import generate_quotation_excel

logger = logging.getLogger(__name__)

def generate_bulk_quotation_excel(quotations, output_folder, columns=None, zip_filename=None):
    """
    Generate Excel files for multiple quotations and package them into a zip file.
    
    Args:
        quotations: List of Quotation objects to export
        output_folder: The folder where the zip file will be saved
        columns: Optional list of column configurations to include in each Excel file
        zip_filename: Optional custom filename for the zip file
        
    Returns:
        str: The path to the generated zip file
    """
    if not quotations:
        logger.warning("No quotations provided for bulk export")
        return None
    
    # Create a temporary directory to store the individual Excel files
    with tempfile.TemporaryDirectory() as temp_dir:
        excel_files = []
        
        # Generate Excel file for each quotation
        for quotation in quotations:
            try:
                excel_path = generate_quotation_excel(
                    quotation,
                    temp_dir,
                    columns=columns
                )
                
                if excel_path:
                    excel_files.append({
                        'path': excel_path,
                        'name': f"{quotation.quotation_number}_quotation.xlsx"
                    })
                    logger.info(f"Generated Excel for quotation #{quotation.quotation_number}")
                
            except Exception as e:
                logger.error(f"Error generating Excel for quotation #{quotation.quotation_number}: {str(e)}")
                # Continue with other quotations even if one fails
        
        if not excel_files:
            logger.error("Failed to generate any Excel files for the selected quotations")
            return None
        
        # Create a zip file containing all the Excel files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not zip_filename:
            zip_filename = f"quotations_export_{timestamp}_{uuid.uuid4().hex[:8]}.zip"
        
        zip_path = os.path.join(output_folder, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for excel_file in excel_files:
                zipf.write(
                    excel_file['path'],
                    arcname=excel_file['name']  # Use quotation number as filename inside zip
                )
        
        logger.info(f"Created zip file with {len(excel_files)} quotation Excel files: {zip_path}")
        return zip_path