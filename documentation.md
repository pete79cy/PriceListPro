# Plant Pricing System Documentation

## Overview
This system allows users to manage customer-specific plant price lists by uploading Excel files and invoices (PDF). The system extracts data from these documents, associates them with customers, and provides intelligent search functionality to quickly retrieve pricing information.

## Key Features
- Upload and process Excel price lists with customer-specific pricing
- Parse PDF invoices to extract line items, prices, and metadata
- Support for scientific plant names, categories, and pot sizes
- Automatic currency and VAT handling
- Intelligent search across products and pricing data

## Database Schema
- **Customer**: Stores customer information including name, contact details, and address
- **Product**: Stores plant product information including name, scientific name, category, and pot size
- **PriceList**: Links products to customers with specific pricing information
- **Invoice**: Tracks invoice metadata including invoice number, date, and totals
- **InvoiceItem**: Stores individual line items from invoices
- **FileUpload**: Tracks uploaded files and their processing status

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

## Search Functionality
The search feature allows users to search for products by:
- Product name
- Scientific name
- Category
- Pot size
- Description

Results include customer-specific pricing when available.

## Technical Implementation
- Backend: Flask with SQLAlchemy ORM
- Database: PostgreSQL
- Excel Processing: pandas with openpyxl and xlrd engines
- PDF Processing: PyPDF2 with regex and text extraction
- Frontend: Bootstrap with Replit dark theme

## Change Log

### 2025-04-01
- Enhanced Excel parser to handle multiple formats (xlsx, xls)
- Added case-insensitive column name matching
- Improved error handling in file processors
- Added better currency detection in PDF parser
- Enhanced VAT handling in invoices
- Added scientific name and pot size extraction from PDFs
- Added detailed logging throughout the application