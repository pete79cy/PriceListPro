# OpenAI Integration Documentation

This document describes the OpenAI integration in the Supplier Duplicate Detection system.

## Overview

The system uses OpenAI's API to analyze potential duplicate products in the supplier database. The integration includes:

1. A health check system to verify OpenAI API availability
2. A centralized service module for all OpenAI API interactions
3. Endpoints for API health monitoring and supplier duplicate analysis

## Files Modified/Added

- **services/openai_utils.py**: New file with centralized OpenAI utilities
- **app.py**: Added OpenAI health check during application startup
- **routes.py**: Updated supplier duplicate analysis endpoint and added a new healthcheck endpoint

## Endpoints

### 1. Health Check Endpoint

**Endpoint**: `/healthcheck`  
**Method**: GET  
**Description**: Checks the health of OpenAI API connection.  
**Response**:
```json
{
  "openai_healthy": true|false
}
```

### 2. Supplier Duplicate Analysis Endpoint

**Endpoint**: `/analyze_supplier_duplicates/<supplier_id>`  
**Method**: POST  
**Parameters**:
- `supplier_id`: ID of the supplier to analyze (path parameter)
- `threshold`: Similarity threshold (0-1) (query parameter, default: 0.9)

**Response**:
```json
{
  "supplier_id": 1,
  "threshold": 0.8,
  "results": [
    {
      "pair": [108, 77],
      "product1": {
        "id": 108,
        "name": "Product name",
        "scientific_name": "Scientific name"
      },
      "product2": {
        "id": 77,
        "name": "Product name",
        "scientific_name": "Scientific name"
      },
      "suggestion": "Analysis and suggestion text",
      "is_duplicate": true
    }
  ]
}
```

## Testing

A test script `test_openai_endpoints.py` has been provided to verify the functionality of both endpoints.

To run the tests:

```bash
python test_openai_endpoints.py [supplier_id] [threshold]
```

## Error Handling

The system includes robust error handling:

1. Graceful handling of missing API keys
2. Timeout management for API requests
3. Error logging for diagnostic purposes
4. Appropriate HTTP status codes for various error conditions

## Future Improvements

1. Add rate limiting controls to prevent API overuse
2. Implement caching for analysis results to reduce API costs
3. Add more detailed metrics on API usage
4. Extend OpenAI integration to other parts of the application