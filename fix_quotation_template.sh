#!/bin/bash
# Define the files to update
update_file() {
    local file="$1"
    echo "Updating $file..."
    
    # Add display: inline-block to the main summary-block class
    sed -i '/\.summary-block {/a \            display: inline-block; /* Use inline-block to treat as a single unit */' "$file"
    
    echo "Updated $file successfully"
}

# Update both quotation template files
update_file "templates/pdf/quotation_template.html"
update_file "templates/pdf/quotation_template_new.html"

echo "All quotation templates updated"
