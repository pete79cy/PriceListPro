"""
Lead management blueprint.

This module provides routes for handling leads, including quote requests
from potential customers and integrating with the external quotation system.
"""

import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from models import Lead, Customer
from utils.quoting import create_draft_quote
from utils.logger import logger
from datetime import datetime

lead_bp = Blueprint('lead', __name__, url_prefix='/lead')

@lead_bp.route('/list')
@login_required
def list_leads():
    """Display a list of all leads"""
    leads = Lead.query.order_by(Lead.created_at.desc()).all()
    return render_template('lead/list.html', leads=leads)

@lead_bp.route('/view/<int:lead_id>')
@login_required
def view_lead(lead_id):
    """View detailed information about a specific lead"""
    lead = Lead.query.get_or_404(lead_id)
    
    # Parse the items JSON for display if it exists
    items = []
    if lead.items:
        if isinstance(lead.items, str):
            try:
                items = json.loads(lead.items)
            except json.JSONDecodeError:
                flash("Error parsing lead items", "warning")
        else:
            items = lead.items
            
    return render_template('lead/view.html', lead=lead, items=items)

@lead_bp.route('/quote_request', methods=['GET', 'POST'])
def quote_request():
    """Handle a new quote request from a potential customer"""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        # Basic validation
        if not name or not email:
            flash("Name and email are required", "danger")
            return render_template('lead/quote_request.html')
            
        # Get products from the form - this will depend on how you structure your form
        items = []
        
        # If using AJAX to add products dynamically, they might be in a JSON string
        products_json = request.form.get('products_json')
        if products_json:
            try:
                items = json.loads(products_json)
            except json.JSONDecodeError:
                logger.error(f"Error parsing products JSON: {products_json}")
                flash("Error processing product information", "danger")
                return render_template('lead/quote_request.html')
        
        # Alternatively, if using form fields like product_1_name, product_1_qty, etc.
        else:
            # Example of parsing products from form fields
            i = 1
            while request.form.get(f'product_{i}_name'):
                item = {
                    'id': request.form.get(f'product_{i}_id'),
                    'name': request.form.get(f'product_{i}_name'),
                    'size': request.form.get(f'product_{i}_size', ''),
                    'qty': int(request.form.get(f'product_{i}_qty', 1))
                }
                items.append(item)
                i += 1
                
        # Create new lead
        lead = Lead(
            name=name,
            email=email,
            phone=phone,
            message=message,
            source='website',
            items=items,
            status='New',
            created_at=datetime.utcnow()
        )
        
        db.session.add(lead)
        
        try:
            db.session.commit()
            logger.info(f"Created new lead: {lead.name} (ID: {lead.id})")
            
            # Send slack notification (if implemented)
            try:
                from utils.notifications import send_slack_notification
                send_slack_notification(lead)
            except (ImportError, Exception) as e:
                logger.warning(f"Failed to send Slack notification: {str(e)}")
            
            # Create draft in external quotation system
            draft = create_draft_quote(lead)
            
            if not draft:
                flash("Your quote request has been received, but there was an issue creating a draft in our quotation system. Our team will be notified.", "warning")
            else:
                flash("Your quote request has been received. A draft quote has been created in our system.", "success")
                
            return redirect(url_for('lead.quote_confirmation'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving lead: {str(e)}")
            flash(f"Error processing your request: {str(e)}", "danger")
            
    # GET request - display the form
    return render_template('lead/quote_request.html')

@lead_bp.route('/quote_confirmation')
def quote_confirmation():
    """Display a confirmation page after a quote request is submitted"""
    return render_template('lead/quote_confirmation.html')

@lead_bp.route('/<int:lead_id>/convert_to_customer', methods=['POST'])
@login_required
def convert_to_customer(lead_id):
    """Convert a lead to a customer"""
    lead = Lead.query.get_or_404(lead_id)
    
    # Check if customer with this email already exists
    existing_customer = None
    if lead.email:
        existing_customer = Customer.query.filter_by(email=lead.email).first()
        
    if existing_customer:
        # Update the lead status
        lead.status = 'Converted'
        flash(f"Lead linked to existing customer: {existing_customer.name}", "info")
    else:
        # Create a new customer from the lead
        new_customer = Customer(
            name=lead.name,
            email=lead.email,
            phone=lead.phone,
        )
        db.session.add(new_customer)
        
        # Update the lead status
        lead.status = 'Converted'
        
        flash(f"Lead converted to new customer: {lead.name}", "success")
    
    try:
        db.session.commit()
        return redirect(url_for('lead.view_lead', lead_id=lead_id))
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error converting lead to customer: {str(e)}")
        flash(f"Error converting lead: {str(e)}", "danger")
        return redirect(url_for('lead.view_lead', lead_id=lead_id))