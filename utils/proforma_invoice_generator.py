"""
Pro Forma Invoice Generator for Orders

This module generates Pro Forma Invoices based on the provided template format.
It creates HTML-based invoices that can be rendered as PDF using WeasyPrint.
"""

import os
import logging
from datetime import datetime
from flask import render_template_string
from weasyprint import HTML, CSS

logger = logging.getLogger(__name__)

def generate_proforma_invoice_html(order):
    """
    Generate HTML content for a Pro Forma Invoice based on the order.
    
    Args:
        order: Order object containing the order details
        
    Returns:
        str: HTML content for the Pro Forma Invoice
    """
    
    # Calculate subtotal and VAT
    subtotal = 0.0
    vat_rate = 19.0  # Default VAT rate
    
    if order.items:
        for item in order.items:
            item_total = item.quantity * item.price
            subtotal += item_total
    
    vat_amount = subtotal * (vat_rate / 100)
    grand_total = subtotal + vat_amount
    
    # Pro Forma Invoice HTML template matching the attached design
    html_template = """
    <!DOCTYPE html>
    <html lang="el">
    <head>
      <meta charset="utf-8"/>
      <title>Pro Forma Invoice {{ order.order_number }}</title>
      <style>
        body{font-family:Arial,Helvetica,sans-serif;color:#333;margin:0;padding:40px;line-height:1.4;}
        .invoice{max-width:800px;margin:0 auto;}
        h1{font-size:28px;margin:0 0 24px;}
        .flex{display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;}
        .details div{margin-bottom:4px;}
        .items, .totals{width:100%;border-collapse:collapse;margin-top:24px;}
        .items th, .items td, .totals td{padding:8px 6px;border-bottom:1px solid #ddd;}
        .items th{background:#f5f5f5;font-weight:600;}
        .right{text-align:right;}
        .totals td{font-weight:600;}
        .totals tr:last-child td{font-size:18px;}
        .footer{margin-top:32px;font-size:12px;}
      </style>
    </head>
    <body>
      <div class="invoice">
        <h1>Pro Forma Invoice</h1>

        <div class="flex">
          <div class="from">
            <strong>Andreas Pakkoutis &amp; Sons Ltd</strong><br/>
            Griva Digeni 39, Avgorou 5510<br/>
            VAT: 10034785S<br/>
            Τηλ.: +357&nbsp;99564330
          </div>
          <div class="details right">
            <div><strong>Pro&nbsp;Forma&nbsp;No.:</strong> {{ order.order_number }}</div>
            <div><strong>Issue&nbsp;Date:</strong> {{ order.created_at.strftime('%d/%m/%Y') }}</div>
            {% if order.delivery_date %}
            <div><strong>Delivery&nbsp;Date:</strong> {{ order.delivery_date.strftime('%d/%m/%Y') }}</div>
            {% endif %}
          </div>
        </div>

        <div class="flex" style="margin-top:24px;">
          <div>
            <strong>Bill&nbsp;To:</strong><br/>
            {{ order.customer.name }}
            {% if order.customer.address %}
            <br/>{{ order.customer.address }}
            {% endif %}
          </div>
        </div>

        <table class="items">
          <thead>
            <tr>
              <th style="width:4%;">#</th>
              <th>SKU / Product</th>
              <th style="width:10%;" class="right">Qty</th>
              <th style="width:16%;" class="right">Unit&nbsp;Price&nbsp;(€)</th>
              <th style="width:16%;" class="right">Total&nbsp;(€)</th>
            </tr>
          </thead>
          <tbody>
            {% for item in order.items %}
            <tr>
              <td class="right">{{ loop.index }}</td>
              <td>{{ item.plant_name }}{% if item.size %} ({{ item.size }}){% endif %}</td>
              <td class="right">{{ item.quantity }}</td>
              <td class="right">{{ "%.2f"|format(item.price) }}</td>
              <td class="right">{{ "%.2f"|format(item.quantity * item.price) }}</td>
            </tr>
            {% endfor %}
          </tbody>
        </table>

        <table class="totals" style="margin-top:8px;">
          <tbody>
            <tr>
              <td class="right" style="width:84%;">Subtotal</td>
              <td class="right" style="width:16%;">€{{ "%.2f"|format(subtotal) }}</td>
            </tr>
            <tr>
              <td class="right">VAT&nbsp;{{ vat_rate|int }}%</td>
              <td class="right">€{{ "%.2f"|format(vat_amount) }}</td>
            </tr>
            <tr>
              <td class="right">Grand&nbsp;Total</td>
              <td class="right">€{{ "%.2f"|format(grand_total) }}</td>
            </tr>
          </tbody>
        </table>

        <div class="footer">
          <strong>Payment Terms:</strong> Within 30 days<br/>
          <strong>IBAN:</strong> CY55&nbsp;0020&nbsp;0555&nbsp;0000&nbsp;0011&nbsp;0082&nbsp;4600<br/>
          <strong>SWIFT/BIC:</strong> BCYPCY2N
        </div>
      </div>
    </body>
    </html>
    """
    
    # Render the template with order data
    html_content = render_template_string(
        html_template,
        order=order,
        subtotal=subtotal,
        vat_rate=vat_rate,
        vat_amount=vat_amount,
        grand_total=grand_total
    )
    
    return html_content

def generate_proforma_invoice_pdf(order, output_path=None):
    """
    Generate a Pro Forma Invoice PDF for the given order.
    
    Args:
        order: Order object containing the order details
        output_path: Optional path to save the PDF. If None, a default path is used.
        
    Returns:
        str: Path to the generated PDF file
    """
    
    try:
        # Generate HTML content
        html_content = generate_proforma_invoice_html(order)
        
        # Create output path if not provided
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"proforma_invoice_{order.order_number}_{timestamp}.pdf"
            output_path = os.path.join('static', 'pdfs', filename)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Generate PDF using WeasyPrint
        HTML(string=html_content).write_pdf(output_path)
        
        logger.info(f"Pro Forma Invoice PDF generated successfully: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error generating Pro Forma Invoice PDF: {e}")
        raise e

def generate_proforma_invoice_bytes(order):
    """
    Generate a Pro Forma Invoice PDF as bytes (for direct download).
    
    Args:
        order: Order object containing the order details
        
    Returns:
        bytes: PDF content as bytes
    """
    
    try:
        # Generate HTML content
        html_content = generate_proforma_invoice_html(order)
        
        # Generate PDF as bytes
        pdf_bytes = HTML(string=html_content).write_pdf()
        
        logger.info(f"Pro Forma Invoice PDF generated as bytes for order {order.order_number}")
        return pdf_bytes
        
    except Exception as e:
        logger.error(f"Error generating Pro Forma Invoice PDF bytes: {e}")
        raise e