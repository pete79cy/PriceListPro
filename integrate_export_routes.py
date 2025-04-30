#!/usr/bin/env python
"""
Script to integrate export routes with the main application
"""
import sys
import os

def update_app_file():
    """Update the main app.py file to register export routes"""
    app_file = 'app.py'
    
    if not os.path.exists(app_file):
        print(f"Error: {app_file} not found")
        return False
    
    with open(app_file, 'r') as f:
        content = f.read()
    
    # Check if import is already there
    if 'from routes_export import register_export_routes' not in content:
        # Find a good spot to add the import
        import_line = 'from routes_export import register_export_routes'
        
        # Add import after other route imports
        if 'import routes' in content:
            content = content.replace('import routes', 'import routes\n' + import_line)
        else:
            # Add import at the top with other imports
            import_section_end = content.find('\n\n', content.find('import'))
            if import_section_end > 0:
                content = content[:import_section_end] + '\n' + import_line + content[import_section_end:]
            else:
                # Just add to the top as a fallback
                content = import_line + '\n' + content
    
    # Check if registration is already there
    if 'register_export_routes(app)' not in content:
        # Find a good spot to add the registration
        registration_line = '    # Register quotation export routes\n    register_export_routes(app)'
        
        # Add registration near end of app setup
        if '# Initialize the app' in content:
            parts = content.split('# Initialize the app')
            if len(parts) > 1:
                # Find the end of the initialization section
                init_section_end = parts[1].find('\n\n')
                if init_section_end > 0:
                    parts[1] = parts[1][:init_section_end] + '\n\n' + registration_line + parts[1][init_section_end:]
                    content = '# Initialize the app'.join(parts)
                else:
                    # Add to the end of the file as a fallback
                    content += '\n\n' + registration_line
            else:
                # Add to the end of the file as a fallback
                content += '\n\n' + registration_line
        else:
            # Try to add before the if __name__ == '__main__': block
            if 'if __name__ == ' in content:
                main_block = content.find('if __name__ == ')
                content = content[:main_block] + registration_line + '\n\n' + content[main_block:]
            else:
                # Add to the end of the file as a fallback
                content += '\n\n' + registration_line
    
    # Write updated content back to the file
    with open(app_file, 'w') as f:
        f.write(content)
    
    print(f"Updated {app_file} to include export routes")
    return True

if __name__ == '__main__':
    if update_app_file():
        print("Integration successful. Restart the application to apply changes.")
    else:
        print("Integration failed. You may need to manually update app.py.")
        sys.exit(1)