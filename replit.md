# Plant Pricing System

## Overview
This project is a Flask-based plant pricing system designed to streamline business operations for plant nurseries and distributors. It manages customer quotations, supplier relationships, and invoice processing, featuring automated PDF generation, Excel and PDF parsing, AI-powered insights for duplicate detection and pricing, and real-time supplier communication via Viber. The system aims to enhance efficiency, reduce manual errors, and provide a comprehensive solution for managing the complex workflows associated with plant sales and procurement.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Backend
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: PostgreSQL
- **Authentication**: Flask-Login
- **Admin Interface**: Flask-Admin
- **PDF Generation**: WeasyPrint
- **File Processing**: pandas, openpyxl, xlrd, PyPDF2
- **AI Integration**: OpenAI API for insights and duplicate detection
- **Communication**: Viber Bot API for supplier updates

### Frontend
- **Templates**: Jinja2 with Tailwind CSS
- **Design System**: Modern Tailwind CSS with a primary color of #2b8cee, rounded-xl cards, and Material Symbols icons. Features a responsive side layout.
- **Interactivity**: Vanilla JavaScript with AJAX for dynamic updates.
- **PWA**: Progressive Web App capabilities for installability and offline support (offline fallback, caching strategies).

### Core Features
- **Database Models**: Comprehensive models for Users, Customers, Suppliers, Products, Quotations, Invoices, PriceLists, and FileUploads.
- **PDF Generation**: Robust system for generating quotations, invoices, delivery notes, and supplier catalogs with custom templates and CSS.
- **File Processing**: Automated parsing of Excel and PDF files for product and pricing data, with flexible column mapping and data validation.
- **AI Integration**: AI-driven duplicate detection for supplier products, document analysis, and intelligent price recommendations.
- **Quotation Workflow**: Supports manual creation, item management, PDF generation, and status tracking.
- **Supplier Integration**: Real-time product updates via Viber and automated product catalog generation.
- **Security**: Implements CSRF protection, secure session management, and API security (Bearer token authentication).
- **Quality Gates**: Includes pytest suite for money/VAT calculations, data integrity checker, and a System Health admin page.
- **Discount System**: Comprehensive discount calculation logic for orders (percentage and fixed amount).
- **Pro Forma Invoicing**: Professional Pro Forma Invoice generation with corporate branding.
- **Pending Pricing Status**: Tracks pricing status for quotation items (CONFIRMED, PENDING, REQUESTED).

## External Dependencies

### Python Packages
- **Web**: flask, flask-sqlalchemy, flask-login, flask-admin, flask-wtf
- **Database**: psycopg2-binary, sqlalchemy
- **File Handling**: pandas, openpyxl, xlrd, pypdf2
- **PDF**: weasyprint, reportlab, fpdf2
- **AI**: openai
- **Communication**: viberbot, requests
- **Utilities**: pillow, qrcode, email-validator

### System Dependencies
- **Database Server**: PostgreSQL 16
- **Font Rendering**: fontconfig, freetype, ghostscript, pango, harfbuzz