"""
Integration script for the flexible quotation PDF generator.

This script:
1. Adds the flexible quotation routes to routes.py
2. Adds a button to the quotation view page
3. Verifies all templates are in place
"""

import os
import re
import sys
import shutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("integrator")

# File paths
ROUTES_FILE = 'routes.py'
FLEXIBLE_ROUTES_FILE = 'flexible_quotation_routes.py'
VIEW_TEMPLATE = 'templates/view_quotation.html'
FORM_TEMPLATE = 'templates/flexible_quotation_form.html'
PDF_TEMPLATE = 'templates/pdf/flexible_quotation_template.html'
GENERATOR_FILE = 'utils/flexible_pdf_generator.py'

def check_files():
    """
    Check if all required files exist
    
    Returns:
        bool: True if all files exist, False otherwise
    """
    files_to_check = [
        FLEXIBLE_ROUTES_FILE,
        FORM_TEMPLATE,
        PDF_TEMPLATE,
        GENERATOR_FILE
    ]
    
    missing_files = []
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
            
    if missing_files:
        logger.error(f"Missing files: {', '.join(missing_files)}")
        return False
        
    return True

def backup_file(file_path):
    """
    Create a backup of a file
    
    Args:
        file_path: Path to the file to backup
        
    Returns:
        str: Path to the backup file, or None if backup failed
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None
        
    backup_path = f"{file_path}.bak"
    try:
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Failed to create backup: {str(e)}")
        return None

def add_routes_to_main():
    """
    Add the flexible quotation routes to the main routes.py file
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(ROUTES_FILE):
        logger.error(f"Routes file not found: {ROUTES_FILE}")
        return False
        
    if not os.path.exists(FLEXIBLE_ROUTES_FILE):
        logger.error(f"Flexible routes file not found: {FLEXIBLE_ROUTES_FILE}")
        return False
        
    # Create backup of routes.py
    if not backup_file(ROUTES_FILE):
        return False
        
    # Read the flexible routes file
    with open(FLEXIBLE_ROUTES_FILE, 'r', encoding='utf-8') as f:
        flexible_routes_content = f.read()
        
    # Extract route functions (those with @app.route decorator)
    route_pattern = r'(@app\.route\([^\)]+\)\s+@login_required\s+def\s+[^:]+:.*?)(?=@app\.route|\Z)'
    routes = re.findall(route_pattern, flexible_routes_content, re.DOTALL | re.MULTILINE)
    
    if not routes:
        logger.error("No route functions found in flexible routes file")
        return False
        
    # Read the main routes file
    with open(ROUTES_FILE, 'r', encoding='utf-8') as f:
        routes_content = f.read()
        
    # Check if routes are already added
    first_route = routes[0].strip()
    if first_route in routes_content:
        logger.info("Flexible routes already added to routes.py")
        return True
        
    # Find the register_routes function
    register_pattern = r'def\s+register_routes\s*\(\s*app\s*\)\s*:'
    match = re.search(register_pattern, routes_content)
    
    if not match:
        logger.error("Could not find register_routes function in routes.py")
        return False
        
    # Insert flexible routes before register_routes
    insertion_point = match.start()
    
    # Prepare content to insert
    flexible_routes_section = "\n\n# ===== Flexible Quotation PDF Routes =====\n"
    flexible_routes_section += "\n\n".join(routes)
    flexible_routes_section += "\n\n"
    
    # Add import for flexible PDF generator
    import_section = "from utils.flexible_pdf_generator import generate_flexible_quotation_pdf, DEFAULT_ITEM_FIELDS, AVAILABLE_ITEM_FIELDS\n"
    
    # Check if import is already present
    if import_section not in routes_content:
        # Find imports section
        import_pattern = r'^import.*|^from.*'
        imports = re.findall(import_pattern, routes_content, re.MULTILINE)
        if imports:
            last_import = imports[-1]
            routes_content = routes_content.replace(last_import, last_import + "\n" + import_section)
        
    # Insert routes
    modified_content = (
        routes_content[:insertion_point] + 
        flexible_routes_section + 
        routes_content[insertion_point:]
    )
    
    # Write modified content back to routes.py
    with open(ROUTES_FILE, 'w', encoding='utf-8') as f:
        f.write(modified_content)
        
    logger.info("Added flexible quotation routes to routes.py")
    return True

def add_button_to_view_page():
    """
    Add a button to the quotation view page to access the flexible PDF export
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(VIEW_TEMPLATE):
        logger.error(f"View template not found: {VIEW_TEMPLATE}")
        return False
        
    # Create backup
    if not backup_file(VIEW_TEMPLATE):
        return False
        
    # Read the template
    with open(VIEW_TEMPLATE, 'r', encoding='utf-8') as f:
        template_content = f.read()
        
    # Check if button already exists
    if 'export_flexible_quotation' in template_content:
        logger.info("Flexible export button already exists in view template")
        return True
        
    # Look for existing export buttons
    btn_pattern = r'<a\s+href="\{\{\s*url_for\([\'"]export_quotation[\'"].*?\)\s*\}\}"\s+class="btn.*?>\s*.*?Export\s+PDF.*?</a>'
    match = re.search(btn_pattern, template_content)
    
    if not match:
        logger.warning("Could not find export button in view template")
        return False
        
    # New button to add
    new_button = """
                <a href="{{ url_for('export_flexible_quotation', quotation_id=quotation.id) }}" 
                   class="btn btn-info btn-sm ml-2" title="Create a customized PDF with selected fields">
                    <i class="fas fa-file-pdf"></i> Custom PDF
                </a>
    """
    
    # Add button after the existing export button
    modified_content = template_content[:match.end()] + new_button + template_content[match.end():]
    
    # Write back to template
    with open(VIEW_TEMPLATE, 'w', encoding='utf-8') as f:
        f.write(modified_content)
        
    logger.info("Added flexible export button to view template")
    return True

def main():
    """
    Run all integration steps
    
    Returns:
        bool: True if all steps succeed, False otherwise
    """
    success = True
    
    # Step 1: Check files
    logger.info("Step 1: Checking files...")
    if not check_files():
        logger.error("Some required files are missing")
        return False
    
    # Step 2: Add routes to main routes.py
    logger.info("Step 2: Adding routes to main routes.py...")
    if not add_routes_to_main():
        logger.error("Failed to add routes to routes.py")
        success = False
    
    # Step 3: Add button to view page
    logger.info("Step 3: Adding button to view template...")
    if not add_button_to_view_page():
        logger.warning("Failed to add button to view template")
        # Not critical, continue
    
    if success:
        logger.info("✅ Integration completed successfully")
        logger.info("Please restart the Flask application to apply the changes")
    else:
        logger.error("❌ Integration completed with errors")
        
    return success

if __name__ == "__main__":
    if not main():
        sys.exit(1)