"""
Script to properly add flexible quotation routes to routes.py.
This script will:
1. Fix the routes.py syntax error
2. Add the routes properly
"""

import os
import re
import sys
import shutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("fix_routes")

ROUTES_FILE = 'routes.py'

def backup_file(file_path):
    """Create a backup of a file"""
    backup_path = f"{file_path}.bak2"
    try:
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create backup: {str(e)}")
        return False

def find_route_insertions():
    """Find where to insert the new routes in routes.py"""
    with open(ROUTES_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all the existing routes
    route_pattern = r'@app\.route\([\'"].*?[\'"](.*?)def\s+([a-zA-Z0-9_]+)'
    routes = re.findall(route_pattern, content, re.DOTALL)
    routes_dict = {name: path for path, name in routes}
    
    # Find the register_routes function
    register_pattern = r'def\s+register_routes\s*\(\s*app\s*\)\s*:'
    match = re.search(register_pattern, content)
    
    if not match:
        logger.error("Could not find register_routes function")
        return None
    
    # Check if we already have the flexible routes
    if 'export_flexible_quotation' in routes_dict:
        logger.info("Flexible routes already exist, but may have syntax errors")
        # Find the existing flexible routes to remove them
        flex_route_pattern = r'(@app\.route\([\'"]\/quotation\/.*?\/export\/flexible.*?)(?=@app\.route|def\s+register_routes)'
        flex_routes = re.findall(flex_route_pattern, content, re.DOTALL)
        
        if flex_routes:
            # Remove the existing flexible routes
            for route in flex_routes:
                content = content.replace(route, '')
            
            # Write the modified content back
            with open(ROUTES_FILE, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info("Removed existing flexible routes with syntax errors")
    
    # Find where to insert the routes
    # Find the register_routes function
    register_pattern = r'def\s+register_routes\s*\(\s*app\s*\)\s*:'
    match = re.search(register_pattern, content)
    
    if not match:
        logger.error("Could not find register_routes function")
        return None
    
    return match.start()

def fix_routes():
    """Fix routes.py by adding flexible quotation routes properly"""
    # Backup the file
    if not backup_file(ROUTES_FILE):
        return False
    
    # Find insertion point
    insertion_point = find_route_insertions()
    if insertion_point is None:
        return False
    
    # Read the current content
    with open(ROUTES_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add import if it doesn't exist
    import_line = "from utils.flexible_pdf_generator import generate_flexible_quotation_pdf, DEFAULT_ITEM_FIELDS, AVAILABLE_ITEM_FIELDS"
    if import_line not in content:
        # Find imports section
        import_pattern = r'^import.*|^from.*'
        imports = re.findall(import_pattern, content, re.MULTILINE)
        if imports:
            last_import = imports[-1]
            content = content.replace(last_import, last_import + "\n" + import_line)
            logger.info("Added import for flexible PDF generator")
    
    # The flexible quotation routes to add
    flexible_routes = """
# ===== Flexible Quotation PDF Routes =====
def export_flexible_quotation(quotation_id):
    \"\"\"
    Export a quotation as PDF with flexible field selection.
    
    GET: Show field selection form
    POST: Generate PDF with selected fields
    \"\"\"
    try:
        # Get the quotation
        quotation = Quotation.query.get_or_404(quotation_id)
        
        if request.method == 'GET':
            # Render form to select fields
            return render_template(
                'flexible_quotation_form.html',
                quotation=quotation,
                default_fields=DEFAULT_ITEM_FIELDS,
                available_fields=AVAILABLE_ITEM_FIELDS,
                is_admin=getattr(current_user, 'is_admin', False)
            )
        else:
            # Process field selection
            selected_fields = request.form.getlist('fields')
            orientation = request.form.get('orientation', 'portrait')
            include_admin = request.form.get('include_admin') == 'yes' and getattr(current_user, 'is_admin', False)
            use_modern = request.form.get('style', 'modern') == 'modern'
            
            # Create directory for PDF output
            output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'flexible_quotations')
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate PDF using our flexible generator
            output_path = generate_flexible_quotation_pdf(
                quotation=quotation,
                selected_fields=selected_fields,
                upload_folder=output_dir,
                orientation=orientation,
                include_admin_fields=include_admin,
                use_modern_style=use_modern,
                debug=False
            )
            
            if not output_path:
                flash("Error generating PDF - please contact support", "danger")
                return redirect(url_for('view_quotation', quotation_id=quotation_id))
            
            # Return the PDF file
            filename = os.path.basename(output_path)
            return send_from_directory(directory=output_dir, path=filename, as_attachment=True)
            
    except Exception as e:
        logger.error(f"Error exporting flexible quotation PDF: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        flash(f"Error generating PDF: {str(e)}", "danger")
        return redirect(url_for('view_quotation', quotation_id=quotation_id))

def export_flexible_quotation_api(quotation_id):
    \"\"\"
    API endpoint to generate a flexible quotation PDF with JSON field configuration.
    
    POST: JSON payload with field configuration
    Returns: JSON with PDF URL or error
    \"\"\"
    try:
        # Get the quotation
        quotation = Quotation.query.get_or_404(quotation_id)
        
        # Get JSON payload
        payload = request.get_json()
        if not payload:
            return jsonify({'error': 'No JSON payload provided'}), 400
            
        # Extract configuration
        selected_fields = payload.get('fields', None)
        orientation = payload.get('orientation', 'portrait')
        include_admin = payload.get('include_admin', False) and getattr(current_user, 'is_admin', False)
        use_modern = payload.get('style', 'modern') == 'modern'
        
        # Create directory for PDF output
        output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'flexible_quotations')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate PDF using our flexible generator
        output_path = generate_flexible_quotation_pdf(
            quotation=quotation,
            selected_fields=selected_fields,
            upload_folder=output_dir,
            orientation=orientation,
            include_admin_fields=include_admin,
            use_modern_style=use_modern,
            debug=False
        )
        
        if not output_path:
            return jsonify({'error': 'Failed to generate PDF'}), 500
        
        # Return the PDF URL
        filename = os.path.basename(output_path)
        pdf_url = url_for('download_flexible_quotation', filename=filename, _external=True)
        
        return jsonify({
            'success': True,
            'pdf_url': pdf_url,
            'filename': filename
        })
            
    except Exception as e:
        logger.error(f"Error in flexible quotation API: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

def download_flexible_quotation(filename):
    \"\"\"Download a generated flexible quotation PDF by filename\"\"\"
    output_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'flexible_quotations')
    return send_from_directory(directory=output_dir, path=filename, as_attachment=True)

def get_quotation_fields():
    \"\"\"API endpoint to get available quotation fields\"\"\"
    fields = {
        'default': DEFAULT_ITEM_FIELDS,
        'available': [f for f in AVAILABLE_ITEM_FIELDS if not f.get('admin_only') or getattr(current_user, 'is_admin', False)]
    }
    return jsonify(fields)

"""
    
    # Create route registration function calls
    route_registrations = """
    # Register flexible quotation routes
    app.route('/quotation/<int:quotation_id>/export/flexible', methods=['GET', 'POST'])(login_required(export_flexible_quotation))
    app.route('/quotation/<int:quotation_id>/export/flexible-api', methods=['POST'])(login_required(export_flexible_quotation_api))
    app.route('/download/flexible-quotation/<filename>')(login_required(download_flexible_quotation))
    app.route('/api/quotation-fields')(login_required(get_quotation_fields))
    
"""
    
    # Insert routes before register_routes
    updated_content = (
        content[:insertion_point] + 
        flexible_routes + 
        content[insertion_point:]
    )
    
    # Add route registrations to register_routes function
    register_function_pattern = r'def\s+register_routes\s*\(\s*app\s*\)\s*:\s*\n(.*?)(return\s+app|$)'
    match = re.search(register_function_pattern, updated_content, re.DOTALL)
    
    if match:
        function_body = match.group(1)
        end_marker = match.group(2)
        
        # Check if the registrations already exist
        if "# Register flexible quotation routes" not in function_body:
            # Insert registrations before the end marker
            updated_function = (
                'def register_routes(app):\n' + 
                function_body +
                route_registrations +
                end_marker
            )
            
            updated_content = updated_content.replace(
                'def register_routes(app):\n' + function_body + end_marker,
                updated_function
            )
            
            logger.info("Added route registrations to register_routes function")
    
    # Write the updated content
    with open(ROUTES_FILE, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    logger.info("Successfully added flexible quotation routes to routes.py")
    return True

if __name__ == "__main__":
    if fix_routes():
        logger.info("✅ Routes.py fixed successfully")
    else:
        logger.error("❌ Failed to fix routes.py")
        sys.exit(1)