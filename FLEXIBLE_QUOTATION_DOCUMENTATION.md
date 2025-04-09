# Flexible Quotation PDF Generator Documentation

This document explains the new flexible quotation PDF generation system implemented to address layout issues and add field selection capabilities.

## Overview

The flexible quotation PDF generator allows users to:

1. **Select which fields** to include in the PDF quotation
2. **Choose the layout** (portrait or landscape)
3. **Apply different styles** (modern or classic)
4. **Generate PDFs** with consistent pagination and formatting

The system is designed to be modular, extensible, and robust, ensuring that all data is correctly rendered in the PDF output.

## Components

### 1. PDF Generator (`utils/flexible_pdf_generator.py`)

The core component that handles PDF generation with the following features:

- **Field Configuration**: Define fields to include with properties like width, alignment, and type
- **Data Processing**: Prepares and validates data before rendering
- **CSS Styling**: Applies appropriate CSS to ensure correct layout and pagination
- **Error Handling**: Comprehensive logging and error management

The generator defines two sets of fields:
- **DEFAULT_ITEM_FIELDS**: Standard fields included by default
- **AVAILABLE_ITEM_FIELDS**: Additional fields that can be optionally included

### 2. HTML Template (`templates/pdf/flexible_quotation_template.html`)

A responsive HTML template that:

- Dynamically renders only the selected fields
- Applies consistent styling to all elements
- Ensures proper pagination with CSS
- Includes header, footer, and summary sections

### 3. Field Selection Form (`templates/flexible_quotation_form.html`)

A user-friendly form that allows users to:

- Select which fields to include from available options
- Choose the page orientation (portrait/landscape)
- Select the design style (modern/classic)
- Access admin-only fields when appropriate

### 4. Routes (`flexible_quotation_routes.py`)

Flask routes that provide:

- Web interface for field selection and PDF generation
- API endpoints for programmatic PDF generation
- Download functionality for generated PDFs

## Usage

### Web Interface

1. Navigate to a quotation view page
2. Click the "Custom PDF" button
3. Select the desired fields and options
4. Click "Generate PDF"

### API

The system provides a JSON API endpoint for programmatic PDF generation:

```
POST /quotation/{quotation_id}/export/flexible-api
```

With JSON payload:
```json
{
  "fields": ["position", "description", "quantity", "selling_price", "total"],
  "orientation": "portrait",
  "style": "modern",
  "include_admin": false
}
```

Returns:
```json
{
  "success": true,
  "pdf_url": "https://example.com/download/flexible-quotation/filename.pdf",
  "filename": "filename.pdf"
}
```

### Programmatic Use

The generator can be used directly in Python code:

```python
from utils.flexible_pdf_generator import generate_flexible_quotation_pdf

# Get a quotation object from the database
quotation = Quotation.query.get(quotation_id)

# Generate PDF with custom fields
pdf_path = generate_flexible_quotation_pdf(
    quotation=quotation,
    selected_fields=['description', 'quantity', 'selling_price', 'total'],
    orientation='landscape',
    use_modern_style=True
)

# The PDF is now available at pdf_path
```

## Available Fields

### Standard Fields

| Field Name | Description | Type |
|------------|-------------|------|
| position | Item number | numeric |
| description | Product description | text |
| scientific_name | Scientific name | text |
| pot_size | Actual size | text |
| height | Customer specification | text |
| quantity | Quantity | numeric |
| selling_price | Unit price | currency |
| total | Total price | currency (calculated) |

### Additional Fields

| Field Name | Description | Type | Admin Only |
|------------|-------------|------|-----------|
| supplier | Supplier name | text | No |
| notes | Additional notes | text | No |
| part_number | Part number | text | No |
| reference | Reference code | text | No |
| cost_price | Cost price | currency | Yes |
| margin | Profit margin | percentage | Yes |

## Integration

To integrate the flexible quotation generator into your application:

1. Run the integration script:
   ```
   python integrate_flexible_quotation.py
   ```

2. This will:
   - Add the flexible quotation routes to your main routes.py
   - Add a "Custom PDF" button to the quotation view page
   - Verify all required templates are in place

3. Restart your Flask application

## Testing

Use the test script to verify the PDF generation:

```
python test_flexible_quotation.py
```

Options:
- `--list-fields`: List all available fields
- `--quotation={number}`: Test with a specific quotation
- `--fields={field1,field2,...}`: Specify fields to include
- `--orientation={portrait|landscape}`: Set orientation

## Troubleshooting

Common issues and solutions:

1. **Missing fields in PDF output**
   - Check if field names match exactly in template and code
   - Verify data exists for those fields in the quotation

2. **Layout issues**
   - Try different orientations for tables with many columns
   - Check CSS settings for problematic fields

3. **JavaScript errors in selection form**
   - Check browser console for specific error messages
   - Verify that all JS dependencies are loaded

4. **Slow PDF generation**
   - Consider limiting the number of items or fields
   - Check for high-resolution images that may slow rendering

## Future Improvements

Potential enhancements for the system:

1. **Saved configurations**: Allow users to save their preferred field selections
2. **PDF templates**: Support multiple design templates beyond modern/classic
3. **Custom sorting**: Allow reordering of fields in the output
4. **Field grouping**: Group related fields together in the UI and PDF
5. **Export formats**: Support additional formats like Excel or CSV
