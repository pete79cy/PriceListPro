# OpenAI Integration Documentation

This document provides an overview of the OpenAI integration in the plant pricing system, focusing on supplier duplicate detection.

## Overview

The system uses OpenAI's API to analyze potential duplicate supplier products, helping users identify and manage duplicate entries more efficiently. The integration includes health checks, analysis endpoints, and a user-friendly interface for reviewing AI-generated suggestions.

## Key Components

### 1. OpenAI Health Check

A health check endpoint (`/healthcheck`) is available to verify if the OpenAI API is properly configured and accessible:

```json
// GET /healthcheck
{
  "openai_healthy": true
}
```

The health check:
- Verifies that the API key is set in the environment
- Tests the connection to OpenAI's API
- Returns a simple JSON response indicating if the API is healthy

### 2. Supplier Duplicate Analysis

The duplicate analysis flow consists of three main steps:

1. **Detection**: Find potential duplicate products for a supplier based on name similarity
2. **Analysis**: Use OpenAI to analyze each potential duplicate pair and provide recommendations
3. **Resolution**: Allow users to flag confirmed duplicates based on AI recommendations

### 3. Key Endpoints

- **GET `/healthcheck`**: Check if OpenAI API is available
- **POST `/analyze_supplier_duplicates/<supplier_id>`**: Analyze potential duplicates for a supplier
- **GET `/supplier_duplicate_results/<supplier_id>`**: View analysis results
- **POST `/flag_supplier_duplicates/<supplier_id>`**: Flag selected products as duplicates

## Implementation Details

### Analysis Process

1. When a user requests duplicate analysis for a supplier, the system first finds potential duplicate pairs using string similarity metrics.
2. Each pair is sent to OpenAI for analysis using a prompt that explains the domain context.
3. OpenAI analyzes each pair and returns:
   - Whether the products are likely duplicates
   - An explanation of why
   - Recommendations for resolution

4. Results are stored in the session and displayed to the user in a structured format.
5. Users can review recommendations and choose which duplicates to flag for resolution.

### OpenAI Prompt Design

The system uses a carefully designed prompt that explains plant nursery context:

```
Analyze these two plant nursery products from supplier '[Supplier Name]' and determine if they're duplicates:

Product 1: [product details]

Product 2: [product details]

Important context: Plant nurseries often create duplicate entries with slightly different names or details when receiving new inventory batches of the same plant. Look for these patterns:
- Slight name variations (e.g., "Monstera deliciosa" vs "Monstera Deliciosa")
- Same scientific name but slightly different common names
- Same plant but different pot sizes (these should NOT be considered duplicates)
- Same plant with slightly different pricing due to quality/size differences
- Typographical errors in product names

Provide your analysis:
1. Are these products duplicates? (yes/no/maybe)
2. Explanation: Why do you think they are or aren't duplicates?
3. Recommended action: merge, keep both, or need more information
4. If merging, which values to keep for each field (choose the more complete/accurate data)?
```

### Session Data Handling

To handle the SQLAlchemy model serialization issue, the analysis results are converted to a serializable format before storing in the session:

```python
# Convert analysis results to a serializable format
serializable_results = []
for result in analysis_results:
    serializable_result = {
        'pair': result['pair'],
        'product1': {
            'id': result['product1'].id,
            'name': result['product1'].product_name,
            'scientific_name': result['product1'].scientific_name,
            'pot_size': result['product1'].pot_size,
            'height': result['product1'].height,
            'price': result['product1'].price,
            'cost_price': result['product1'].cost_price
        },
        'product2': {
            'id': result['product2'].id,
            'name': result['product2'].product_name,
            'scientific_name': result['product2'].scientific_name,
            'pot_size': result['product2'].pot_size,
            'height': result['product2'].height,
            'price': result['product2'].price,
            'cost_price': result['product2'].cost_price
        },
        'suggestion': result['suggestion'],
        'is_duplicate': result['is_duplicate']
    }
    serializable_results.append(serializable_result)
```

## Error Handling

The integration includes comprehensive error handling:

1. **API Key Check**: The system checks if the OpenAI API key is properly configured
2. **Timeout Handling**: Requests to OpenAI include timeouts to prevent blocking
3. **User-Friendly Errors**: Clear error messages for common issues (invalid/missing API key, rate limits, etc.)
4. **Fallback Options**: If OpenAI analysis fails, the system still allows manual duplicate flagging

## Testing

The integration includes test scripts for verifying functionality:

- `test_openai_health.py`: Verify health check functionality
- `test_openai_endpoints.py`: Test the analysis endpoints

## Configuration

To use the OpenAI integration:

1. Set the `OPENAI_API_KEY` environment variable with a valid API key
2. The system will automatically use this key for all OpenAI operations
3. The key can be configured through the AI Settings page in the application

## User Interface

The interface for duplicate detection includes:

1. A list of potential duplicates with AI analysis results
2. Clearly marked suggestions (duplicate/not duplicate/needs review)
3. The full AI analysis text for each product pair
4. Checkbox controls to select which items to flag as duplicates

## Future Improvements

Potential improvements for the OpenAI integration:

1. **Batch Processing**: Process multiple suppliers in a single operation
2. **Scheduled Analysis**: Automatically run duplicate detection on a schedule
3. **Model Optimization**: Fine-tune prompts and temperature settings for better results
4. **Feedback Learning**: Incorporate user feedback to improve future analyses
