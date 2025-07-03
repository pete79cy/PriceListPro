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
    
    # Enhanced Pro Forma Invoice HTML template with improved styling and responsive design
    html_template = """
    <!DOCTYPE html>
    <html lang="el">
    <head>
      <meta charset="utf-8"/>
      <meta name="viewport" content="width=device-width, initial-scale=1"/>
      <title>Pro Forma Invoice {{ order.order_number }}</title>
      <style>
        :root{
          --accent:#0A3D62;       /* corporate accent colour */
          --border:#d0d0d0;
          --bg-stripe:#fafafa;    /* alt‑row background */
          --pad:8px;
        }
        *{box-sizing:border-box;margin:0;padding:0;}

        /* Base layout */
        body{font-family:"Helvetica Neue",Arial,sans-serif;color:#333;background:#fff;padding:40px;line-height:1.45;}
        .invoice{max-width:800px;margin:0 auto;border:1px solid var(--border);border-radius:6px;padding:40px;box-shadow:0 4px 16px rgba(0,0,0,.05);}

        /* Headings */
        h1{font-size:26px;font-weight:700;margin-bottom:24px;letter-spacing:.5px;text-transform:uppercase;color:var(--accent);}
        h2{font-size:16px;font-weight:700;margin:0 0 4px;color:var(--accent);}

        /* Flex utilities */
        .flex{display:flex;justify-content:space-between;gap:24px;flex-wrap:wrap;}
        .w-50{flex:1 1 48%;}

        /* Blocks */
        .details div{margin-bottom:4px;font-size:14px;white-space:pre;}

        /* Table */
        table{width:100%;border-collapse:collapse;margin-top:24px;font-size:14px;}
        th,td{padding:var(--pad);text-align:left;border-bottom:1px solid var(--border);}  
        th{font-weight:600;text-transform:uppercase;font-size:12px;letter-spacing:.4px;background:var(--bg-stripe);color:var(--accent);}  
        tbody tr:nth-child(odd){background:#fdfdfd;}  /* gentle zebra striping */
        td:last-child,th:last-child{text-align:right;}
        td:first-child{text-align:center;}

        /* Totals */
        .totals{margin-top:12px;max-width:280px;margin-left:auto;font-size:14px;}
        .totals div{display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid transparent;}
        .totals div:not(:last-child){border-bottom:1px solid var(--border);}
        .totals .grand{font-weight:700;font-size:16px;color:var(--accent);}

        /* Footer */
        footer{margin-top:32px;font-size:12px;line-height:1.6;}

        /* Print‑friendly tweaks */
        @media print{
          body{padding:0;}
          .invoice{box-shadow:none;border:none;margin:0;padding:0;}
          a{color:inherit;text-decoration:none;}
        }
      </style>
    </head>
    <body>
      <section class="invoice">
        <h1>Pro Forma Invoice</h1>
        <div class="flex">
          <div class="w-50">
            <h2>Issued By</h2>
            <div>Andreas Pakkoutis &amp; Sons Ltd</div>
            <div>Griva Digeni 39, Avgorou 5510</div>
            <div>VAT: 10034785S</div>
            <div>Τηλ.: +357 99564330</div>
          </div>
          <div class="w-50">
            <h2>Invoice Details</h2>
            <div>Pro Forma No.: <strong>{{ order.order_number }}</strong></div>
            <div>Issue Date: {{ order.created_at.strftime('%d/%m/%Y') }}</div>
            {% if order.delivery_date %}
            <div>Delivery Date: {{ order.delivery_date.strftime('%d/%m/%Y') }}</div>
            {% endif %}
          </div>
        </div>

        <div class="flex" style="margin-top:24px;">
          <div class="w-50">
            <h2>Bill To</h2>
            <div>{{ order.customer.name }}</div>
            {% if order.customer.address %}
            <div>{{ order.customer.address }}</div>
            {% endif %}
          </div>
        </div>

        <table>
          <thead>
            <tr>
              <th style="width:32px;text-align:center;">#</th>
              <th>SKU / Product</th>
              <th style="width:60px;text-align:right;">Qty</th>
              <th style="width:120px;text-align:right;">Unit Price (€)</th>
              <th style="width:120px;text-align:right;">Total (€)</th>
            </tr>
          </thead>
          <tbody>
            {% for item in order.items %}
            <tr>
              <td style="text-align:center;">{{ loop.index }}</td>
              <td>{{ item.plant_name }}{% if item.size %} ({{ item.size }}){% endif %}</td>
              <td>{{ item.quantity }}</td>
              <td>{{ "%.2f"|format(item.price) }}</td>
              <td>{{ "%.2f"|format(item.quantity * item.price) }}</td>
            </tr>
            {% endfor %}
          </tbody>
        </table>

        <div class="totals">
          <div><span>Subtotal</span><span>€{{ "%.2f"|format(subtotal) }}</span></div>
          <div><span>VAT {{ vat_rate|int }}%</span><span>€{{ "%.2f"|format(vat_amount) }}</span></div>
          <div class="grand"><span>Grand Total</span><span>€{{ "%.2f"|format(grand_total) }}</span></div>
        </div>

        <footer>
          Payment Terms: Within 30 days<br>
          IBAN: CY55 0020 0555 0000 0011 0082 4600<br>
          SWIFT/BIC: BCYPCY2N
        </footer>
      </section>
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