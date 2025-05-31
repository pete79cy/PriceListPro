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