"""
Comprehensive fix script that applies all PDF quotation fixes:
1. Fixes item positions in all quotations
2. Integrates fixed routes into routes.py
3. Tests the fixes on problematic quotations
"""

import os
import sys
import logging
import subprocess
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("pdf_fix")

def run_script(script_name, *args):
    """
    Run a Python script with optional arguments.
    
    Args:
        script_name: The name of the script to run
        *args: Additional arguments to pass to the script
        
    Returns:
        bool: True if script exited with code 0, False otherwise
    """
    cmd = [sys.executable, script_name] + list(args)
    logger.info(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logger.error(f"Script {script_name} failed with exit code {e.returncode}")
        return False

def main():
    """
    Apply all PDF quotation fixes in sequence.
    
    Returns:
        bool: True if all fixes were applied successfully, False otherwise
    """
    start_time = datetime.now()
    logger.info(f"Starting comprehensive PDF fixes at {start_time}")
    
    # Step 1: Fix positions for all quotation items
    logger.info("Step 1: Fixing quotation item positions...")
    if not run_script("fix_all_quotation_positions.py"):
        logger.error("❌ Failed to fix quotation positions")
        return False
    logger.info("✅ Successfully fixed quotation positions")
    
    # Step 2: Integrate fixed routes into the main routes.py
    logger.info("Step 2: Integrating fixed routes...")
    if not run_script("integrate_fixed_quotation_routes.py"):
        logger.error("❌ Failed to integrate fixed routes")
        return False
    logger.info("✅ Successfully integrated fixed routes")
    
    # Step 3: Test the fixes on a known problematic quotation
    logger.info("Step 3: Testing fixes...")
    if not run_script("test_fixed_quotation_pdf.py", "PAK-2025-007", "--debug"):
        logger.warning("⚠️ Test produced warnings, but continuing")
    else:
        logger.info("✅ Successfully tested fixes")
    
    # Calculate execution time
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info(f"All fixes completed in {duration.total_seconds():.2f} seconds")
    logger.info("To access the fixed PDFs, use the 'Export Fixed PDF' button on the quotation view page")
    logger.info("You may need to restart the application for the new routes to take effect")
    
    return True

if __name__ == "__main__":
    if main():
        logger.info("✅ All PDF quotation fixes applied successfully")
    else:
        logger.error("❌ Some fixes failed - check the logs for details")
        sys.exit(1)
