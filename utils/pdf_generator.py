"""
PDF Generator for delivery notes and other documents
Uses WeasyPrint to generate PDFs from HTML templates
"""
import os
from datetime import datetime
from flask import render_template, current_app
from weasyprint import HTML, CSS
import logging

def generate_delivery_note(order, language='en'):
    """
    Generate a PDF delivery note for an order
    
    Args:
        order: The order object to generate the delivery note for
        language (str): Language code for translations ('en', 'el', 'ar')
        
    Returns:
        bytes: The PDF file as bytes
    """
    # Get translations for the specified language
    from utils.translations import get_translations
    translations = get_translations(language)
    
    # Render the HTML template with order details and translations
    html = render_template('pdfs/delivery_note.html',
                          order=order,
                          translations=translations,
                          language=language,
                          date=datetime.now().strftime('%Y-%m-%d'))
    
    # Generate PDF using WeasyPrint
    pdf = HTML(string=html).write_pdf()
    return pdf

def generate_delivery_note_pdf(order, language='en'):
    """Alias for generate_delivery_note with the _pdf suffix for consistent naming"""
    return generate_delivery_note(order, language)

def generate_quotation_pdf(quotation, items=None):
    """
    Generate a PDF for a quotation
    
    Args:
        quotation: The quotation object
        items: Optional list of quotation items (if not provided, will use quotation.items)
        
    Returns:
        bytes: The PDF file as bytes
    """
    # Basic implementation - this would be expanded with actual HTML rendering
    html = render_template('pdfs/quotation.html', 
                          quotation=quotation,
                          items=items or quotation.items)
    pdf = HTML(string=html).write_pdf()
    return pdf

def generate_supplier_pdf_report(supplier, items=None, title=None):
    """
    Generate a PDF report for a supplier
    
    Args:
        supplier: The supplier object
        items: Optional list of supplier products
        title: Optional custom title for the report
        
    Returns:
        bytes: The PDF file as bytes
    """
    # Basic implementation
    html = render_template('pdfs/supplier_report.html',
                          supplier=supplier,
                          items=items,
                          title=title or f"Supplier Report: {supplier.name}")
    pdf = HTML(string=html).write_pdf()
    return pdf

def generate_supplier_products_pdf(supplier, products=None):
    """
    Generate a PDF of products for a supplier
    
    Args:
        supplier: The supplier object
        products: Optional list of products
        
    Returns:
        bytes: The PDF file as bytes
    """
    # Basic implementation
    html = render_template('pdfs/supplier_products.html',
                          supplier=supplier,
                          products=products or supplier.products)
    pdf = HTML(string=html).write_pdf()
    return pdf

def generate_supplier_catalog_pdf(supplier, categories=None):
    """
    Generate a product catalog PDF for a supplier
    
    Args:
        supplier: The supplier object
        categories: Optional list of product categories
        
    Returns:
        bytes: The PDF file as bytes
    """
    # Basic implementation
    html = render_template('pdfs/supplier_catalog.html',
                          supplier=supplier,
                          categories=categories)
    pdf = HTML(string=html).write_pdf()
    return pdf