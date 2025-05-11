"""
Script to integrate enhanced quotation routes into the main routes.py file.
This adds the routes necessary for generating enhanced quotation PDFs with pagination.
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
ENHANCED_ROUTES_FILE = 'enhanced_quotation_routes.py'

def integrate_routes():
    """
    Integrate the enhanced quotation routes into the main routes.py file.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if files exist
        if not os.path.exists(ROUTES_FILE):
            logger.error(f"Main routes file not found: {ROUTES_FILE}")
            return False
            
        if not os.path.exists(ENHANCED_ROUTES_FILE):
            logger.error(f"Enhanced routes file not found: {ENHANCED_ROUTES_FILE}")
            return False
        
        # Create backup of routes.py
        backup_file = f"{ROUTES_FILE}.bak"
        shutil.copy2(ROUTES_FILE, backup_file)
        logger.info(f"Created backup of routes.py: {backup_file}")
        
        # Read enhanced routes content
        with open(ENHANCED_ROUTES_FILE, 'r', encoding='utf-8') as f:
            enhanced_routes_content = f.read()
        
        # Extract the route functions from enhanced routes file
        route_pattern = r'(@app\.route\([^\)]+\)\s+@login_required\s+def\s+[^:]+:.*?)(?=@app\.route|\Z)'
        routes = re.findall(route_pattern, enhanced_routes_content, re.DOTALL | re.MULTILINE)
        
        if not routes:
            logger.error("No route functions found in enhanced routes file")
            return False
            
        # Read main routes file
        with open(ROUTES_FILE, 'r', encoding='utf-8') as f:
            routes_content = f.read()
            
        # Find the end of route definitions
        register_routes_pos = routes_content.find("def register_routes(app):")
        if register_routes_pos == -1:
            logger.error("Could not find register_routes function in routes.py")
            return False
            
        # Insert enhanced routes before the register_routes function
        routes_to_insert = "\n\n# Enhanced Quotation PDF Routes with Pagination\n" + "\n\n".join(routes)
        modified_content = (
            routes_content[:register_routes_pos] + 
            routes_to_insert + 
            "\n\n" + 
            routes_content[register_routes_pos:]
        )
        
        # Add import for enhanced PDF generator if missing
        if "from utils.enhanced_weasprint_pdf_generator import generate_enhanced_quotation_pdf" not in modified_content:
            import_pos = modified_content.find("import ")
            import_line = "from utils.enhanced_weasprint_pdf_generator import generate_enhanced_quotation_pdf\n"
            modified_content = modified_content[:import_pos] + import_line + modified_content[import_pos:]
            
        # Write updated content to routes.py
        with open(ROUTES_FILE, 'w', encoding='utf-8') as f:
            f.write(modified_content)
            
        logger.info(f"Successfully integrated enhanced quotation routes into {ROUTES_FILE}")
        
        # Modify view_quotation route to add buttons
        add_buttons_to_view_template()
            
        return True
            
    except Exception as e:
        logger.error(f"Error integrating routes: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def add_buttons_to_view_template():
    """
    Add buttons for enhanced PDF generation to the quotation view template.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        template_file = 'templates/view_quotation.html'
        if not os.path.exists(template_file):
            logger.warning(f"View quotation template not found: {template_file}")
            return False
            
        # Create backup of the template
        backup_file = f"{template_file}.bak"
        shutil.copy2(template_file, backup_file)
        
        # Read template content
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        # Find where to add the new buttons
        button_pattern = r'<a href="\{\{ url_for\(\'export_quotation\', quotation_id=quotation.id\) \}\}"[^>]*>.*?</a>'
        match = re.search(button_pattern, template_content)
        
        if not match:
            logger.warning("Could not find export button in view_quotation.html")
            return False
            
        button_pos = match.end()
        
        # Add enhanced PDF export buttons
        new_buttons = """
                <a href="{{ url_for('export_quotation_enhanced', quotation_id=quotation.id) }}" 
                   class="btn btn-sm btn-outline-success" title="Export as enhanced PDF with pagination">
                   <i class="fa fa-file-pdf-o"></i> Enhanced PDF
                </a>
                {% if current_user.is_admin %}
                <a href="{{ url_for('export_quotation_enhanced_debug', quotation_id=quotation.id) }}" 
                   class="btn btn-sm btn-outline-info" title="Export debug PDF with visual indicators">
                   <i class="fa fa-bug"></i> Debug PDF
                </a>
                {% endif %}
        """
        
        modified_content = template_content[:button_pos] + new_buttons + template_content[button_pos:]
        
        # Write updated content to template
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
            
        logger.info(f"Successfully added enhanced PDF buttons to {template_file}")
        return True
            
    except Exception as e:
        logger.error(f"Error adding buttons to template: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Main function to integrate the enhanced routes"""
    logger.info("Starting integration of enhanced quotation routes")
    
    if integrate_routes():
        logger.info("✅ Enhanced quotation routes integration successful")
        print("\n✅ Enhanced quotation routes have been integrated into routes.py")
        print("✅ PDF export buttons have been added to the view_quotation.html template")
        return 0
    else:
        logger.error("❌ Enhanced quotation routes integration failed")
        print("\n❌ Failed to integrate enhanced quotation routes")
        return 1

if __name__ == '__main__':
    sys.exit(main())