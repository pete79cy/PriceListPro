"""
Script to permanently fix the template to prevent missing items in quotation PDFs.
This adds improved CSS handling for table rows to ensure all rows appear properly.
"""

import os
import sys
import shutil
import logging
from app import app

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("template_fix")

def backup_template(template_path):
    """Create a backup of the template before modifying it"""
    backup_path = f"{template_path}.bak"
    if not os.path.exists(backup_path):
        shutil.copy2(template_path, backup_path)
        logger.info(f"Created backup of original template at: {backup_path}")
    else:
        logger.info(f"Backup already exists at: {backup_path}")
    return backup_path

def fix_template_css(template_path):
    """
    Apply CSS fixes to the template to ensure all rows appear in PDFs.
    
    Args:
        template_path: Path to the template file to fix
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the entire template
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create a backup first
        backup_template(template_path)
        
        # CSS fixes for common WeasyPrint issues with table rows
        css_fixes = [
            # 1. Fix table row breaking across pages
            ('tbody tr {', 'tbody tr {\n            page-break-inside: avoid !important;\n            break-inside: avoid !important;\n            display: table-row !important;\n            visibility: visible !important;'),
            
            # 2. Fix table overflow
            ('overflow: hidden;', 'overflow: visible; /* Changed from hidden to prevent clipping */'),
            
            # 3. Fix td styling for word wrapping
            ('word-break: break-word;', 'word-break: break-word;\n            overflow-wrap: break-word;\n            max-width: 20cm; /* Prevent overly wide cells */\n            overflow: visible;'),
            
            # 4. Fix table layout
            ('border-collapse: collapse;', 'border-collapse: collapse;\n            table-layout: fixed; /* More predictable layout */'),
        ]
        
        # Apply each fix
        for old, new in css_fixes:
            if old in content:
                content = content.replace(old, new)
                logger.info(f"Applied fix: {old} → {new}")
            else:
                logger.warning(f"Could not find text to replace: {old}")
        
        # Write the updated content
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Successfully updated template with CSS fixes: {template_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error fixing template: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def fix_quotation_templates():
    """Fix all quotation templates to ensure they render all rows properly"""
    with app.app_context():
        # Template paths
        templates_folder = os.path.join(app.root_path, 'templates', 'pdf')
        modern_template = os.path.join(templates_folder, 'modern_quotation_template.html')
        standard_template = os.path.join(templates_folder, 'quotation_template.html')
        
        # Fix both templates
        success1 = fix_template_css(modern_template)
        success2 = fix_template_css(standard_template)
        
        return success1 and success2

if __name__ == "__main__":
    print("\nApplying permanent CSS fixes to quotation templates to prevent missing rows...\n")
    
    success = fix_quotation_templates()
    
    if success:
        print("\n✅ Templates successfully updated!")
        print("The fix addresses the following issues:")
        print("1. Rows disappearing across page breaks")
        print("2. Table overflow handling that caused clipping")
        print("3. Word wrapping in cells to prevent overflow")
        print("4. Table layout stability to ensure consistent rendering")
    else:
        print("\n❌ Error updating templates. Check the log for details.")