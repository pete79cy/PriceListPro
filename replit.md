# Plant Pricing System

## Overview

A comprehensive Flask-based plant pricing system that manages customer quotations, supplier relationships, invoice processing, and automated PDF generation. The system supports Excel file imports, PDF invoice parsing, AI-powered insights, and Viber integration for real-time supplier communication.

## System Architecture

### Backend Architecture
- **Framework**: Flask 3.1.0 with SQLAlchemy 2.0.40 ORM
- **Database**: PostgreSQL 16 with psycopg2-binary connector
- **Authentication**: Flask-Login with werkzeug password hashing
- **Admin Interface**: Flask-Admin for data management
- **PDF Generation**: WeasyPrint 65.0 for quotation and report generation
- **File Processing**: pandas, openpyxl, xlrd for Excel parsing; PyPDF2 for PDF extraction

### Frontend Architecture
- **Templates**: Jinja2 template engine with Bootstrap-based UI
- **JavaScript**: Vanilla JS with AJAX for dynamic interactions
- **CSS**: Custom styles with responsive design
- **File Uploads**: Secure file handling with validation

### External Integrations
- **OpenAI API**: For duplicate detection and AI insights
- **Viber Bot API**: Real-time supplier product updates
- **WeasyPrint**: Professional PDF generation with custom CSS

## Key Components

### Database Models
- **User**: Authentication and admin roles
- **Customer/Supplier**: Business relationship management
- **Product/SupplierProduct**: Plant inventory with scientific names
- **Quotation/QuotationItem**: Quote generation with line items
- **Invoice/InvoiceItem**: Invoice processing and tracking
- **PriceList**: Customer-specific pricing structures
- **FileUpload**: Upload tracking and processing status

### PDF Generation System
- **Enhanced PDF Generator**: Fixes for missing items and layout issues
- **Template System**: Modern quotation templates with proper CSS handling
- **Debug Mode**: Visual debugging for PDF generation issues
- **Multi-format Support**: Quotations, invoices, delivery notes, supplier catalogs

### File Processing Pipeline
- **Excel Parser**: Flexible column mapping for price lists
- **PDF Parser**: Invoice data extraction with metadata
- **Quotation Parser**: Automated quotation file processing
- **Validation**: Data integrity checks and error handling

### AI Integration
- **Duplicate Detection**: OpenAI-powered supplier product duplicate analysis
- **Document Insights**: AI analysis of quotations and invoices
- **Price Recommendations**: Intelligent pricing suggestions

## Data Flow

### Quotation Workflow
1. **Creation**: Manual quotation creation or file import
2. **Item Management**: Add/edit line items with pricing
3. **PDF Generation**: Enhanced PDF export with fixed positioning
4. **Status Tracking**: Workflow management through quotation lifecycle

### File Import Process
1. **Upload**: Secure file upload with validation
2. **Processing**: Background parsing of Excel/PDF files
3. **Data Extraction**: Product and pricing information extraction
4. **Validation**: Data integrity and format validation
5. **Integration**: Merge with existing database records

### Supplier Integration
1. **Viber Messages**: Real-time product updates via Viber webhook
2. **Product Parsing**: Automatic extraction of plant details
3. **Duplicate Detection**: AI-powered duplicate identification
4. **Catalog Generation**: PDF catalog creation for suppliers

## External Dependencies

### Python Packages
- **Flask Stack**: flask, flask-sqlalchemy, flask-login, flask-admin, flask-wtf
- **Database**: psycopg2-binary, sqlalchemy
- **File Processing**: pandas, openpyxl, xlrd, pypdf2
- **PDF Generation**: weasyprint, reportlab, fpdf2
- **AI Integration**: openai
- **Communication**: viberbot, requests, slack-sdk
- **Utilities**: pillow, qrcode, email-validator

### System Dependencies
- **PostgreSQL 16**: Primary database server
- **System Fonts**: fontconfig, freetype for PDF rendering
- **Graphics Libraries**: ghostscript, pango, harfbuzz for PDF generation

## Deployment Strategy

### Environment Configuration
- **Runtime**: Python 3.11 with Nix package management
- **Database**: PostgreSQL 16 with connection pooling
- **Server**: Gunicorn WSGI server with autoscaling deployment
- **Storage**: Local file system for uploads and generated PDFs

### Deployment Settings
- **Target**: Autoscale deployment on Replit infrastructure
- **Port**: 5000 internal, 80 external
- **Process**: Gunicorn with bind 0.0.0.0:5000 and reload capability
- **Workflows**: Parallel task execution with package installation

### Database Management
- **Migrations**: Custom migration scripts for schema updates
- **Backups**: Automated backup system with retention policies
- **Health Checks**: Database connection monitoring

## Changelog

- June 29, 2025: Added pending pricing status feature for quotation items
  - Added pricing_status column to QuotationItem model (CONFIRMED, PENDING, REQUESTED)
  - Enhanced quotation parser to handle items without prices
  - Updated edit quotation interface with pricing status controls
  - Added visual indicators for pending pricing items
  - Fixed AI price suggestion button restoration issues
- June 24, 2025: Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.