
# Plant Pricing System Documentation

## Overview
This system allows users to manage customer-specific plant price lists by uploading Excel files and invoices (PDF). The system extracts data from these documents, associates them with customers, and provides intelligent search functionality to quickly retrieve pricing information.

## Key Features
- Upload and process Excel price lists with customer-specific pricing
- Parse PDF invoices to extract line items, prices, and metadata
- Support for scientific plant names, categories, and pot sizes
- Automatic currency and VAT handling
- Intelligent search across products and pricing data
- AI-powered document insights for quotations and invoices
- Viber integration for real-time supplier updates
- Custom supplier reporting and catalog generation
- Quotation management system
- Price update tracking and approval workflow

## Database Schema
- **Customer**: Stores customer information including name, contact details, and address
- **Product**: Stores plant product information including name, scientific name, category, and pot size
- **PriceList**: Links products to customers with specific pricing information
- **Invoice**: Tracks invoice metadata including invoice number, date, and totals
- **InvoiceItem**: Stores individual line items from invoices
- **FileUpload**: Tracks uploaded files and their processing status
- **Quotation**: Manages quotation documents and their status
- **PriceUpdate**: Tracks price change requests and approvals

## File Processing

### Excel Processing
The system supports multiple Excel formats (xlsx, xls) with flexible column mapping:
- Name/NAME (Required): Product name
- Category/CATEGORY: Optional product category
- Scientific Name/SCIENTIFIC NAME: Optional scientific plant name
- Pot/POT/Pot Size: Optional pot size information
- Price/PRICE/Selling Price: Product price

### PDF Processing
PDF invoices are processed to extract:
- Invoice number and date
- Customer information
- Line items with descriptions, quantities, prices
- Currency and VAT information
- Scientific names and pot sizes when available

## AI Integration
The system includes AI capabilities for:
- Document analysis and data extraction
- Price trend analysis and recommendations
- Quotation quality assessment
- Automated product categorization
- Smart search suggestions

## Viber Integration
The system integrates with Viber for:
- Real-time supplier price updates
- Automated product information extraction
- Supplier group message processing
- Price change notifications
- Product availability updates

## Search Functionality
The search feature allows users to search for products by:
- Product name
- Scientific name
- Category
- Pot size
- Description
- Price range
- Supplier information

Results include:
- Customer-specific pricing
- Historical price trends
- Related products
- Availability status
- Supplier information

## Technical Implementation
- Backend: Flask with SQLAlchemy ORM
- Database: PostgreSQL
- Excel Processing: pandas with openpyxl and xlrd engines
- PDF Processing: PyPDF2 with regex and text extraction
- Frontend: Bootstrap with Replit dark theme
- AI Integration: OpenAI API
- Messaging: Viber REST API

## User Interface Features
- Modern dashboard with key metrics
- Responsive design for all devices
- Dark theme support
- Interactive data visualizations
- Real-time updates
- Advanced filtering and sorting
- Bulk operations support
- Custom report generation

## Security Features
- User authentication and authorization
- Role-based access control
- Secure file handling
- API key management
- Audit logging
- Input validation and sanitization

## Reporting Features
- Custom supplier reports
- Price comparison analysis
- Quotation tracking
- Invoice summaries
- Activity logs
- Price change history
- Usage statistics

## Change Log

### 2025-04-05
- Added Viber integration for supplier updates
- Implemented AI-powered document analysis
- Enhanced quotation management system
- Added custom supplier reporting
- Improved dashboard with new metrics
- Enhanced search functionality
- Added dark theme support

### 2025-04-01
- Enhanced Excel parser to handle multiple formats
- Added case-insensitive column name matching
- Improved error handling in file processors
- Added better currency detection in PDF parser
- Enhanced VAT handling in invoices
- Added scientific name and pot size extraction from PDFs
- Added detailed logging throughout the application
