"""
PDF utilities for delivery adjustments
"""
import os
import tempfile
from datetime import datetime
from flask import render_template_string
from weasyprint import HTML, CSS
import logging

def generate_delivery_adjustment_pdf(adjustment):
    """
    Generate a PDF for a delivery adjustment (RET-xxx, ADD-xxx, etc.)
    
    Args:
        adjustment: DeliveryAdjustment object
        
    Returns:
        str: Path to the generated PDF file
    """
    
    # HTML template for delivery adjustment
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{{ adjustment.adjustment_number }}</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                color: #333;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 2px solid #007bff;
            }
            .header h1 {
                color: #007bff;
                margin: 0;
                font-size: 28px;
            }
            .header .subtitle {
                color: #666;
                font-size: 16px;
                margin-top: 5px;
            }
            .info-section {
                display: flex;
                justify-content: space-between;
                margin-bottom: 30px;
            }
            .info-box {
                flex: 1;
                margin-right: 20px;
            }
            .info-box:last-child {
                margin-right: 0;
            }
            .info-box h3 {
                color: #007bff;
                font-size: 14px;
                margin: 0 0 10px 0;
                text-transform: uppercase;
                border-bottom: 1px solid #ddd;
                padding-bottom: 5px;
            }
            .info-box p {
                margin: 5px 0;
                font-size: 14px;
            }
            .items-table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 30px;
            }
            .items-table th {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
                font-weight: bold;
                color: #495057;
            }
            .items-table td {
                border: 1px solid #ddd;
                padding: 12px;
                vertical-align: top;
            }
            .items-table tr:nth-child(even) {
                background-color: #f8f9fa;
            }
            .summary {
                background-color: #f8f9fa;
                padding: 20px;
                border-left: 4px solid #007bff;
                margin-bottom: 20px;
            }
            .summary h3 {
                margin: 0 0 15px 0;
                color: #007bff;
            }
            .total-row {
                font-weight: bold;
                font-size: 16px;
            }
            .type-badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                text-transform: uppercase;
            }
            .type-return { background-color: #dc3545; }
            .type-additional { background-color: #28a745; }
            .type-replacement { background-color: #ffc107; color: #000; }
            .status-badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                text-transform: uppercase;
            }
            .status-pending { background-color: #ffc107; color: #000; }
            .status-confirmed { background-color: #28a745; }
            .status-processed { background-color: #007bff; }
            .status-cancelled { background-color: #dc3545; }
            .footer {
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-size: 12px;
                color: #666;
                text-align: center;
            }
            .text-right { text-align: right; }
            .text-center { text-align: center; }
            .negative { color: #dc3545; }
            .positive { color: #28a745; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{{ adjustment.get_type_label() }}</h1>
            <div class="subtitle">{{ adjustment.adjustment_number }}</div>
        </div>

        <div class="info-section">
            <div class="info-box">
                <h3>Adjustment Details</h3>
                <p><strong>Type:</strong> 
                    <span class="type-badge type-{{ adjustment.adjustment_type }}">
                        {{ adjustment.get_type_label() }}
                    </span>
                </p>
                <p><strong>Status:</strong> 
                    <span class="status-badge status-{{ adjustment.status }}">
                        {{ adjustment.get_status_label() }}
                    </span>
                </p>
                <p><strong>Date:</strong> {{ adjustment.adjustment_date.strftime('%B %d, %Y') }}</p>
                <p><strong>Created:</strong> {{ adjustment.created_at.strftime('%B %d, %Y at %I:%M %p') }}</p>
            </div>

            <div class="info-box">
                <h3>Related Document</h3>
                {% if adjustment.order %}
                <p><strong>Order Number:</strong> {{ adjustment.order.order_number }}</p>
                <p><strong>Customer:</strong> {{ adjustment.order.customer.name }}</p>
                <p><strong>Original Total:</strong> €{{ "%.2f"|format(adjustment.order.items|sum(attribute='total')) }}</p>
                {% elif adjustment.quotation %}
                <p><strong>Quotation Number:</strong> {{ adjustment.quotation.quotation_number }}</p>
                <p><strong>Customer:</strong> {{ adjustment.quotation.customer.name }}</p>
                <p><strong>Original Total:</strong> €{{ "%.2f"|format(adjustment.quotation.items|sum(attribute='total')) }}</p>
                {% endif %}
            </div>

            <div class="info-box">
                <h3>Financial Impact</h3>
                <p><strong>Items Count:</strong> {{ adjustment.items|length }}</p>
                <p><strong>Adjustment Value:</strong> €{{ "%.2f"|format(adjustment.total_value) }}</p>
                <p><strong>Net Impact:</strong> 
                    {% if adjustment.signed_total_value < 0 %}
                        <span class="negative">-€{{ "%.2f"|format(adjustment.signed_total_value|abs) }}</span>
                    {% else %}
                        <span class="positive">+€{{ "%.2f"|format(adjustment.signed_total_value) }}</span>
                    {% endif %}
                </p>
            </div>
        </div>

        {% if adjustment.reason %}
        <div class="summary">
            <h3>Adjustment Reason</h3>
            <p>{{ adjustment.reason }}</p>
        </div>
        {% endif %}

        <h3>Items</h3>
        <table class="items-table">
            <thead>
                <tr>
                    <th style="width: 40%;">Plant Name</th>
                    <th style="width: 15%;">Size</th>
                    <th style="width: 10%;">Quantity</th>
                    <th style="width: 15%;">Unit Price</th>
                    <th style="width: 10%;">VAT Rate</th>
                    <th style="width: 15%;">Total</th>
                </tr>
            </thead>
            <tbody>
                {% for item in adjustment.items %}
                <tr>
                    <td>
                        <strong>{{ item.plant_name }}</strong>
                        {% if item.reason %}
                        <br><small style="color: #666;">{{ item.reason }}</small>
                        {% endif %}
                    </td>
                    <td>{{ item.size or '-' }}</td>
                    <td class="text-center">{{ item.quantity }}</td>
                    <td class="text-right">€{{ "%.2f"|format(item.unit_price) }}</td>
                    <td class="text-center">{{ item.vat_rate }}%</td>
                    <td class="text-right">€{{ "%.2f"|format(item.get_total()) }}</td>
                </tr>
                {% endfor %}
                <tr class="total-row">
                    <td colspan="5" class="text-right">Total Adjustment Value:</td>
                    <td class="text-right">€{{ "%.2f"|format(adjustment.total_value) }}</td>
                </tr>
                <tr class="total-row">
                    <td colspan="5" class="text-right">
                        Net Impact on Invoice:
                        <small style="font-weight: normal;">
                            ({{ "Credit" if adjustment.signed_total_value < 0 else "Charge" }})
                        </small>
                    </td>
                    <td class="text-right">
                        {% if adjustment.signed_total_value < 0 %}
                            <span class="negative">-€{{ "%.2f"|format(adjustment.signed_total_value|abs) }}</span>
                        {% else %}
                            <span class="positive">+€{{ "%.2f"|format(adjustment.signed_total_value) }}</span>
                        {% endif %}
                    </td>
                </tr>
            </tbody>
        </table>

        {% if adjustment.notes %}
        <div class="summary">
            <h3>Additional Notes</h3>
            <p>{{ adjustment.notes }}</p>
        </div>
        {% endif %}

        <div class="footer">
            <p>Generated on {{ datetime.now().strftime('%B %d, %Y at %I:%M %p') }}</p>
            <p>{{ adjustment.adjustment_number }} | {{ adjustment.get_type_label() }} | {{ adjustment.get_status_label() }}</p>
        </div>
    </body>
    </html>
    """
    
    try:
        # Render the HTML template
        html_content = render_template_string(html_template, adjustment=adjustment, datetime=datetime)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False, encoding='utf-8') as temp_file:
            pdf_path = temp_file.name
        
        # Generate PDF
        HTML(string=html_content).write_pdf(pdf_path)
        
        logging.info(f"Generated PDF for adjustment {adjustment.adjustment_number} at {pdf_path}")
        return pdf_path
        
    except Exception as e:
        logging.error(f"Error generating PDF for adjustment {adjustment.adjustment_number}: {e}")
        raise e

def generate_final_invoice_pdf(final_invoice):
    """
    Generate a PDF for a final proforma invoice (FPI-xxx)
    
    Args:
        final_invoice: FinalProformaInvoice object
        
    Returns:
        str: Path to the generated PDF file
    """
    
    # Enhanced HTML template for pro forma invoice with detailed improvements
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Pro Forma Invoice {{ final_invoice.invoice_number }}</title>
        <style>
            @page {
                size: A4;
                margin: 20mm;
                @bottom-center {
                    content: "Page " counter(page) " of " counter(pages);
                    font-size: 10px;
                    color: #666;
                }
            }
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                color: #333;
                line-height: 1.4;
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 2px solid #007bff;
            }
            .logo-section {
                flex: 1;
            }
            .logo-section h1 {
                color: #007bff;
                margin: 0;
                font-size: 24px;
                font-weight: bold;
            }
            .logo-section .company-info {
                font-size: 12px;
                color: #666;
                margin-top: 5px;
            }
            .invoice-title {
                flex: 2;
                text-align: center;
            }
            .invoice-title h1 {
                color: #007bff;
                margin: 0;
                font-size: 28px;
                font-weight: bold;
            }
            .invoice-title .subtitle {
                color: #666;
                font-size: 14px;
                margin-top: 5px;
            }
            .invoice-number {
                flex: 1;
                text-align: right;
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
            }
            .invoice-number .number {
                font-size: 18px;
                font-weight: bold;
                color: #007bff;
            }
            .invoice-number .date {
                font-size: 12px;
                color: #666;
                margin-top: 3px;
            }
            .parties-section {
                display: flex;
                justify-content: space-between;
                margin-bottom: 25px;
                gap: 20px;
            }
            .party-box {
                flex: 1;
                padding: 15px;
                background-color: #f8f9fa;
                border-left: 4px solid #007bff;
                border-radius: 3px;
            }
            .party-box h3 {
                color: #007bff;
                font-size: 12px;
                margin: 0 0 8px 0;
                text-transform: uppercase;
                font-weight: bold;
                letter-spacing: 0.5px;
            }
            .party-box p {
                margin: 3px 0;
                font-size: 11px;
                line-height: 1.3;
            }
            .party-box .company-name {
                font-weight: bold;
                font-size: 13px;
                color: #333;
            }
            .payment-terms {
                background-color: #e3f2fd;
                padding: 12px;
                border-left: 4px solid #2196f3;
                margin-bottom: 20px;
                border-radius: 3px;
            }
            .payment-terms h4 {
                margin: 0 0 6px 0;
                font-size: 12px;
                color: #2196f3;
                text-transform: uppercase;
                font-weight: bold;
            }
            .payment-terms p {
                margin: 2px 0;
                font-size: 11px;
            }
            .items-table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
                font-size: 11px;
                background-color: white;
            }
            .items-table th {
                background-color: #007bff;
                color: white;
                border: 1px solid #007bff;
                padding: 8px;
                text-align: left;
                font-weight: bold;
                font-size: 10px;
                text-transform: uppercase;
            }
            .items-table td {
                border: 1px solid #ddd;
                padding: 6px 8px;
                vertical-align: top;
                font-size: 10px;
            }
            .items-table tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .items-table .text-right {
                text-align: right;
            }
            .items-table .text-center {
                text-align: center;
            }
            .summary-section {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }
            .summary-table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 15px;
                font-size: 11px;
            }
            .summary-table th {
                background-color: #e9ecef;
                color: #495057;
                border: 1px solid #dee2e6;
                padding: 8px;
                text-align: left;
                font-weight: bold;
                font-size: 10px;
            }
            .summary-table td {
                border: 1px solid #dee2e6;
                padding: 8px;
                vertical-align: top;
                font-size: 10px;
            }
            .summary-table .total-row {
                background-color: #e3f2fd;
                font-weight: bold;
            }
            .adjustments-table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 30px;
            }
            .adjustments-table th {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
                font-weight: bold;
                color: #495057;
            }
            .adjustments-table td {
                border: 1px solid #ddd;
                padding: 12px;
                vertical-align: top;
            }
            .adjustments-table tr:nth-child(even) {
                background-color: #fdfdfd;
            }
            .total-section {
                background-color: #007bff;
                color: white;
                padding: 20px;
                margin-bottom: 20px;
                text-align: center;
                border-radius: 5px;
            }
            .total-section h2 {
                margin: 0;
                font-size: 24px;
            }
            .total-section .amount {
                font-size: 32px;
                font-weight: bold;
                margin-top: 10px;
            }
            .footer {
                margin-top: 40px;
                padding-top: 20px;
                border-top: 2px solid #ddd;
                font-size: 12px;
                color: #666;
                text-align: center;
            }
            .text-right { text-align: right; }
            .text-center { text-align: center; }
            .negative { color: #dc3545; font-weight: bold; }
            .positive { color: #28a745; font-weight: bold; }
            .neutral { color: #6c757d; }
            .badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                text-transform: uppercase;
            }
            .badge-return { background-color: #dc3545; }
            .badge-additional { background-color: #28a745; }
            .badge-replacement { background-color: #ffc107; color: #000; }
        </style>
    </head>
    <body>
        <!-- Enhanced Header with Logo and Clear Title -->
        <div class="header">
            <div class="logo-section">
                <!-- Logo section left empty as requested -->
            </div>
            <div class="invoice-title">
                <h1>Pro Forma Invoice</h1>
                <div class="subtitle">For customs and quotation purposes only</div>
            </div>
            <div class="invoice-number">
                <div class="number">{{ final_invoice.invoice_number }}</div>
                <div class="date">{{ final_invoice.invoice_date.strftime('%-d %B %Y') }}</div>
                <div class="date">Rev A</div>
            </div>
        </div>

        <!-- Parties Information (Seller & Buyer) -->
        <div class="parties-section">
            <div class="party-box">
                <h3>Seller / From</h3>
                <p class="company-name">Andreas Pakkoutis & Sons Ltd</p>
                <p>Griva Digeni 39</p>
                <p>Avgorou 5510, Cyprus</p>
                <p>VAT ID: 10034785 S</p>
                <p>REG: 12034785 U</p>
                <p>Tel: +357 99564330</p>
                <p>Email: panayiotis@pakkoutis.com</p>
            </div>
            
            <div class="party-box">
                <h3>Buyer / Ship To</h3>
                {% if final_invoice.quotation %}
                <p class="company-name">{{ final_invoice.quotation.customer.name }}</p>
                {% if final_invoice.quotation.customer.address %}
                    {% for line in final_invoice.quotation.customer.address.split('\n') %}
                    <p>{{ line.strip() }}</p>
                    {% endfor %}
                {% else %}
                <p>[Address to be provided]</p>
                {% endif %}
                {% if final_invoice.quotation.customer.email %}
                <p>Email: {{ final_invoice.quotation.customer.email }}</p>
                {% endif %}
                {% if final_invoice.quotation.customer.phone %}
                <p>Tel: {{ final_invoice.quotation.customer.phone }}</p>
                {% endif %}
                {% elif final_invoice.order %}
                <p class="company-name">{{ final_invoice.order.customer.name }}</p>
                {% if final_invoice.order.customer.address %}
                    {% for line in final_invoice.order.customer.address.split('\n') %}
                    <p>{{ line.strip() }}</p>
                    {% endfor %}
                {% endif %}
                {% endif %}
            </div>
            
            <div class="party-box">
                <h3>Invoice Details</h3>
                <p><strong>Invoice No:</strong> {{ final_invoice.invoice_number }}</p>
                <p><strong>Date:</strong> {{ final_invoice.invoice_date.strftime('%-d %B %Y') }}</p>
                {% if final_invoice.quotation %}
                <p><strong>Reference:</strong> {{ final_invoice.quotation.quotation_number }}</p>
                {% endif %}
                <p><strong>Currency:</strong> EUR (€)</p>
            </div>
        </div>

        <!-- Payment Terms -->
        <div class="payment-terms">
            <h4>Payment Terms & Bank Details</h4>
            <p><strong>Terms:</strong> 50% advance payment, 50% prior to delivery</p>
            <p><strong>Bank:</strong> Bank of Cyprus • <strong>IBAN:</strong> CY55 0020 0555 0000 0011 0082 4600 • <strong>SWIFT:</strong> BCYPCY2N</p>
            <p><strong>Beneficiary:</strong> Andreas Pakkoutis & Sons Ltd</p>
        </div>

        <!-- Detailed Line Items Table -->
        {% if final_invoice.quotation and final_invoice.quotation.items %}
        <h3>Line Items from Quotation {{ final_invoice.quotation.quotation_number }}</h3>
        <table class="items-table">
            <thead>
                <tr>
                    <th style="width: 8%;">Item #</th>
                    <th style="width: 35%;">Description</th>
                    <th style="width: 8%;">Qty</th>
                    <th style="width: 12%;">Unit Price</th>
                    <th style="width: 12%;">Line Total</th>
                    <th style="width: 8%;">VAT%</th>
                    <th style="width: 10%;">VAT Amount</th>
                    <th style="width: 12%;">Total Inc VAT</th>
                </tr>
            </thead>
            <tbody>
                {% for item in final_invoice.quotation.items %}
                {% set vat_amount = item.total * (item.vat_rate / 100) %}
                {% set total_inc_vat = item.total + vat_amount %}
                <tr>
                    <td class="text-center">{{ loop.index }}</td>
                    <td>{{ item.description }}</td>
                    <td class="text-center">{{ item.quantity }}</td>
                    <td class="text-right">€{{ "%.2f"|format(item.selling_price) }}</td>
                    <td class="text-right">€{{ "%.2f"|format(item.total) }}</td>
                    <td class="text-center">{{ item.vat_rate }}%</td>
                    <td class="text-right">€{{ "%.2f"|format(vat_amount) }}</td>
                    <td class="text-right">€{{ "%.2f"|format(total_inc_vat) }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}

        <!-- Delivery Adjustments Detail -->
        {% if final_invoice.quotation and final_invoice.quotation.delivery_adjustments %}
        <h3>Delivery Adjustments Detail</h3>
        {% for adjustment in final_invoice.quotation.delivery_adjustments %}
        {% if adjustment.status == 'confirmed' %}
        <h4>{{ adjustment.get_type_label() }} {{ adjustment.adjustment_number }} - {{ adjustment.adjustment_date.strftime('%-d %B %Y') }}</h4>
        <table class="items-table">
            <thead>
                <tr>
                    <th style="width: 8%;">Item #</th>
                    <th style="width: 40%;">Description</th>
                    <th style="width: 10%;">Qty</th>
                    <th style="width: 12%;">Unit Price</th>
                    <th style="width: 12%;">Line Total</th>
                    <th style="width: 8%;">VAT%</th>
                    <th style="width: 10%;">Total Inc VAT</th>
                </tr>
            </thead>
            <tbody>
                {% for adj_item in adjustment.items %}
                {% set line_total = adj_item.quantity * adj_item.unit_price %}
                {% set vat_amount = line_total * (adj_item.vat_rate / 100) if adj_item.vat_rate else 0 %}
                {% set total_inc_vat = line_total + vat_amount %}
                <tr>
                    <td class="text-center">{{ loop.index }}</td>
                    <td>{{ adj_item.plant_name }}</td>
                    <td class="text-center">{{ adj_item.quantity }}</td>
                    <td class="text-right">€{{ "%.2f"|format(adj_item.unit_price) }}</td>
                    <td class="text-right">
                        {% if adjustment.adjustment_type == 'return' %}
                            <span class="negative">-€{{ "%.2f"|format(line_total) }}</span>
                        {% else %}
                            €{{ "%.2f"|format(line_total) }}
                        {% endif %}
                    </td>
                    <td class="text-center">{{ adj_item.vat_rate or 19 }}%</td>
                    <td class="text-right">
                        {% if adjustment.adjustment_type == 'return' %}
                            <span class="negative">-€{{ "%.2f"|format(total_inc_vat) }}</span>
                        {% else %}
                            €{{ "%.2f"|format(total_inc_vat) }}
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}
        {% endfor %}
        {% endif %}

        <!-- Financial Summary -->
        <div class="summary-section">
            <h3>Financial Summary</h3>
            <table class="summary-table">
                <tr>
                    <td><strong>Subtotal (Net Amount):</strong></td>
                    <td class="text-right">€{{ "%.2f"|format(final_invoice.original_total) }}</td>
                </tr>
                {% if final_invoice.adjustments_total != 0 %}
                <tr>
                    <td><strong>Delivery Adjustments:</strong></td>
                    <td class="text-right">
                        {% if final_invoice.adjustments_total < 0 %}
                            <span class="negative">€{{ "%.2f"|format(final_invoice.adjustments_total) }}</span>
                        {% else %}
                            <span class="positive"> + €{{ "%.2f"|format(final_invoice.adjustments_total) }}</span>
                        {% endif %}
                    </td>
                </tr>
                {% endif %}
                <tr class="total-row">
                    <td><strong>Net Total:</strong></td>
                    <td class="text-right"><strong>€{{ "%.2f"|format(final_invoice.final_total) }}</strong></td>
                </tr>
            </table>
        </div>

        <!-- Terms & Conditions and Disclaimers -->
        <div style="margin-top: 25px; padding: 15px; background-color: #f8f9fa; border-radius: 5px; font-size: 10px;">
            <h4 style="margin: 0 0 8px 0; font-size: 11px; color: #007bff;">Terms & Conditions</h4>
            <ul style="margin: 0; padding-left: 15px; line-height: 1.4;">
                <li>This pro forma invoice is issued for customs and quotation purposes only and does <strong>not</strong> constitute a legal tax invoice.</li>
                <li>Offer valid for 15 days from issue date: {{ final_invoice.invoice_date.strftime('%-d %B %Y') }}.</li>
                <li>Payment terms: 50% advance payment, 50% prior to delivery.</li>
                <li>Delivery timeframe will be confirmed upon order placement.</li>
                <li>All prices are inclusive of applicable taxes as indicated.</li>
                <li>Prices subject to change without prior notice after validity period.</li>
            </ul>
        </div>

        {% if final_invoice.notes %}
        <div style="background-color: #fff3cd; padding: 12px; border-left: 4px solid #ffc107; margin: 15px 0; border-radius: 3px;">
            <h4 style="margin: 0 0 6px 0; color: #856404; font-size: 11px;">Additional Notes</h4>
            <p style="margin: 0; font-size: 10px; color: #856404;">{{ final_invoice.notes }}</p>
        </div>
        {% endif %}

        <!-- Delivery Adjustments Explanation (if adjustments exist) -->
        {% if final_invoice.quotation and final_invoice.quotation.delivery_adjustments %}
        <div style="page-break-before: always; margin-top: 40px; padding: 20px; background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; font-size: 11px; line-height: 1.5;">
            <h3 style="margin: 0 0 15px 0; font-size: 14px; color: #007bff; text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 10px;">Understanding Delivery Adjustments in Pro Forma Invoices</h3>
            
            <div style="margin-bottom: 15px;">
                <h4 style="margin: 0 0 8px 0; font-size: 12px; color: #495057;">Overview</h4>
                <p style="margin: 0 0 10px 0; text-align: justify;">
                    This Pro Forma Invoice includes delivery adjustments that modify the final invoice amount after the original quotation was delivered. 
                    These adjustments ensure accurate billing by accounting for any changes that occurred during or after the delivery process.
                </p>
            </div>

            <div style="margin-bottom: 15px;">
                <h4 style="margin: 0 0 8px 0; font-size: 12px; color: #495057;">Types of Adjustments</h4>
                <div style="margin-left: 15px;">
                    <p style="margin: 3px 0;"><strong>• Product Returns:</strong> Items returned by the customer are credited (subtracted) from the invoice total.</p>
                    <p style="margin: 3px 0;"><strong>• Additional Deliveries:</strong> Extra items delivered are charged (added) to the invoice total.</p>
                    <p style="margin: 3px 0;"><strong>• Product Replacements:</strong> Replacement items provided are charged (added) to the invoice total.</p>
                </div>
            </div>

            <div style="margin-bottom: 15px;">
                <h4 style="margin: 0 0 8px 0; font-size: 12px; color: #495057;">Calculation Method</h4>
                <p style="margin: 0 0 10px 0; text-align: justify;">
                    The final Pro Forma Invoice total is calculated using the following formula:
                </p>
                <div style="background-color: #e3f2fd; padding: 10px; border-left: 4px solid #2196f3; margin: 10px 0; font-family: monospace; text-align: center;">
                    <strong>Final Total = Original Quotation Total + Delivery Adjustments</strong>
                </div>
                <p style="margin: 5px 0 0 0; font-size: 10px; color: #666;">
                    Where delivery adjustments are automatically signed: returns as negative values (credits), additions and replacements as positive values (charges).
                </p>
            </div>

            <div style="margin-bottom: 15px;">
                <h4 style="margin: 0 0 8px 0; font-size: 12px; color: #495057;">Individual Item Calculation</h4>
                <p style="margin: 0 0 5px 0;">For each adjustment item, the following calculations apply:</p>
                <div style="margin-left: 15px; font-size: 10px;">
                    <p style="margin: 2px 0;">• Line Total = Quantity × Unit Price</p>
                    <p style="margin: 2px 0;">• VAT Amount = Line Total × (VAT Rate ÷ 100)</p>
                    <p style="margin: 2px 0;">• Total Including VAT = Line Total + VAT Amount</p>
                </div>
            </div>

            <div style="margin-bottom: 15px;">
                <h4 style="margin: 0 0 8px 0; font-size: 12px; color: #495057;">Quality Assurance</h4>
                <p style="margin: 0; text-align: justify;">
                    All delivery adjustments included in this invoice have been confirmed and verified. Only adjustments with "confirmed" status 
                    are reflected in the final calculation, ensuring accuracy and preventing unauthorized modifications to the invoice total.
                </p>
            </div>

            <div style="background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin-top: 15px; border-radius: 3px;">
                <p style="margin: 0; font-size: 10px; color: #856404; font-style: italic;">
                    <strong>Note:</strong> This explanation is provided for transparency and clarity regarding the adjustment calculations reflected in this Pro Forma Invoice. 
                    All adjustments are documented with detailed line items above for your review and records.
                </p>
            </div>
        </div>
        {% endif %}

        <!-- Footer -->
        <div style="margin-top: 30px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 9px; color: #666; text-align: center;">
            <p style="margin: 2px 0;"><strong>{{ final_invoice.invoice_number }}</strong> | Pro Forma Invoice | Rev A</p>
            <p style="margin: 2px 0;">Generated on {{ datetime.now().strftime('%-d %B %Y at %H:%M') }}</p>
            <p style="margin: 2px 0;">Page 1 of 1 | Pakkoutis Plant & Garden Solutions</p>
            <p style="margin: 2px 0; font-style: italic;">This document includes all confirmed delivery adjustments</p>
        </div>
    </body>
    </html>
    """
    
    try:
        # Render the HTML template
        html_content = render_template_string(html_template, final_invoice=final_invoice, datetime=datetime)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False, encoding='utf-8') as temp_file:
            pdf_path = temp_file.name
        
        # Generate PDF
        HTML(string=html_content).write_pdf(pdf_path)
        
        logging.info(f"Generated PDF for final invoice {final_invoice.invoice_number} at {pdf_path}")
        return pdf_path
        
    except Exception as e:
        logging.error(f"Error generating PDF for final invoice {final_invoice.invoice_number}: {e}")
        raise e