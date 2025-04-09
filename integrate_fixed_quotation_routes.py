"""
Script to integrate fixed quotation routes into the main routes.py file.
This adds the routes necessary for generating fixed quotation PDFs.
"""

import os
import re
import sys
import logging
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("route_integrator")

# Path to files
ROUTES_FILE = 'routes.py'
FIXED_ROUTES_FILE = 'fixed_quotation_routes.py'

def integrate_routes():
    """
    Integrate the fixed quotation routes into the main routes.py file.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if files exist
        if not os.path.exists(ROUTES_FILE):
            logger.error(f"Main routes file not found: {ROUTES_FILE}")
            return False
            
        if not os.path.exists(FIXED_ROUTES_FILE):
            logger.error(f"Fixed routes file not found: {FIXED_ROUTES_FILE}")
            return False
        
        # Create backup of routes.py
        backup_file = f"{ROUTES_FILE}.bak"
        shutil.copy2(ROUTES_FILE, backup_file)
        logger.info(f"Created backup of routes.py: {backup_file}")
        
        # Read fixed routes content
        with open(FIXED_ROUTES_FILE, 'r', encoding='utf-8') as f:
            fixed_routes_content = f.read()
        
        # Extract the route functions from fixed routes file
        route_pattern = r'(@app\.route\([^\)]+\)\s+@login_required\s+def\s+[^:]+:.*?)(?=@app\.route|\Z)'
        routes = re.findall(route_pattern, fixed_routes_content, re.DOTALL | re.MULTILINE)
        
        if not routes:
            logger.error("No route functions found in fixed routes file")
            return False
            
        # Read main routes file
        with open(ROUTES_FILE, 'r', encoding='utf-8') as f:
            routes_content = f.read()
            
        # Find the end of route definitions
        register_routes_pos = routes_content.find("def register_routes(app):")
        if register_routes_pos == -1:
            logger.error("Could not find register_routes function in routes.py")
            return False
            
        # Insert fixed routes before the register_routes function
        routes_to_insert = "\n\n# Fixed Quotation PDF Routes\n" + "\n\n".join(routes)
        modified_content = (
            routes_content[:register_routes_pos] + 
            routes_to_insert + 
            "\n\n" + 
            routes_content[register_routes_pos:]
        )
        
        # Add import for fixed PDF generator if missing
        if "from utils.fixed_pdf_generator import generate_fixed_quotation_pdf" not in modified_content:
            import_pos = modified_content.find("import ")
            import_line = "from utils.fixed_pdf_generator import generate_fixed_quotation_pdf\n"
            modified_content = modified_content[:import_pos] + import_line + modified_content[import_pos:]
            
        # Write updated content to routes.py
        with open(ROUTES_FILE, 'w', encoding='utf-8') as f:
            f.write(modified_content)
            
        logger.info(f"Successfully integrated fixed quotation routes into {ROUTES_FILE}")
        
        # Modify view_quotation route to add buttons
        add_buttons_to_view()
            
        return True
            
    except Exception as e:
        logger.error(f"Error integrating routes: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False
        
def add_buttons_to_view():
    """
    Add buttons to export fixed PDFs to the quotation view template.
    """
    VIEW_TEMPLATE = 'templates/view_quotation.html'
    
    if not os.path.exists(VIEW_TEMPLATE):
        logger.warning(f"View template not found: {VIEW_TEMPLATE}")
        return
        
    try:
        # Create backup
        backup_file = f"{VIEW_TEMPLATE}.bak"
        shutil.copy2(VIEW_TEMPLATE, backup_file)
        
        # Read template
        with open(VIEW_TEMPLATE, 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        # Check if buttons already exist
        if 'export_quotation_fixed' in template_content:
            logger.info("Fixed PDF buttons already exist in template")
            return
            
        # Find export button to position our new buttons
        export_btn_pattern = r'<a\s+href="\{\{\s*url_for\([\'"]export_quotation[\'"],\s*quotation_id=quotation.id\)\s*\}\}"\s+class="btn[^>]+>\s*Export\s+PDF\s*</a>'
        match = re.search(export_btn_pattern, template_content)
        
        if not match:
            logger.warning("Could not find export button in template")
            return
            
        # Add our buttons after the existing export button
        button_html = """
                <a href="{{ url_for('export_quotation_fixed', quotation_id=quotation.id) }}" class="btn btn-success btn-sm">
                    <i class="fas fa-file-pdf"></i> Export Fixed PDF
                </a>
                {% if current_user.is_admin %}
                <a href="{{ url_for('export_quotation_fixed_debug', quotation_id=quotation.id) }}" class="btn btn-warning btn-sm">
                    <i class="fas fa-bug"></i> Debug PDF
                </a>
                {% endif %}
        """
        
        # Insert buttons
        pos = match.end()
        modified_content = template_content[:pos] + button_html + template_content[pos:]
        
        # Write updated template
        with open(VIEW_TEMPLATE, 'w', encoding='utf-8') as f:
            f.write(modified_content)
            
        logger.info(f"Added fixed PDF buttons to {VIEW_TEMPLATE}")
        
    except Exception as e:
        logger.error(f"Error adding buttons to template: {str(e)}")

if __name__ == "__main__":
    if integrate_routes():
        logger.info("✅ Integration completed successfully")
    else:
        logger.error("❌ Integration failed")
        sys.exit(1)
