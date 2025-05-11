# WeasyPrint PDF Pagination Fix

This document outlines the comprehensive solution to the missing row issues in quotation PDFs generated with WeasyPrint. The solution addresses the problem where certain rows (particularly items #10 and #14) were being cut off or not appearing in the generated PDFs.

## Root Cause Analysis

WeasyPrint sometimes struggles with complex CSS and layout calculations, particularly with page breaks inside tables. The problem occurs because:

1. WeasyPrint's page break algorithm sometimes miscalculates the available space for a row
2. Certain rows get "lost" when they fall near page boundaries
3. CSS `page-break-inside: avoid` isn't always sufficient by itself

## The Solution

We've implemented a comprehensive solution that combines multiple techniques:

### 1. Enhanced CSS Controls

```css
/* Critical fixes for table layout and pagination */
table { 
    width: 100% !important;
    table-layout: fixed !important;
    page-break-inside: auto !important;
    border-collapse: collapse !important;
    page-break-after: auto !important;
}

/* Header and footer handling */
thead { display: table-header-group !important; }
tfoot { display: table-footer-group !important; }

/* Force row display and prevent page breaks */
tr { 
    page-break-inside: avoid !important; 
    break-inside: avoid !important;
    visibility: visible !important;
    display: table-row !important;
    height: auto !important;
}

/* Cell handling for better text wrapping */
td, th { 
    word-break: break-word !important;
    overflow-wrap: break-word !important;
    overflow: visible !important;
    height: auto !important;
}

/* Footer positioning */
.footer {
    position: fixed;
    bottom: 10mm;
    width: 100%;
    page-break-inside: avoid !important;
}
```

### 2. Pagination Technique

We've implemented a manual pagination technique that divides items into pages:

```python
def adjust_table_rows_for_pagination(items):
    """
    Adjusts the product list for better pagination.
    Organizes products into pages with a specific number of products per page.
    """
    # Calculate how many products fit on the first page (e.g., 7)
    first_page_items = 7
    
    # Calculate how many products fit on subsequent pages (e.g., 8)
    other_pages_items = 8
    
    # Organize products into pages
    paginated_items = []
    
    # First page
    if len(items) > 0:
        paginated_items.append({
            'page': 1,
            'items': items[:first_page_items]
        })
    
    # Subsequent pages
    remaining_items = items[first_page_items:]
    page_num = 2
    
    while remaining_items:
        page_items = remaining_items[:other_pages_items]
        paginated_items.append({
            'page': page_num,
            'items': page_items
        })
        remaining_items = remaining_items[other_pages_items:]
        page_num += 1
    
    return paginated_items
```

### 3. Item Position Management

We ensure all items have sequential positions, which is critical for proper ordering and rendering:

```python
def fix_item_positions(quotation):
    """
    Fix positions for all items in a quotation to ensure they're sequential.
    This helps with consistent rendering in the PDF.
    """
    if not quotation.items:
        return False
    
    # Sort items by existing position or by ID if position is None
    sorted_items = sorted(
        quotation.items, 
        key=lambda x: (x.position if hasattr(x, 'position') and x.position is not None else float('inf'), x.id)
    )
    
    # Reassign positions sequentially starting from 0
    changes_made = False
    for i, item in enumerate(sorted_items):
        if not hasattr(item, 'position') or item.position != i:
            item.position = i
            changes_made = True
    
    return changes_made
```

### 4. Advanced WeasyPrint Configuration

We've improved the WeasyPrint configuration with font handling and CSS application:

```python
# Initialize font configuration
font_config = FontConfiguration()
html = HTML(string=html_content)

# Create additional CSS for page break control
enhanced_css = CSS(string=css_string, font_config=font_config)

# Generate PDF with enhanced configuration
html.write_pdf(
    output_path,
    stylesheets=[enhanced_css],
    font_config=font_config
)
```

## Testing and Validation

The solution includes a comprehensive testing script (`test_enhanced_quotation_pdf.py`) that:

1. Tests known problematic quotations (e.g., PAK-2025-007)
2. Verifies all items are properly positioned
3. Generates PDFs with both pagination techniques
4. Provides debugging options to visualize the layout

## How to Use

### Routes

Three new routes are available:

- `/quotation/<id>/export/enhanced`: Standard enhanced PDF with pagination
- `/quotation/<id>/export/enhanced-debug`: Debug version with visual indicators
- `/quotation/<id>/export/enhanced-nopaginate`: Enhanced PDF without explicit pagination

### Integration

To add these routes to your application:

1. Add the enhanced quotation routes to your main `routes.py` file:

```python
from enhanced_quotation_routes import register_enhanced_quotation_routes
register_enhanced_quotation_routes(app)
```

## Future Improvements

1. **Database Schema**: Add a trigger or constraint to ensure quotation items always have sequential positions
2. **UI Enhancement**: Add visual indicators for item positions in the quotation editor
3. **Testing**: Implement regular automated tests to ensure PDF generation works correctly
4. **Version Updates**: Keep WeasyPrint updated to the latest version for improved rendering
5. **Monitoring**: Add telemetry to track PDF generation success/failure rates

## Conclusion

This solution provides a comprehensive fix for the WeasyPrint pagination issues by combining multiple techniques:

- Enhanced CSS controls for better page break handling
- Manual pagination for explicit control of item layout
- Proper item position management
- Advanced WeasyPrint configuration

By implementing all these techniques together, we ensure that all items in quotations are properly rendered in the generated PDFs, regardless of their position or the length of the quotation.