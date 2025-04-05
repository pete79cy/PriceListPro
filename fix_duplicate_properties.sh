#!/bin/bash
# Function to fix duplicate display properties in a file
fix_duplicate_display() {
    local file="$1"
    echo "Fixing duplicate display properties in $file..."
    
    # Create a temporary file
    local tmpfile=$(mktemp)
    
    # Use sed to remove the duplicate display property
    sed '/.summary-block {/,/}/s/display: inline-block;.*\n            display: inline-block;.*/display: inline-block; \/* Use inline-block to treat as a single unit *\//' "$file" > "$tmpfile"
    
    # Replace the original file with the fixed version
    mv "$tmpfile" "$file"
    
    echo "Fixed $file"
}

# Apply the fix to all relevant files
fix_duplicate_display "templates/pdf/quotation_template.html"
fix_duplicate_display "templates/pdf/quotation_template_new.html"

# Also fix the duplicate in the @media print section for all files
for file in templates/pdf/*.html; do
    if grep -q "@media print" "$file"; then
        echo "Fixing media print section in $file..."
        local tmpfile=$(mktemp)
        sed '/@media print/,/}/s/display: inline-block;.*\n            display: inline-block;.*/display: inline-block; \/* Ensure consistent treatment as a single unit *\//' "$file" > "$tmpfile"
        mv "$tmpfile" "$file"
    fi
done

echo "All files fixed"
