#!/usr/bin/env python3

with open('templates/custom_supplier_report.html', 'r') as f:
    content = f.read()

# Remove all DejaVu checkboxes
import re
content = re.sub(r'<div class="form-check mb-3">\s*<input class="form-check-input" type="checkbox" name="use_dejavu" id="useDejavu">.*?</div>', '', content, flags=re.DOTALL)

# Save the file
with open('templates/custom_supplier_report.html', 'w') as f:
    f.write(content)

print("Cleaned template successfully")
