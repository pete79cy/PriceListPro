import os
import uuid
import re
import traceback
import time
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, jsonify, flash, send_from_directory, session, make_response
from werkzeug.utils import secure_filename
from app import db
from models import User, Customer, CustomerCategory, CustomerContact, Product, PriceList, Invoice, InvoiceItem, FileUpload, ProductUpdateRequest, Quotation, QuotationItem, Supplier, SupplierProduct, CompanySettings
from flask_login import login_user, logout_user, login_required, current_user
from utils.excel_parser import parse_excel_file
from utils.pdf_parser import extract_text_from_pdf, extract_invoice_data
from utils.search import search_price_list
from utils.logger import logger, log_with_context, log_api_request
from utils.excel_template import ensure_template_exists
from utils.invoice_excel_parser import parse_invoice_excel, update_price_list_from_invoice
from utils.product_management import approve_price_update, reject_price_update
from utils.quotation_parser import parse_quotation_file
from utils.db_utils import with_db_reconnect, test_db_connection
from utils.pdf_generator import generate_quotation_pdf, generate_supplier_pdf_report, generate_supplier_products_pdf, generate_supplier_catalog_pdf
from utils.enhanced_pdf_generator import generate_enhanced_pdf
from utils.feedback_collector import get_feedback_collector
from utils.supplier_duplicate_detector import find_supplier_duplicates, ask_openai_for_resolution, flag_duplicate_products
from utils.bulk_excel_export import generate_bulk_quotation_excel

# Helper function to get recent activities 
def get_recent_activities(limit=5):
    """
    Get a list of recent activities from various sources.
    
    Args:
        limit (int): Maximum number of activities to return
        
    Returns:
        list: List of activity dictionaries with timestamp and message
    """
    activities = []
    
    try:
        # Add recent file uploads
        try:
            uploads = FileUpload.query.order_by(FileUpload.upload_date.desc()).limit(limit).all()
            for upload in uploads:
                try:
                    timestamp = upload.upload_date
                    file_type = upload.file_type.capitalize() if upload.file_type else "File"
                    customer_name = "N/A"
                    
                    # Safely try to get customer name
                    if upload.customer_id:
                        try:
                            customer = Customer.query.get(upload.customer_id)
                            if customer:
                                customer_name = customer.name
                        except Exception as e:
                            logger.error(f"Error getting customer for activity log: {str(e)}")
                    
                    activities.append({
                        'timestamp': timestamp,
                        'message': f"{file_type} upload: {upload.filename} for {customer_name}",
                        'type': 'upload',
                        'icon': 'fas fa-upload'
                    })
                except Exception as e:
                    logger.error(f"Error processing upload for activity log: {str(e)}")
                    continue  # Skip this upload but continue with others
        except Exception as e:
            logger.error(f"Error getting uploads for activity log: {str(e)}")
        
        # Add recent invoices with error handling
        try:
            invoices = Invoice.query.order_by(Invoice.created_at.desc()).limit(limit).all()
            for invoice in invoices:
                try:
                    customer_name = "Unknown Customer"
                    if invoice.customer_id:
                        customer = Customer.query.get(invoice.customer_id)
                        if customer:
                            customer_name = customer.name
                    
                    activities.append({
                        'timestamp': invoice.created_at,
                        'message': f"Invoice {invoice.invoice_number} created for {customer_name}",
                        'type': 'invoice',
                        'icon': 'fas fa-file-invoice'
                    })
                except Exception as e:
                    logger.error(f"Error processing invoice for activity log: {str(e)}")
                    continue  # Skip this invoice but continue with others
        except Exception as e:
            logger.error(f"Error getting invoices for activity log: {str(e)}")
        
        # Add recent price update requests with error handling
        try:
            updates = ProductUpdateRequest.query.order_by(ProductUpdateRequest.created_at.desc()).limit(limit).all()
            for update in updates:
                try:
                    product_name = "Unknown Product"
                    if update.product_id:
                        product = Product.query.get(update.product_id)
                        if product:
                            product_name = product.name
                    
                    status = update.status.capitalize() if update.status else "Unknown"
                    old_price = update.old_price if hasattr(update, 'old_price') else "0.00"
                    new_price = update.new_price if hasattr(update, 'new_price') else "0.00"
                    
                    activities.append({
                        'timestamp': update.created_at,
                        'message': f"Price update for {product_name}: {old_price} → {new_price} ({status})",
                        'type': 'price_update',
                        'icon': 'fas fa-tags'
                    })
                except Exception as e:
                    logger.error(f"Error processing price update for activity log: {str(e)}")
                    continue
        except Exception as e:
            logger.error(f"Error getting price updates for activity log: {str(e)}")
        
        # Add recent quotations with error handling
        try:
            quotations = Quotation.query.order_by(Quotation.created_at.desc()).limit(limit).all()
            for quotation in quotations:
                try:
                    customer_name = "Unknown Customer"
                    if quotation.customer_id:
                        customer = Customer.query.get(quotation.customer_id)
                        if customer:
                            customer_name = customer.name
                            
                    quotation_number = quotation.quotation_number if hasattr(quotation, 'quotation_number') else "Unknown"
                    
                    activities.append({
                        'timestamp': quotation.created_at,
                        'message': f"Quotation {quotation_number} created for {customer_name}",
                        'type': 'quotation',
                        'icon': 'fas fa-file-contract'
                    })
                except Exception as e:
                    logger.error(f"Error processing quotation for activity log: {str(e)}")
                    continue
        except Exception as e:
            logger.error(f"Error getting quotations for activity log: {str(e)}")
    
    except Exception as e:
        # Top-level error handler for activities
        logger.error(f"Error generating activity log: {str(e)}")
        # Return an empty activities list as fallback
        return []
        
    # Sort all activities by timestamp (newest first) and limit the total
    try:
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        return activities[:limit]
    except Exception as e:
        logger.error(f"Error sorting activities: {str(e)}")
        # Return unsorted if there's a sorting error
        return activities[:limit] if activities else []

# Simple redirect for backup testing - will be registered with app in register_routes

# Log that routes module was loaded
logger.info("Routes module loaded")

def register_routes(app):
    
    # Direct access to database backup
    @app.route('/database-backup')
    def database_backup_redirect():
        return redirect(url_for('backup.index'))
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Helper function to check allowed file extensions
    def allowed_file(filename, extensions):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions
        
    # Context processor to add pending update count to all templates
    @app.context_processor
    def inject_pending_update_count():
        try:
            if current_user.is_authenticated:
                pending_count = ProductUpdateRequest.query.filter_by(status='Pending').count()
                return {
                    'pending_update_count': pending_count,
                    'has_pending_updates': pending_count > 0
                }
        except:
            # If there's any error (like with current_user not being available), return defaults
            pass
        return {
            'pending_update_count': 0,
            'has_pending_updates': False
        }
    
    @app.route('/', methods=['GET'])
    def index():
        # If user is already logged in, show the dashboard
        if current_user.is_authenticated:
            import json
            # Get some stats for the dashboard
            pending_update_count = ProductUpdateRequest.query.filter_by(status='Pending').count()
            
            # Get counts for the dashboard
            customer_count = Customer.query.count()
            product_count = Product.query.count()
            price_list_count = PriceList.query.count() 
            invoice_count = Invoice.query.count()
            
            # Build stats dictionary
            stats = {
                'customers': customer_count,
                'products': product_count,
                'price_lists': price_list_count,
                'invoices': invoice_count,
                'pending_updates': pending_update_count
            }
            
            # Dynamic card coloring based on thresholds
            card_classes = {
                'customers': 'bg-primary' if customer_count > 10 else 'bg-warning',
                'products': 'bg-success' if product_count > 20 else 'bg-info',
                'price_lists': 'bg-info' if price_list_count > 5 else 'bg-secondary',
                'invoices': 'bg-warning' if invoice_count > 0 else 'bg-light text-dark'
            }
            
            # Get recent activities for the dashboard
            recent_activities = get_recent_activities(limit=5)
            
            # Get data for charts
            try:
                # Get product categories for pie chart
                product_categories = db.session.query(Product.category, db.func.count(Product.id)).filter(
                    Product.category.isnot(None)
                ).group_by(Product.category).all()
                
                # Convert SQLAlchemy result to Python native types for JSON serialization
                category_labels = []
                category_values = []
                
                for category in product_categories:
                    category_labels.append(str(category[0]) if category[0] else 'Uncategorized')
                    category_values.append(int(category[1]))
                
                # Get invoices per month for past 6 months
                six_months_ago = datetime.utcnow() - timedelta(days=180)
                invoice_counts = db.session.query(
                    db.func.to_char(Invoice.invoice_date, 'YYYY-MM').label('month'), 
                    db.func.count(Invoice.id)
                ).filter(
                    Invoice.invoice_date >= six_months_ago
                ).group_by('month').order_by('month').all()
                
                # Convert SQLAlchemy result to Python native types for JSON serialization
                invoice_labels = []
                invoice_values = []
                
                for count in invoice_counts:
                    invoice_labels.append(str(count[0]))
                    invoice_values.append(int(count[1]))
                
            except Exception as e:
                # Log the error and provide empty chart data if there's an issue
                app.logger.error(f"Error generating chart data in index: {str(e)}")
                category_labels = []
                category_values = []
                invoice_labels = []
                invoice_values = []
            
            # Create chart data objects and convert to JSON with fallback
            try:
                # Create structured data objects for charts
                category_chart_data = {
                    "labels": category_labels,
                    "values": category_values
                }
                invoice_chart_data = {
                    "labels": invoice_labels,
                    "values": invoice_values
                }
                
                # Convert to JSON with safe handling for any type
                category_chart_json = json.dumps(category_chart_data, default=str)
                invoice_chart_json = json.dumps(invoice_chart_data, default=str)
            except Exception as e:
                # If JSON serialization fails, provide empty fallback data
                app.logger.error(f"JSON serialization error in index: {str(e)}")
                category_chart_json = json.dumps({"labels": [], "values": []})
                invoice_chart_json = json.dumps({"labels": [], "values": []})
                
            # Variables for template compatibility
            category_labels_json = category_chart_json
            invoice_labels_json = invoice_chart_json
            
            return render_template('dashboard_improved.html', 
                                  stats=stats,
                                  card_classes=card_classes,
                                  pending_update_count=pending_update_count,
                                  recent_activities=recent_activities,
                                  category_labels_json=category_labels_json,
                                  category_values_json=category_labels_json,  # Using same variable as a fallback
                                  invoice_labels_json=invoice_labels_json,
                                  invoice_values_json=invoice_labels_json)
        # Otherwise show the login page
        return render_template('index.html')
        
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # If user is already logged in, redirect to dashboard
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
            
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            # Validate the username and password
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                # Update last login timestamp
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                # Log the user in
                login_user(user)
                flash(f'Welcome back, {user.username}!', 'success')
                
                # Redirect to the page they were trying to access or the dashboard
                next_page = request.args.get('next')
                return redirect(next_page if next_page else url_for('dashboard'))
            else:
                flash('Invalid username or password. Please try again.', 'danger')
                
        return render_template('index.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out successfully.', 'success')
        return redirect(url_for('index'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        import json
        # Get some stats for the dashboard
        pending_update_count = ProductUpdateRequest.query.filter_by(status='Pending').count()
        
        # Get counts for the dashboard
        customer_count = Customer.query.count()
        product_count = Product.query.count()
        price_list_count = PriceList.query.count() 
        invoice_count = Invoice.query.count()
        
        # Build stats dictionary
        stats = {
            'customers': customer_count,
            'products': product_count,
            'price_lists': price_list_count,
            'invoices': invoice_count,
            'pending_updates': pending_update_count
        }
        
        # Dynamic card coloring based on thresholds
        card_classes = {
            'customers': 'bg-primary' if customer_count > 10 else 'bg-warning',
            'products': 'bg-success' if product_count > 20 else 'bg-info',
            'price_lists': 'bg-info' if price_list_count > 5 else 'bg-secondary',
            'invoices': 'bg-warning' if invoice_count > 0 else 'bg-light text-dark'
        }
        
        # Get recent activities for the dashboard
        recent_activities = get_recent_activities(limit=5)
        
        try:
            # Get data for charts
            # Get product categories for pie chart
            product_categories = db.session.query(Product.category, db.func.count(Product.id)).filter(
                Product.category.isnot(None)
            ).group_by(Product.category).all()
            
            # Convert SQLAlchemy result to Python native types for JSON serialization
            category_labels = []
            category_values = []
            
            for category in product_categories:
                category_labels.append(str(category[0]) if category[0] else 'Uncategorized')
                category_values.append(int(category[1]))
            
            # Get invoices per month for past 6 months
            six_months_ago = datetime.utcnow() - timedelta(days=180)
            invoice_counts = db.session.query(
                db.func.to_char(Invoice.invoice_date, 'YYYY-MM').label('month'), 
                db.func.count(Invoice.id)
            ).filter(
                Invoice.invoice_date >= six_months_ago
            ).group_by('month').order_by('month').all()
            
            # Convert SQLAlchemy result to Python native types for JSON serialization
            invoice_labels = []
            invoice_values = []
            
            for count in invoice_counts:
                invoice_labels.append(str(count[0]))
                invoice_values.append(int(count[1]))
            
        except Exception as e:
            # Log the error and provide empty chart data if there's an issue
            app.logger.error(f"Error generating chart data: {str(e)}")
            category_labels = []
            category_values = []
            invoice_labels = []
            invoice_values = []
        
        # Create chart data objects and convert to JSON with fallback
        try:
            # Create structured data objects for charts
            category_chart_data = {
                "labels": category_labels,
                "values": category_values
            }
            invoice_chart_data = {
                "labels": invoice_labels,
                "values": invoice_values
            }
            
            # Convert to JSON with safe handling for any type
            category_chart_json = json.dumps(category_chart_data, default=str)
            invoice_chart_json = json.dumps(invoice_chart_data, default=str)
        except Exception as e:
            # If JSON serialization fails, provide empty fallback data
            app.logger.error(f"JSON serialization error: {str(e)}")
            category_chart_json = json.dumps({"labels": [], "values": []})
            invoice_chart_json = json.dumps({"labels": [], "values": []})
        
        # Variables were renamed
        category_labels_json = category_chart_json
        invoice_labels_json = invoice_chart_json
        
        return render_template('dashboard_improved.html', 
                              stats=stats,
                              card_classes=card_classes,
                              pending_update_count=pending_update_count,
                              recent_activities=recent_activities,
                              category_labels_json=category_labels_json,
                              category_values_json=category_labels_json,  # Using same variable as a fallback
                              invoice_labels_json=invoice_labels_json,
                              invoice_values_json=invoice_labels_json)
    
    @app.route('/uploads', methods=['GET'])
    @login_required
    def uploads():
        customers = Customer.query.all()
        recent_uploads = FileUpload.query.order_by(FileUpload.upload_date.desc()).limit(10).all()
        return render_template('uploads.html', customers=customers, recent_uploads=recent_uploads)
    
    @app.route('/upload/excel', methods=['POST'])
    @login_required
    def upload_excel():
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        customer_id = request.form.get('customer_id')
        
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        
        if not customer_id:
            flash('Please select a customer', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename, {'xlsx', 'xls'}):
            # Generate unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Create file upload record
            upload = FileUpload(
                filename=filename,
                file_type='excel',
                customer_id=customer_id,
                processed=False
            )
            db.session.add(upload)
            db.session.commit()
            
            try:
                # Log before processing with detailed info
                logger.info(f"Starting Excel processing for file: {filename}, customer_id: {customer_id}")
                logger.info(f"File size: {os.path.getsize(file_path)} bytes")
                logger.info(f"Upload ID: {upload.id}")
                
                # Add extra debugging for file content
                try:
                    import pandas as pd
                    logger.info(f"Attempting to read first few rows of the Excel file for debugging")
                    sample_df = pd.read_excel(file_path, engine='openpyxl', nrows=5)
                    logger.info(f"Sample Excel data headers: {sample_df.columns.tolist()}")
                    logger.info(f"Sample Excel data types: {sample_df.dtypes.to_dict()}")
                except Exception as sample_error:
                    logger.warning(f"Failed to read sample data: {str(sample_error)}")
                
                try:
                    # Process the excel file with extra error handling
                    result = parse_excel_file(file_path, customer_id, upload.id)
                    
                    # Handle errors from the parser
                    if result.get('errors') and len(result['errors']) > 0:
                        error_messages = '; '.join(result['errors'])
                        logger.error(f"Excel processing completed with errors: {error_messages}")
                        upload.processing_notes = f"Processed with errors: {error_messages}"
                        upload.processed = True
                        db.session.commit()
                        flash(f'File processed with errors: {error_messages}', 'warning')
                    else:
                        # Update upload record for success
                        logger.info(f"Excel processing successful: {result}")
                        upload.processed = True
                        upload.processing_notes = f"Successfully processed. Added {result['new_products']} products and {result['price_entries']} price list entries."
                        db.session.commit()
                        
                        flash(f'Successfully uploaded and processed: {filename}. Added {result["new_products"]} products and {result["price_entries"]} price list entries.', 'success')
                except UnicodeError as ue:
                    # Specifically catch encoding issues
                    error_msg = f"Character encoding error: {str(ue)}. The file may contain special characters that need preprocessing."
                    logger.error(f"Unicode error: {error_msg}")
                    logger.error(f"Unicode error traceback: {traceback.format_exc()}")
                    upload.processing_notes = error_msg
                    db.session.commit()
                    flash(error_msg, 'danger')
            except Exception as e:
                error_msg = f"Error processing file: {str(e)}"
                logger.error("=== Excel Upload Error ===")
                logger.error(f"File: {filename}")
                logger.error(f"Customer ID: {customer_id}")
                logger.error(f"Upload ID: {upload.id}")
                logger.error(f"Error: {error_msg}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                logger.error("========================")
                
                upload.processing_notes = error_msg
                db.session.commit()
                flash("Error uploading file. Please check if the Excel file follows the expected format.", 'danger')
            
            return redirect(url_for('uploads'))
        
        flash('Invalid file type. Please upload Excel files only (.xlsx, .xls)', 'danger')
        return redirect(request.url)
    
    @app.route('/upload/pdf', methods=['POST'])
    @login_required
    def upload_pdf():
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        customer_id = request.form.get('customer_id')
        
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        
        if not customer_id:
            flash('Please select a customer', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename, {'pdf'}):
            # Generate unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Create file upload record
            upload = FileUpload(
                filename=filename,
                file_type='pdf',
                customer_id=customer_id,
                processed=False
            )
            db.session.add(upload)
            db.session.commit()
            
            try:
                # Extract text from PDF
                pdf_text = extract_text_from_pdf(file_path)
                
                # Extract invoice data from the text
                invoice_data = extract_invoice_data(pdf_text)
                
                # Create invoice record
                invoice = Invoice(
                    customer_id=customer_id,
                    invoice_number=invoice_data.get('invoice_number', f'AUTO-{uuid.uuid4().hex[:8]}'),
                    invoice_date=datetime.strptime(invoice_data.get('invoice_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d'),
                    total_amount=invoice_data.get('total_amount', 0),
                    currency=invoice_data.get('currency', '€'),
                    file_path=unique_filename
                )
                db.session.add(invoice)
                db.session.commit()
                
                # Track price list updates
                price_list_updates = {
                    'new': 0,
                    'pending': 0
                }
                
                # Add invoice items
                for item in invoice_data.get('items', []):
                    # Use the enhanced product verification system
                    from utils.product_verification import verify_product_exists
                    
                    # Create product data dictionary from the invoice item
                    product_data = {
                        'name': item['description'],
                        'scientific_name': item.get('scientific_name'),
                        'pot': item.get('pot_size'),
                        'description': f"{item.get('scientific_name', '')} {item.get('pot_size', '')}".strip() or None
                    }
                    
                    # Use the enhanced verification system that tries multiple strategies
                    product, message, is_new, was_created = verify_product_exists(
                        product_data, 
                        create_if_missing=True  # Create if not found
                    )
                    logger.info(f"Product from invoice: {message}")
                    
                    invoice_item = InvoiceItem(
                        invoice_id=invoice.id,
                        product_id=product.id if product else None,
                        description=item['description'],
                        scientific_name=item.get('scientific_name'),
                        pot_size=item.get('pot_size'),
                        quantity=item.get('quantity', 1),
                        price=item.get('price', 0),
                        vat=item.get('vat', 0),
                        vat_percentage=item.get('vat_percentage'),
                        total=item.get('total', 0)
                    )
                    db.session.add(invoice_item)
                    
                    # Create or update price list entry if we have a product and price
                    if product and item.get('price', 0) > 0:
                        from utils.product_management import create_or_update_price_list
                        price_list, message, is_new = create_or_update_price_list(
                            customer_id=customer_id,
                            product_id=product.id,
                            new_price=item['price'],
                            source_file=f"Invoice #{invoice.invoice_number}"
                        )
                        logger.info(f"Price list from invoice: {message}")
                        
                        # Track updates
                        if is_new:
                            price_list_updates['new'] += 1
                        elif "pending approval" in message:
                            price_list_updates['pending'] += 1
                
                # Update upload record
                # Update processing notes to include price list updates
                price_list_info = ""
                if price_list_updates['new'] > 0 or price_list_updates['pending'] > 0:
                    price_list_info = f" Also "
                    if price_list_updates['new'] > 0:
                        price_list_info += f"created {price_list_updates['new']} new price list entries"
                    
                    if price_list_updates['new'] > 0 and price_list_updates['pending'] > 0:
                        price_list_info += f" and "
                        
                    if price_list_updates['pending'] > 0:
                        price_list_info += f"added {price_list_updates['pending']} pending price updates"
                    price_list_info += "."
                
                upload.processed = True
                upload.processing_notes = f"Successfully processed. Created invoice #{invoice.invoice_number} with {len(invoice_data.get('items', []))} items.{price_list_info}"
                db.session.commit()
                
                success_message = f'Successfully uploaded and processed: {filename}. Created invoice #{invoice.invoice_number}.'
                
                # Add price list information to the success message
                if price_list_updates['new'] > 0:
                    success_message += f' Created {price_list_updates["new"]} new price list entries.'
                
                if price_list_updates['pending'] > 0:
                    success_message += f' Added {price_list_updates["pending"]} pending price updates that require approval.'
                
                success_message += f' You can view the invoice on the <a href="{url_for("invoices")}">Invoices page</a>'
                
                if price_list_updates['new'] > 0 or price_list_updates['pending'] > 0:
                    success_message += f' and check the price lists on the <a href="{url_for("price_lists")}?customer_id={customer_id}">Price Lists page</a>'
                
                if price_list_updates['pending'] > 0:
                    success_message += f' or review the pending updates on the <a href="{url_for("pending_updates")}">Price Updates page</a>'
                
                success_message += '.'
                
                flash(success_message, 'success')
            except Exception as e:
                upload.processing_notes = f"Error processing file: {str(e)}"
                db.session.commit()
                flash(f'Error processing file: {str(e)}', 'danger')
            
            return redirect(url_for('uploads'))
        
        flash('Invalid file type. Please upload PDF files only.', 'danger')
        return redirect(request.url)
    
    @app.route('/upload/customer-invoice', methods=['POST'])
    @login_required
    def upload_customer_invoice():
        """
        Upload customer invoice Excel file with specific structure and update price lists
        - Customer name on line 11 (columns J-AE)
        - From line 16 onwards:
            - Scientific name in merged columns E-L
            - Description in merged columns M-S
            - Quantity in merged columns T-W
            - Price in merged columns X-Z
            - VAT type in merged columns AA-AD (5% or 19%)
            - Total excluding VAT in column AE
        """
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(url_for('uploads'))
        
        file = request.files['file']
        customer_id = request.form.get('customer_id')
        
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('uploads'))
            
        # Check if file is an Excel file
        if not allowed_file(file.filename, {'xlsx', 'xls'}):
            flash('Invalid file type. Please upload Excel files only (.xlsx, .xls)', 'danger')
            return redirect(url_for('uploads'))
            
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Create file upload record
        upload = FileUpload(
            filename=filename,
            file_type='customer_invoice',
            customer_id=customer_id,
            processed=False
        )
        db.session.add(upload)
        db.session.commit()
        
        try:
            # Log before processing
            logger.info(f"Starting customer invoice Excel processing for file: {filename}")
            
            # Parse the invoice Excel file
            invoice_data = parse_invoice_excel(file_path, customer_id)
            
            # If customer wasn't provided but was found in the file
            if not customer_id and invoice_data.get('customer_id'):
                customer_id = invoice_data['customer_id']
                upload.customer_id = customer_id
                db.session.commit()
                
            # Update price lists based on the invoice data
            if invoice_data and invoice_data.get('products'):
                update_result = update_price_list_from_invoice(invoice_data)
                
                # Update the upload record
                upload.processed = True
                upload.processing_notes = (
                    f"Successfully processed. Updated {update_result['updated_count']} "
                    f"existing prices and added {update_result['new_count']} new price list entries."
                )
                db.session.commit()
                
                flash(
                    f'Successfully processed customer invoice: {filename}. '
                    f'Updated {update_result["updated_count"]} existing prices and '
                    f'added {update_result["new_count"]} new price list entries.',
                    'success'
                )
            else:
                flash('No product data found in the invoice file.', 'warning')
                upload.processed = True
                upload.processing_notes = "No product data found in the invoice file."
                db.session.commit()
                
        except Exception as e:
            error_msg = f"Error processing customer invoice: {str(e)}"
            logger.error(f"Customer invoice Excel processing error: {error_msg}")
            logger.error(traceback.format_exc())
            
            upload.processed = True
            upload.processing_notes = error_msg
            db.session.commit()
            
            flash(f'Error processing customer invoice: {str(e)}', 'danger')
            
        return redirect(url_for('uploads'))
                
    @app.route('/download-customer-invoice-template')
    @login_required
    def download_customer_invoice_template():
        """Download a sample customer invoice template for reference"""
        return send_from_directory(
            directory=app.config['TEMPLATES_FOLDER'],
            path='customer_invoice_template.xlsx',
            as_attachment=True,
            download_name='Customer_Invoice_Template.xlsx'
        )
        
    @app.route('/customers', methods=['GET', 'POST'])
    @login_required
    def customers():
        if request.method == 'POST':
            # Add or update a customer
            customer_id = request.form.get('customer_id')
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')
            category_id = request.form.get('category_id')
            
            # Validate email if provided
            from utils.validation import is_valid_email, sanitize_input
            
            if email and not is_valid_email(email):
                flash('Invalid email address format. Please check and try again.', 'danger')
                customers = Customer.query.all()
                categories = CustomerCategory.query.all()
                return render_template('customers.html', customers=customers, categories=categories)
            
            if customer_id:  # Update existing
                customer = Customer.query.get_or_404(customer_id)
                customer.name = name
                customer.email = email
                customer.phone = phone
                customer.address = address
                if category_id:
                    customer.category_id = category_id
                flash(f'Customer {name} updated successfully!', 'success')
            else:  # Create new
                customer = Customer(name=name, email=email, phone=phone, address=address, category_id=category_id if category_id else None)
                db.session.add(customer)
                flash(f'Customer {name} added successfully!', 'success')
            
            db.session.commit()
            return redirect(url_for('customers'))
        
        # GET request - show customers
        customers_list = Customer.query.all()
        categories = CustomerCategory.query.all()
        return render_template('customers.html', customers=customers_list, categories=categories)
    
    @app.route('/customers/<int:customer_id>', methods=['GET'])
    @login_required
    def customer_detail(customer_id):
        """Show customer details including stats and contact history"""
        customer = Customer.query.get_or_404(customer_id)
        
        # Get customer statistics
        from utils.customer_stats import get_customer_stats
        stats = get_customer_stats(customer_id)
        
        # Get customer contacts
        contacts = customer.contacts
        
        # Get price lists for this customer
        price_lists = PriceList.query.filter_by(customer_id=customer_id).all()
        
        # Get invoices for this customer
        invoices = Invoice.query.filter_by(customer_id=customer_id).all()
        
        # Get all available categories for the contact form
        categories = CustomerCategory.query.all()
        
        return render_template('customer_detail.html', 
                               customer=customer, 
                               stats=stats, 
                               contacts=contacts,
                               price_lists=price_lists,
                               invoices=invoices,
                               categories=categories)
                               
    @app.route('/customers/<int:customer_id>/add_contact', methods=['POST'])
    @login_required
    def add_customer_contact(customer_id):
        """Add a new contact record for a customer"""
        customer = Customer.query.get_or_404(customer_id)
        
        contact_type = request.form.get('contact_type')
        notes = request.form.get('notes')
        contact_date = request.form.get('contact_date')
        
        if not contact_type or not notes:
            flash('Contact type and notes are required.', 'danger')
            return redirect(url_for('customer_detail', customer_id=customer_id))
            
        try:
            # Create a new contact record
            if contact_date:
                contact_date = datetime.strptime(contact_date, '%Y-%m-%d')
            else:
                contact_date = datetime.utcnow()
                
            contact = CustomerContact(
                customer_id=customer_id,
                contact_type=contact_type,
                notes=notes,
                contact_date=contact_date
            )
            
            db.session.add(contact)
            db.session.commit()
            
            flash('Customer contact record added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding contact record: {str(e)}', 'danger')
            
        return redirect(url_for('customer_detail', customer_id=customer_id))
        
    @app.route('/customers/<int:customer_id>/delete_contact/<int:contact_id>', methods=['POST'])
    @login_required
    def delete_customer_contact(customer_id, contact_id):
        """Delete a customer contact record"""
        contact = CustomerContact.query.get_or_404(contact_id)
        
        # Verify the contact belongs to the specified customer
        if contact.customer_id != customer_id:
            flash('Invalid contact record.', 'danger')
            return redirect(url_for('customer_detail', customer_id=customer_id))
            
        try:
            db.session.delete(contact)
            db.session.commit()
            flash('Contact record deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting contact record: {str(e)}', 'danger')
            
        return redirect(url_for('customer_detail', customer_id=customer_id))
    
    @app.route('/customers/<int:customer_id>/delete', methods=['POST'])
    @login_required
    def delete_customer(customer_id):
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        flash(f'Customer {customer.name} deleted successfully!', 'success')
        return redirect(url_for('customers'))
    
    @app.route('/customer_categories', methods=['GET', 'POST'])
    @login_required
    def customer_categories():
        """View and manage customer categories"""
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description', '')
            category_id = request.form.get('category_id')
            
            if not name:
                flash('Category name is required.', 'danger')
                categories = CustomerCategory.query.all()
                return render_template('customer_categories.html', categories=categories)
                
            if category_id:  # Update existing category
                category = CustomerCategory.query.get_or_404(category_id)
                category.name = name
                category.description = description
                flash(f'Category {name} updated successfully!', 'success')
            else:  # Create new category
                category = CustomerCategory(name=name, description=description)
                db.session.add(category)
                flash(f'Category {name} added successfully!', 'success')
                
            db.session.commit()
            return redirect(url_for('customer_categories'))
            
        # GET request - show categories
        categories = CustomerCategory.query.all()
        return render_template('customer_categories.html', categories=categories)
        
    @app.route('/customer_categories/<int:category_id>/delete', methods=['POST'])
    @login_required
    def delete_customer_category(category_id):
        """Delete a customer category"""
        category = CustomerCategory.query.get_or_404(category_id)
        
        # Check if any customers use this category
        customers_count = Customer.query.filter_by(category_id=category_id).count()
        if customers_count > 0:
            flash(f'Cannot delete category {category.name} as it is used by {customers_count} customers.', 'danger')
            return redirect(url_for('customer_categories'))
            
        try:
            category_name = category.name
            db.session.delete(category)
            db.session.commit()
            flash(f'Category {category_name} deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting category: {str(e)}', 'danger')
            
        return redirect(url_for('customer_categories'))
    
    @app.route('/products', methods=['GET', 'POST'])
    @login_required
    def products():
        if request.method == 'POST':
            # Add or update a product
            product_id = request.form.get('product_id')
            name = request.form.get('name')
            category = request.form.get('category')
            scientific_name = request.form.get('scientific_name')
            pot = request.form.get('pot')
            sku = request.form.get('sku')
            description = request.form.get('description')
            
            if product_id:  # Update existing
                product = Product.query.get_or_404(product_id)
                product.name = name
                product.category = category
                product.scientific_name = scientific_name
                product.pot = pot
                product.sku = sku
                product.description = description
                flash(f'Product {name} updated successfully!', 'success')
            else:  # Create new
                product = Product(
                    name=name, 
                    category=category,
                    scientific_name=scientific_name,
                    pot=pot,
                    sku=sku, 
                    description=description
                )
                db.session.add(product)
                flash(f'Product {name} added successfully!', 'success')
            
            db.session.commit()
            return redirect(url_for('products'))
        
        # GET request - show products
        products_list = Product.query.all()
        return render_template('products.html', products=products_list)
    
    @app.route('/products/<int:product_id>/delete', methods=['POST'])
    @login_required
    def delete_product(product_id):
        product = Product.query.get_or_404(product_id)
        product_name = product.name
        redirect_to = request.form.get('redirect_to', 'products')
        customer_id = request.form.get('customer_id', '')
        category = request.form.get('category', '')
        
        # Delete associated price list entries first
        PriceList.query.filter_by(product_id=product_id).delete()
        # Then delete the product
        db.session.delete(product)
        db.session.commit()
        flash(f'Product "{product_name}" deleted successfully!', 'success')
        
        # Redirect based on where the request came from
        if redirect_to == 'price_lists':
            return redirect(url_for('price_lists', customer_id=customer_id, category=category))
        else:
            return redirect(url_for('products'))

    @app.route('/products/batch-delete', methods=['POST'])
    @login_required
    def batch_delete_products():
        data = request.get_json()
        product_ids = data.get('product_ids', [])
        
        if not product_ids:
            return jsonify({'error': 'No products selected'}), 400
            
        try:
            # Delete associated price list entries first
            PriceList.query.filter(PriceList.product_id.in_(product_ids)).delete(synchronize_session=False)
            # Then delete the products
            Product.query.filter(Product.id.in_(product_ids)).delete(synchronize_session=False)
            db.session.commit()
            flash(f'{len(product_ids)} products deleted successfully!', 'success')
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/search', methods=['GET'])
    @login_required
    def search():
        customers = Customer.query.all()
        return render_template('search.html', customers=customers)
    
    @app.route('/api/search', methods=['GET'])
    @login_required
    def api_search():
        query = request.args.get('q', '')
        customer_id = request.args.get('customer_id', '')
        
        if not query:
            return jsonify({'error': 'No search query provided'}), 400
        
        if not customer_id:
            return jsonify({'error': 'No customer selected'}), 400
        
        results = search_price_list(query, customer_id)
        return jsonify(results)
    
    @app.route('/api/categories', methods=['GET'])
    @login_required
    def get_categories():
        """API endpoint to get all customer categories"""
        try:
            categories = CustomerCategory.query.order_by(CustomerCategory.name).all()
            
            # Format categories as JSON
            categories_list = [{
                'id': c.id,
                'name': c.name,
                'description': c.description,
                'customer_count': Customer.query.filter_by(category_id=c.id).count()
            } for c in categories]
            
            return jsonify(categories_list)
        except Exception as e:
            logger.error(f"Error in API categories endpoint: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/customers/search', methods=['GET'])
    @login_required
    def search_customers():
        """API endpoint for searching customers by name, email or phone"""
        query = request.args.get('q', '')
        category_id = request.args.get('category_id')
        
        if len(query) < 2 and not category_id:
            return jsonify([])
            
        # Build the filter conditions
        filter_conditions = []
        
        if query:
            filter_conditions.append(
                db.or_(
                    Customer.name.ilike(f'%{query}%'),
                    Customer.email.ilike(f'%{query}%'),
                    Customer.phone.ilike(f'%{query}%')
                )
            )
        
        if category_id:
            try:
                category_id = int(category_id)
                filter_conditions.append(Customer.category_id == category_id)
            except (ValueError, TypeError):
                # If category_id is not a valid integer, ignore it
                logger.warning(f"Invalid category_id provided: {category_id}")
                pass
        
        # Apply filters
        if filter_conditions:
            query_obj = Customer.query.filter(db.and_(*filter_conditions))
        else:
            query_obj = Customer.query
            
        # Order by name and limit results
        customers = query_obj.order_by(Customer.name).limit(50).all()
        
        # Get customer categories for display
        categories = {}
        for category in CustomerCategory.query.all():
            categories[category.id] = category.name
            
        # Format results with additional information
        results = []
        for c in customers:
            # Count related data
            invoice_count = len(c.invoices)
            price_list_count = len(c.price_lists)
            contact_count = len(c.contacts)
            
            # Calculate last order date
            last_order_date = None
            if c.invoices:
                invoice_dates = [i.invoice_date for i in c.invoices if i.invoice_date]
                if invoice_dates:
                    last_order_date = max(invoice_dates)
            
            # Calculate last contact date
            last_contact_date = None
            if c.contacts:
                contact_dates = [co.contact_date for co in c.contacts if co.contact_date]
                if contact_dates:
                    last_contact_date = max(contact_dates)
            
            result = {
                'id': c.id,
                'name': c.name,
                'email': c.email or '',
                'phone': c.phone or '',
                'category': categories.get(c.category_id, 'Uncategorized'),
                'category_id': c.category_id,
                'address': c.address or '',
                'created_at': c.created_at.strftime('%Y-%m-%d') if c.created_at else '',
                'invoice_count': invoice_count,
                'price_list_count': price_list_count,
                'contact_count': contact_count,
                'last_order_date': last_order_date.strftime('%Y-%m-%d') if last_order_date else None,
                'last_contact_date': last_contact_date.strftime('%Y-%m-%d %H:%M') if last_contact_date else None,
            }
            
            # Validate email if present
            if c.email:
                from utils.validation import is_valid_email
                result['email_valid'] = is_valid_email(c.email)
            else:
                result['email_valid'] = None
                
            results.append(result)
        
        return jsonify(results)
    
    @app.route('/download/template')
    @login_required
    def download_template():
        """Provide a downloadable Excel template for price lists or quotations"""
        templates_dict = ensure_template_exists(app.static_folder)
        template_type = request.args.get('type', 'price_list')
        
        if template_type == 'quotation':
            template_path = templates_dict['quotation']
            download_name = "quotation_template.xlsx"
        else:
            template_path = templates_dict['price_list']
            download_name = "price_list_template.xlsx"
            
        template_dir = os.path.dirname(template_path)
        template_file = os.path.basename(template_path)
            
        return send_from_directory(template_dir, template_file, 
                                 as_attachment=True, download_name=download_name)
    
    @app.route('/price-lists')
    @login_required
    def price_lists():
        """View all price lists with filtering options"""
        # Get query parameters
        customer_id = request.args.get('customer_id', '')
        category = request.args.get('category', '')
        page = request.args.get('page', 1, type=int)
        per_page = 20  # Items per page
        
        # Base query
        query = PriceList.query.join(Product)
        
        # Apply filters
        if customer_id:
            query = query.filter(PriceList.customer_id == customer_id)
        if category:
            query = query.filter(Product.category == category)
            
        # Order by customer name and product name
        query = query.order_by(PriceList.customer_id, Product.category, Product.name)
        
        # Paginate results
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        price_lists = pagination.items
        
        # Get all customers for filter dropdown
        customers = Customer.query.all()
        
        # Get all existing products for add product form
        products = []
        if customer_id:
            # Get products that aren't already in this customer's price list
            subquery = db.session.query(PriceList.product_id).filter(PriceList.customer_id == customer_id).subquery()
            products = Product.query.filter(~Product.id.in_(subquery)).order_by(Product.name).all()
        
        # Get all unique categories for filter dropdown
        categories = db.session.query(Product.category).filter(Product.category != None, Product.category != '').distinct().order_by(Product.category).all()
        categories = [c[0] for c in categories]  # Extract the category names
        
        return render_template('price_lists.html', 
                              price_lists=price_lists, 
                              customers=customers,
                              categories=categories,
                              products=products,
                              pagination=pagination,
                              selected_customer_id=customer_id,
                              selected_category=category)
    
    @app.route('/edit-product', methods=['POST'])
    @login_required
    def edit_product():
        """Edit product details from any page"""
        product_id = request.form.get('product_id')
        redirect_to = request.form.get('redirect_to', 'products')
        
        if not product_id:
            flash('Product ID is required.', 'danger')
            return redirect(url_for(redirect_to))
            
        try:
            product = Product.query.get_or_404(product_id)
            product.name = request.form.get('name')
            
            # Handle 'None' string values properly
            category = request.form.get('product_category')
            if category == 'None' or not category:
                category = None
            product.category = category
                
            scientific_name = request.form.get('scientific_name')
            if scientific_name == 'None' or not scientific_name:
                scientific_name = None
            product.scientific_name = scientific_name
                
            pot = request.form.get('pot')
            if pot == 'None' or not pot:
                pot = None
            product.pot = pot
                
            # Special handling for SKU (unique constraint)
            sku = request.form.get('sku')
            if sku == 'None' or not sku or sku.strip() == '':
                # Set to None explicitly if empty or 'None'
                product.sku = None
            else:
                # Check if this SKU already exists on another product
                existing_product = Product.query.filter(Product.sku == sku, Product.id != product.id).first()
                if existing_product:
                    raise ValueError(f"SKU '{sku}' already exists on product '{existing_product.name}'. SKUs must be unique.")
                product.sku = sku.strip()
                
            description = request.form.get('description')
            if description == 'None' or not description:
                description = None
            product.description = description
            
            db.session.commit()
            flash(f'Product "{product.name}" updated successfully!', 'success')
        except ValueError as e:
            db.session.rollback()
            logger.error(f"Validation error updating product {product_id}: {str(e)}")
            flash(f'Error: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating product {product_id}: {str(e)}")
            flash(f'An error occurred while updating the product: {str(e)}', 'danger')
        
        # Handle redirection with query parameters
        if redirect_to == 'price_lists':
            customer_id = request.form.get('customer_id')
            category = request.form.get('category')
            return redirect(url_for('price_lists', customer_id=customer_id, category=category))
        else:
            return redirect(url_for(redirect_to))
    
    @app.route('/add-to-price-list', methods=['POST'])
    @login_required
    def add_to_price_list():
        """Add a product to a customer's price list"""
        product_id = request.form.get('product_id')
        customer_id = request.form.get('customer_id')
        price = request.form.get('price')
        
        if not product_id or not customer_id or not price:
            flash('Missing required information. Product, customer, and price are required.', 'danger')
            return redirect(url_for('price_lists', customer_id=customer_id))
        
        try:
            # Convert price to float
            price = float(price)
            
            # Check if product and customer exist
            product = Product.query.get_or_404(product_id)
            customer = Customer.query.get_or_404(customer_id)
            
            # Check if this price list entry already exists
            existing = PriceList.query.filter_by(
                product_id=product_id, 
                customer_id=customer_id
            ).first()
            
            if existing:
                flash(f'Price list entry for {product.name} already exists for this customer.', 'warning')
                return redirect(url_for('price_lists', customer_id=customer_id))
            
            # Create new price list entry
            price_list = PriceList(
                product_id=product_id,
                customer_id=customer_id,
                price=price,
                effective_date=datetime.now().date(),
                source_file='manual_addition'
            )
            
            db.session.add(price_list)
            db.session.commit()
            
            flash(f'Product "{product.name}" added to price list with price {price}€.', 'success')
            
        except ValueError:
            flash('Invalid price. Please enter a valid number.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding product to price list: {str(e)}', 'danger')
            logger.error(f"Error adding product {product_id} to price list: {str(e)}")
        
        return redirect(url_for('price_lists', customer_id=customer_id))

    @app.route('/price-list/<int:price_id>/delete', methods=['POST'])
    @login_required
    def delete_price_list_entry(price_id):
        """Delete a single price list entry"""
        price_list = PriceList.query.get_or_404(price_id)
        customer_id = price_list.customer_id
        product_name = price_list.product.name if price_list.product else "Unknown product"
        
        # Store information before deleting
        customer_name = Customer.query.get(customer_id).name if customer_id else "Unknown customer"
        
        try:
            # Delete just this price list entry
            db.session.delete(price_list)
            db.session.commit()
            flash(f'Price list entry for "{product_name}" for customer "{customer_name}" deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting price list entry {price_id}: {str(e)}")
            flash(f'Error deleting price list entry: {str(e)}', 'danger')
        
        # Redirect back to price lists page with the same filter
        category = request.form.get('category', '')
        return redirect(url_for('price_lists', customer_id=customer_id, category=category))
        
    @app.route('/price-lists/batch-delete', methods=['POST'])
    @login_required
    def batch_delete_price_lists():
        """Delete multiple price list entries at once"""
        data = request.get_json()
        price_ids = data.get('price_ids', [])
        
        if not price_ids:
            return jsonify({'error': 'No price list entries selected'}), 400
            
        try:
            # Get info before deleting for the success message
            prices_info = []
            for price_id in price_ids:
                price = PriceList.query.get(price_id)
                if price:
                    product_name = price.product.name if price.product else "Unknown product"
                    customer_name = price.customer.name if price.customer else "Unknown customer"
                    prices_info.append(f"{product_name} for {customer_name}")
            
            # Delete the selected price list entries
            PriceList.query.filter(PriceList.id.in_(price_ids)).delete(synchronize_session=False)
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'message': f'{len(price_ids)} price list entries deleted successfully'
            })
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error in batch delete price lists: {str(e)}")
            return jsonify({'error': str(e)}), 500
            
    @app.route('/edit-price', methods=['POST'])
    @login_required
    def edit_price():
        """Edit price in a price list"""
        price_id = request.form.get('price_id')
        product_id = request.form.get('product_id')
        customer_id = request.form.get('customer_id')
        new_price = float(request.form.get('price', 0))
        immediate_update = request.form.get('immediate_update') == '1'
        
        if not price_id or not product_id or not customer_id:
            flash('Missing required information.', 'danger')
            return redirect(url_for('price_lists'))
        
        price_list = PriceList.query.get_or_404(price_id)
        old_price = price_list.price
        
        if immediate_update:
            # Apply the change directly
            price_list.price = new_price
            db.session.commit()
            flash(f'Price updated successfully from {old_price}€ to {new_price}€.', 'success')
        else:
            # Create a price update request
            update_request = ProductUpdateRequest(
                product_id=product_id,
                price_list_id=price_id,
                old_price=old_price,
                new_price=new_price,
                status='Pending',
                source_file=f'manual_edit&customer_id={customer_id}'
            )
            db.session.add(update_request)
            db.session.commit()
            flash(f'Price update request created. Current price: {old_price}€, Requested price: {new_price}€. This change requires approval.', 'info')
        
        return redirect(url_for('price_lists', customer_id=customer_id))
                              
    @app.route('/invoices')
    @login_required
    def invoices():
        """View all invoices with filtering options"""
        # Get query parameters
        customer_id = request.args.get('customer_id', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        page = request.args.get('page', 1, type=int)
        per_page = 20  # Items per page
        
        # Base query
        query = Invoice.query
        
        # Apply filters
        if customer_id:
            query = query.filter(Invoice.customer_id == customer_id)
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                query = query.filter(Invoice.invoice_date >= date_from_obj)
            except ValueError:
                pass
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                query = query.filter(Invoice.invoice_date <= date_to_obj)
            except ValueError:
                pass
            
        # Order by invoice date (newest first)
        query = query.order_by(Invoice.invoice_date.desc())
        
        # Paginate results
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        invoices_list = pagination.items
        
        # Get all customers for filter dropdown
        customers = Customer.query.all()
        
        return render_template('invoices.html', 
                              invoices=invoices_list, 
                              customers=customers,
                              pagination=pagination,
                              selected_customer_id=customer_id,
                              date_from=date_from,
                              date_to=date_to)
                              
    @app.route('/invoice/<int:invoice_id>')
    @login_required
    def invoice_details(invoice_id):
        """View details of a specific invoice"""
        invoice = Invoice.query.get_or_404(invoice_id)
        
        # Get associated customer
        customer = Customer.query.get(invoice.customer_id)
        
        # Get all invoice items with products
        items = InvoiceItem.query.filter_by(invoice_id=invoice_id).all()
        
        return render_template('invoice_details.html',
                              invoice=invoice,
                              customer=customer,
                              items=items)
                              
    @app.route('/invoice/<int:invoice_id>/delete', methods=['POST'])
    @login_required
    def delete_invoice(invoice_id):
        """Delete an invoice and its related items"""
        invoice = Invoice.query.get_or_404(invoice_id)
        
        # Get the file path if it exists
        file_path = invoice.file_path
        
        # Get customer information for the flash message
        customer_name = Customer.query.get(invoice.customer_id).name if Customer.query.get(invoice.customer_id) else "Unknown"
        invoice_number = invoice.invoice_number
        
        try:
            # First delete all related invoice items (cascade doesn't work here)
            InvoiceItem.query.filter_by(invoice_id=invoice_id).delete()
            
            # Then delete the invoice
            db.session.delete(invoice)
            db.session.commit()
            
            # Delete the file if it exists
            if file_path:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file_path))
                except (OSError, FileNotFoundError):
                    # If file is not found, just log and continue
                    logger.warning(f"Could not delete file at {file_path}")
            
            flash(f'Invoice #{invoice_number} for {customer_name} has been deleted successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting invoice: {str(e)}', 'danger')
            logger.error(f"Error deleting invoice {invoice_id}: {str(e)}")
        
        return redirect(url_for('invoices'))
        
    @app.route('/invoices/batch-delete', methods=['POST'])
    @login_required
    def batch_delete_invoices():
        """Delete multiple invoices at once"""
        data = request.get_json()
        invoice_ids = data.get('invoice_ids', [])
        
        if not invoice_ids:
            return jsonify({'error': 'No invoices selected'}), 400
            
        deleted_count = 0
        try:
            for invoice_id in invoice_ids:
                invoice = Invoice.query.get(invoice_id)
                if invoice:
                    # Delete file if it exists
                    if invoice.file_path:
                        try:
                            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], invoice.file_path))
                        except (OSError, FileNotFoundError):
                            logger.warning(f"Could not delete file for invoice {invoice_id}")
                    
                    # Delete invoice items
                    InvoiceItem.query.filter_by(invoice_id=invoice_id).delete()
                    
                    # Delete invoice
                    db.session.delete(invoice)
                    deleted_count += 1
            
            db.session.commit()
            return jsonify({'success': True, 'message': f'{deleted_count} invoices deleted successfully'})
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error in batch delete invoices: {str(e)}")
            return jsonify({'error': str(e)}), 500
            
    @app.route('/invoices/delete-all', methods=['POST'])
    @login_required
    def delete_all_invoices():
        """Delete all invoices from the database"""
        from utils.database_cleanup import delete_all_invoices
        
        success, message, deleted_count = delete_all_invoices()
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'danger')
            
        return redirect(url_for('invoices'))
    
    @app.route('/pending-updates')
    @login_required
    def pending_updates():
        """View all pending price update requests"""
        # Get filter parameters
        status = request.args.get('status', 'Pending')  # Default to showing pending updates
        customer_id = request.args.get('customer_id', '')
        page = request.args.get('page', 1, type=int)
        per_page = 20  # Items per page
        
        # Base query
        query = ProductUpdateRequest.query.join(Product)
        
        # Apply filters
        if status:
            query = query.filter(ProductUpdateRequest.status == status)
        if customer_id:
            # We need to join with PriceList to filter by customer
            query = query.join(PriceList).filter(PriceList.customer_id == customer_id)
            
        # Order by creation date (newest first)
        query = query.order_by(ProductUpdateRequest.created_at.desc())
        
        # Paginate results
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        updates = pagination.items
        
        # Get all customers for filter dropdown
        customers = Customer.query.all()
        
        return render_template('pending_updates.html', 
                              updates=updates,
                              customers=customers,
                              pagination=pagination,
                              selected_status=status,
                              selected_customer_id=customer_id)
    
    @app.route('/update/<int:update_id>/approve', methods=['POST'])
    @login_required
    def approve_update(update_id):
        """Approve a pending price update"""
        if approve_price_update(update_id):
            flash('Price update approved successfully.', 'success')
        else:
            flash('Failed to approve price update. The update may no longer exist or has already been processed.', 'danger')
        
        # Redirect back to the pending updates page
        return redirect(url_for('pending_updates'))
    
    @app.route('/update/<int:update_id>/reject', methods=['POST'])
    @login_required
    def reject_update(update_id):
        """Reject a pending price update"""
        if reject_price_update(update_id):
            flash('Price update rejected.', 'success')
        else:
            flash('Failed to reject price update. The update may no longer exist or has already been processed.', 'danger')
        
        # Redirect back to the pending updates page
        return redirect(url_for('pending_updates'))
    
    @app.route('/uploads/<filename>')
    @login_required
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        
    @app.route('/test-encoding', methods=['GET', 'POST'])
    @login_required
    def test_encoding():
        """Test the application's ability to handle different character encodings"""
        # Fetch products with potential Unicode characters
        products = Product.query.filter(
            db.or_(
                Product.name.like('%Κ%'),        # Greek
                Product.name.like('%Т%'),        # Cyrillic
                Product.scientific_name.like('%Δ%')  # Greek
            )
        ).limit(10).all()
        
        return render_template('test_encoding.html', products=products)
        
    @app.route('/test-encoding-submit', methods=['POST'])
    @login_required
    def test_encoding_submit():
        """Handle the test encoding form submission"""
        # Get form data
        name = request.form.get('name')
        category = request.form.get('category')
        scientific_name = request.form.get('scientific_name')
        pot = request.form.get('pot')
        
        # Create a test product with the provided data
        from utils.excel_parser import sanitize_string
        
        # Apply sanitization to ensure consistent handling
        safe_name = sanitize_string(name)
        safe_category = sanitize_string(category)
        safe_scientific_name = sanitize_string(scientific_name)
        safe_pot = sanitize_string(pot)
        safe_description = f"{safe_scientific_name or ''} {safe_pot or ''}".strip() or None
        
        product = Product(
            name=safe_name,
            category=safe_category,
            scientific_name=safe_scientific_name,
            pot=safe_pot,
            description=safe_description
        )
        
        # Log the data being saved
        logger.info(f"Test Encoding - Saving product with name: {safe_name}")
        logger.info(f"Test Encoding - Category: {safe_category}")
        logger.info(f"Test Encoding - Scientific Name: {safe_scientific_name}")
        logger.info(f"Test Encoding - Pot: {safe_pot}")
        
        # Save to database
        db.session.add(product)
        db.session.commit()
        
        # Fetch products with potential Unicode characters, including the one just created
        products = Product.query.filter(
            db.or_(
                Product.name.like('%Κ%'),        # Greek
                Product.name.like('%Т%'),        # Cyrillic
                Product.scientific_name.like('%Δ%')  # Greek
            )
        ).limit(10).all()
        
        # Return to the test encoding page with the results
        return render_template('test_encoding.html', product=product, products=products)
        
    # Quotation Management Routes
    @app.route('/quotations')
    @login_required
    def quotations():
        """View all quotations with filtering options"""
        # Get filter parameters
        customer_id = request.args.get('customer_id', type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Build the query
        query = Quotation.query
        
        # Apply filters if provided
        if customer_id:
            query = query.filter(Quotation.customer_id == customer_id)
            
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                query = query.filter(Quotation.quotation_date >= from_date)
            except ValueError:
                flash("Invalid 'from' date format. Please use YYYY-MM-DD.", 'warning')
                
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                query = query.filter(Quotation.quotation_date <= to_date)
            except ValueError:
                flash("Invalid 'to' date format. Please use YYYY-MM-DD.", 'warning')
        
        # Get customer list for filter dropdown
        customers = Customer.query.order_by(Customer.name).all()
        
        # Execute the query
        quotations = query.order_by(Quotation.created_at.desc()).all()
        
        return render_template('quotations.html', 
                              quotations=quotations,
                              customers=customers,
                              selected_customer_id=customer_id,
                              date_from=date_from,
                              date_to=date_to)
    
    @app.route('/upload-quotation')
    @login_required
    def upload_quotation():
        """Show the quotation upload page"""
        customers = Customer.query.order_by(Customer.name).all()
        return render_template('upload_quotation.html', customers=customers)
    
    @app.route('/upload-quotation-file', methods=['POST'])
    @login_required
    def upload_quotation_file():
        """Handle uploaded file for quotation creation"""
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(url_for('upload_quotation'))
        
        file = request.files['file']
        customer_id = request.form.get('customer_id')
        file_type = request.form.get('file_type')
        
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('upload_quotation'))
        
        if not customer_id:
            flash('Please select a customer', 'danger')
            return redirect(url_for('upload_quotation'))
            
        # Validate file type and extension
        allowed_extensions = {'excel': ['xlsx', 'xls'], 'pdf': ['pdf']}
        if file_type not in allowed_extensions:
            flash('Invalid file type selection', 'danger')
            return redirect(url_for('upload_quotation'))
            
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if file_ext not in allowed_extensions[file_type]:
            flash(f'Invalid file extension for {file_type}. Allowed: {", ".join(allowed_extensions[file_type])}', 'danger')
            return redirect(url_for('upload_quotation'))
        
        # Generate unique filename and save the file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        try:
            # Parse the file to extract product data
            quotation_data = parse_quotation_file(file_path, customer_id, file_type)
            
            # Store the extracted data in session for editing
            session['quotation_data'] = quotation_data
            
            # Get the customer info for the edit page
            customer = Customer.query.get_or_404(customer_id)
            
            # Get suppliers list for the dropdown
            suppliers_list = Supplier.query.order_by(Supplier.name).all()
            
            flash('File processed successfully. Please review and edit the quotation below.', 'success')
            return render_template('edit_quotation.html', 
                                  products=quotation_data['products'],
                                  customer=customer,
                                  quotation_number=quotation_data['quotation_number'],
                                  quotation_date=quotation_data['quotation_date'],
                                  suppliers=suppliers_list)
            
        except Exception as e:
            logger.error(f"Error processing file for quotation: {str(e)}")
            logger.error(traceback.format_exc())
            flash(f"Error processing file: {str(e)}", 'danger')
            return redirect(url_for('upload_quotation'))
            
    @app.route('/save-quotation', methods=['POST'])
    @login_required
    def save_quotation():
        """Save the finalized quotation"""
        try:
            # Get basic quotation data
            customer_id = request.form.get('customer_id', type=int)
            quotation_number = request.form.get('quotation_number')
            quotation_date_str = request.form.get('quotation_date')
            currency = request.form.get('currency', '€')
            notes = request.form.get('notes', '')
            
            # Parse quotation date
            try:
                quotation_date = datetime.strptime(quotation_date_str, '%Y-%m-%d').date()
            except ValueError:
                quotation_date = datetime.now().date()
            
            # Get the number of products
            product_count = int(request.form.get('product_count', 0))
            
            # Create new quotation
            quotation = Quotation(
                customer_id=customer_id,
                quotation_number=quotation_number,
                quotation_date=quotation_date,
                currency=currency,
                notes=notes
            )
            db.session.add(quotation)
            db.session.flush()  # Generate the quotation.id
            
            # Track totals for the quotation
            total_amount = 0
            
            # Process each product
            for i in range(product_count):
                # Get product data from the form
                description = request.form.get(f'description_{i}')
                scientific_name = request.form.get(f'scientific_name_{i}')
                pot_size = request.form.get(f'pot_size_{i}')
                height = request.form.get(f'height_{i}')
                # Convert 'None' string to actual None value
                product_id_raw = request.form.get(f'product_id_{i}')
                product_id = None if product_id_raw == 'None' else product_id_raw
                
                # Parse quantity with better error handling - using floats for more flexibility
                try:
                    quantity_raw = request.form.get(f'quantity_{i}', '1')
                    # First clean the quantity string (handle comma as decimal separator)
                    if isinstance(quantity_raw, str):
                        quantity_raw = quantity_raw.replace(',', '.').strip()
                    
                    quantity = float(quantity_raw)
                    # Log the quantity parsing for debugging
                    logger.info(f"Parsed quantity {quantity} from input '{request.form.get(f'quantity_{i}')}' for item {i}")
                except (ValueError, TypeError) as e:
                    quantity = 1
                    logger.warning(f"Invalid quantity format '{request.form.get(f'quantity_{i}')}' in quotation form item {i}, using default of 1. Error: {str(e)}")
                
                # Parse selling price with better error handling
                try:
                    selling_price_raw = request.form.get(f'selling_price_{i}', '0')
                    # Handle comma as decimal separator and remove currency symbols
                    if isinstance(selling_price_raw, str):
                        selling_price_raw = selling_price_raw.replace('€', '').replace(',', '.').strip()
                        selling_price_raw = re.sub(r'[^\d.]', '', selling_price_raw) if selling_price_raw else '0'
                    selling_price = float(selling_price_raw)
                except (ValueError, TypeError):
                    selling_price = 0
                    logger.warning(f"Invalid selling price format in quotation form item {i}, using 0")
                
                # Parse VAT rate with better error handling
                try:
                    vat_rate = float(request.form.get(f'vat_rate_{i}', 19))
                except (ValueError, TypeError):
                    vat_rate = 19  # Default VAT rate
                    logger.warning(f"Invalid VAT rate format in quotation form item {i}, using default of 19%")
                
                supplier = request.form.get(f'supplier_{i}')
                
                # Parse cost price with better error handling
                try:
                    cost_price_raw = request.form.get(f'cost_price_{i}', '0')
                    # Handle comma as decimal separator and remove currency symbols
                    if isinstance(cost_price_raw, str):
                        cost_price_raw = cost_price_raw.replace('€', '').replace(',', '.').strip()
                        cost_price_raw = re.sub(r'[^\d.]', '', cost_price_raw) if cost_price_raw else '0'
                    cost_price = float(cost_price_raw)
                except (ValueError, TypeError):
                    cost_price = 0
                    logger.warning(f"Invalid cost price format in quotation form item {i}, using 0")
                
                # Calculate item total
                item_total = quantity * selling_price
                total_amount += item_total
                
                # Check for existing product with same scientific name and pot size
                existing_product = None
                if scientific_name and pot_size:
                    existing_product = Product.query.filter(
                        db.func.lower(Product.scientific_name) == scientific_name.lower(),
                        db.func.lower(Product.pot) == pot_size.lower()
                    ).first()
                    
                    if existing_product:
                        logger.info(f"Found existing product in database: {existing_product.name} " +
                                   f"({existing_product.scientific_name}, {existing_product.pot})")
                        product_id = existing_product.id
                
                # Create quotation item
                quotation_item = QuotationItem(
                    quotation_id=quotation.id,
                    product_id=int(product_id) if product_id and product_id != 'None' else None,
                    description=description,
                    scientific_name=scientific_name,
                    pot_size=pot_size,
                    height=height,
                    quantity=quantity,
                    selling_price=selling_price,
                    vat_rate=vat_rate,
                    supplier=supplier,
                    cost_price=cost_price,
                    total=item_total
                )
                db.session.add(quotation_item)
            
            # Update the quotation total
            quotation.total_amount = total_amount
            db.session.commit()
            
            # Update supplier products from the quotation items
            from utils.supplier_manager import update_suppliers_from_quotation
            supplier_results = update_suppliers_from_quotation(quotation)
            
            # Create a more detailed success message
            if supplier_results['success_count'] > 0:
                flash(f'Quotation created successfully! Products have been automatically added to supplier database and checked against existing products in main catalog.', 'success')
            else:
                flash('Quotation created successfully!', 'success')
                
            return redirect(url_for('view_quotation', quotation_id=quotation.id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving quotation: {str(e)}")
            logger.error(traceback.format_exc())
            flash(f"Error saving quotation: {str(e)}", 'danger')
            return redirect(url_for('upload_quotation'))
            
    @app.route('/quotation/<int:quotation_id>')
    @login_required
    def view_quotation(quotation_id):
        """View details of a specific quotation"""
        quotation = Quotation.query.get_or_404(quotation_id)
        
        # Calculate subtotal and VAT summary
        subtotal = 0
        vat_dict = {}  # Dictionary to track VAT by rate
        
        for item in quotation.items:
            item_subtotal = item.quantity * item.selling_price
            subtotal += item_subtotal
            
            # Track VAT amounts by rate
            vat_rate = item.vat_rate
            vat_amount = item_subtotal * (vat_rate / 100)
            
            if vat_rate in vat_dict:
                vat_dict[vat_rate] += vat_amount
            else:
                vat_dict[vat_rate] = vat_amount
        
        # Convert VAT dict to list for the template
        vat_summary = [{'rate': rate, 'amount': amount} for rate, amount in vat_dict.items()]
        
        # Create a dictionary of suppliers and item counts
        suppliers_dict = {}
        for item in quotation.items:
            if item.supplier:
                if item.supplier in suppliers_dict:
                    suppliers_dict[item.supplier] += 1
                else:
                    suppliers_dict[item.supplier] = 1
        
        # Get all suppliers for the dropdown in edit form
        all_suppliers = Supplier.query.order_by(Supplier.name).all()
        
        return render_template('view_quotation.html', 
                              quotation=quotation,
                              subtotal=subtotal,
                              vat_summary=vat_summary,
                              suppliers=suppliers_dict,
                              all_suppliers=all_suppliers)
    
    @app.route('/quotation/<int:quotation_id>/export')
    @login_required
    def export_quotation(quotation_id):
        """Export a quotation as PDF using the standard template"""
        quotation = Quotation.query.get_or_404(quotation_id)
        
        try:
            # Generate the PDF using standard template
            pdf_path = generate_quotation_pdf(quotation, app.config['UPLOAD_FOLDER'], use_modern_template=False)
            
            # Update the quotation with the PDF path
            quotation.file_path = os.path.basename(pdf_path)
            db.session.commit()
            
            # Send the file to the client
            return send_from_directory(
                directory=app.config['UPLOAD_FOLDER'],
                path=os.path.basename(pdf_path),
                as_attachment=True,
                download_name=f"Quotation_{quotation.quotation_number}.pdf"
            )
            
        except Exception as e:
            logger.error(f"Error exporting quotation: {str(e)}")
            logger.error(traceback.format_exc())
            flash(f"Error generating PDF: {str(e)}", 'danger')
            return redirect(url_for('view_quotation', quotation_id=quotation_id))
            
    @app.route('/quotation/<int:quotation_id>/export/excel')
    @login_required
    def export_quotation_excel(quotation_id):
        """Export a quotation as Excel (.xlsx) file with optional column selection"""
        from utils.excel_generator import generate_quotation_excel
        
        quotation = Quotation.query.get_or_404(quotation_id)
        
        # Map of supported fields
        all_fields = {
            "index": "#",
            "description": "Description",
            "scientific_name": "Scientific Name",
            "pot_size": "Actual Size",
            "height": "Asked Size",
            "quantity": "Quantity",
            "unit_price": "Unit Price",
            "vat_rate": "VAT Rate",
            "supplier": "Supplier",
            "total_price": "Total"
        }
        
        # Get selected fields from GET parameters
        selected_keys = request.args.getlist("columns") or list(all_fields.keys())
        
        # Prepare field config
        selected_fields = [{"key": k, "label": all_fields[k]} for k in selected_keys if k in all_fields]
        
        try:
            # Generate the Excel file with selected columns
            file_path = generate_quotation_excel(
                quotation, 
                app.config['UPLOAD_FOLDER'],
                columns=selected_fields
            )
            
            # Send the file to the client
            return send_from_directory(
                directory=app.config['UPLOAD_FOLDER'],
                path=os.path.basename(file_path),
                as_attachment=True,
                download_name=f"{quotation.quotation_number}_quotation.xlsx"
            )
            
        except Exception as e:
            logger.error(f"Error exporting Excel: {str(e)}")
            logger.error(traceback.format_exc())
            flash(f"Error generating Excel file: {str(e)}", 'danger')
            return redirect(url_for('view_quotation', quotation_id=quotation_id))
            
    @app.route('/quotation/<int:quotation_id>/export/modern')
    @login_required
    def export_quotation_modern(quotation_id):
        """Export a quotation as PDF using the modern template"""
        quotation = Quotation.query.get_or_404(quotation_id)
        
        try:
            # Generate the PDF using modern template
            pdf_path = generate_quotation_pdf(quotation, app.config['UPLOAD_FOLDER'], use_modern_template=True)
            
            # Update the quotation with the PDF path (we're not updating to avoid overwriting standard PDF path)
            # quotation.file_path = os.path.basename(pdf_path)
            # db.session.commit()
            
            # Send the file to the client
            return send_from_directory(
                directory=app.config['UPLOAD_FOLDER'],
                path=os.path.basename(pdf_path),
                as_attachment=True,
                download_name=f"Modern_Quotation_{quotation.quotation_number}.pdf"
            )
            
        except Exception as e:
            logger.error(f"Error exporting quotation with modern template: {str(e)}")
            logger.error(traceback.format_exc())
            flash(f"Error generating modern PDF: {str(e)}", 'danger')
            return redirect(url_for('view_quotation', quotation_id=quotation_id))
    
    @app.route('/quotation/<int:quotation_id>/export/fixed')
    @login_required
    def export_quotation_fixed(quotation_id):
        """Export a quotation as PDF using the enhanced generator to fix missing items"""
        quotation = Quotation.query.get_or_404(quotation_id)
        
        try:
            # Generate the PDF using enhanced generator
            pdf_path = generate_enhanced_pdf(quotation, app.config['UPLOAD_FOLDER'], use_modern_template=True)
            
            # Send the file to the client
            return send_from_directory(
                directory=app.config['UPLOAD_FOLDER'],
                path=os.path.basename(pdf_path),
                as_attachment=True,
                download_name=f"Fixed_Quotation_{quotation.quotation_number}.pdf"
            )
            
        except Exception as e:
            logger.error(f"Error exporting quotation with enhanced generator: {str(e)}")
            logger.error(traceback.format_exc())
            flash(f"Error generating fixed PDF: {str(e)}", 'danger')
            return redirect(url_for('view_quotation', quotation_id=quotation_id))

    @app.route('/quotation/<int:quotation_id>/export/debug')
    @login_required
    def export_quotation_debug(quotation_id):
        """Export a quotation with debug visuals to identify missing items"""
        quotation = Quotation.query.get_or_404(quotation_id)
        
        try:
            # Generate the PDF using enhanced generator with debug mode
            pdf_path = generate_enhanced_pdf(quotation, app.config['UPLOAD_FOLDER'], 
                                           use_modern_template=True, debug=True)
            
            # Send the file to the client
            return send_from_directory(
                directory=app.config['UPLOAD_FOLDER'],
                path=os.path.basename(pdf_path),
                as_attachment=True,
                download_name=f"Debug_Quotation_{quotation.quotation_number}.pdf"
            )
            
        except Exception as e:
            logger.error(f"Error exporting debug quotation: {str(e)}")
            logger.error(traceback.format_exc())
            flash(f"Error generating debug PDF: {str(e)}", 'danger')
            return redirect(url_for('view_quotation', quotation_id=quotation_id))
    
    @app.route('/quotation/<int:quotation_id>/supplier/<path:supplier>')
    @login_required
    def export_supplier_report(quotation_id, supplier):
        """Export a supplier-specific report from a quotation"""
        quotation = Quotation.query.get_or_404(quotation_id)
        
        try:
            # Generate the supplier report
            pdf_path = generate_supplier_pdf_report(quotation, supplier, app.config['UPLOAD_FOLDER'])
            
            if not pdf_path:
                flash(f"No items found for supplier '{supplier}'", 'warning')
                return redirect(url_for('view_quotation', quotation_id=quotation_id))
            
            # Send the file to the client
            return send_from_directory(
                directory=app.config['UPLOAD_FOLDER'],
                path=os.path.basename(pdf_path),
                as_attachment=True,
                download_name=f"Supplier_{supplier}_Quotation_{quotation.quotation_number}.pdf"
            )
            
        except Exception as e:
            logger.error(f"Error exporting supplier report: {str(e)}")
            logger.error(traceback.format_exc())
            flash(f"Error generating supplier report: {str(e)}", 'danger')
            return redirect(url_for('view_quotation', quotation_id=quotation_id))
    
    @app.route('/quotation/<int:quotation_id>/custom_supplier_report', methods=['GET', 'POST'])
    @login_required
    def custom_supplier_report(quotation_id):
        """Create a custom report with multiple suppliers and configurable fields"""
        quotation = Quotation.query.get_or_404(quotation_id)
        
        # Get unique suppliers from this quotation
        suppliers = set(item.supplier for item in quotation.items if item.supplier)
        
        # Define available fields for customization
        available_fields = [
            {'key': 'description', 'label': 'Description', 'default': True},
            {'key': 'scientific_name', 'label': 'Scientific Name', 'default': True},
            {'key': 'pot_size', 'label': 'Pot Size', 'default': True},
            {'key': 'height', 'label': 'Height', 'default': True},
            {'key': 'quantity', 'label': 'Quantity', 'default': True},
            {'key': 'selling_price', 'label': 'Selling Price', 'default': False},
            {'key': 'cost_price', 'label': 'Cost Price', 'default': True},
            {'key': 'total', 'label': 'Total', 'default': True},
            {'key': 'vat_rate', 'label': 'VAT Rate', 'default': False}
        ]
        
        if request.method == 'POST':
            try:
                # Get selected suppliers
                selected_suppliers = request.form.getlist('suppliers')
                
                if not selected_suppliers:
                    flash("Please select at least one supplier", "warning")
                    return redirect(url_for('custom_supplier_report', quotation_id=quotation_id))
                
                # Get selected fields
                selected_fields = request.form.getlist('fields')
                
                if not selected_fields:
                    # Default to all fields if none selected
                    selected_fields = [field['key'] for field in available_fields if field['default']]
                
                # Get report options
                include_prices = request.form.get('include_prices') == 'on'
                include_company_header = request.form.get('include_company_header') == 'on'
                include_terms = request.form.get('include_terms') == 'on'
                group_by_supplier = request.form.get('group_by_supplier') == 'on'
                use_fpdf = request.form.get('use_fpdf') == 'on'
                use_ubuntu = request.form.get('use_ubuntu') == 'on'
                use_dejavu = False  # Removed DejaVu option from the form
                notes = request.form.get('notes', '')
                
                # Generate the custom report
                from utils.pdf_generator import generate_custom_supplier_report
                from utils.pdf_generator_update import generate_custom_supplier_report_with_ubuntu

                # If using Ubuntu fonts
                if use_ubuntu:
                    try:
                        pdf_file, filename = generate_custom_supplier_report_with_ubuntu(
                            quotation, 
                            selected_suppliers, 
                            selected_fields,
                            include_prices=include_prices,
                            include_company_header=include_company_header,
                            include_terms=include_terms,
                            group_by_supplier=group_by_supplier,
                            notes=notes if notes else None
                        )
                    except Exception as e:
                        logger.error(f"Error generating report with Ubuntu font: {str(e)}")
                        logger.error(traceback.format_exc())
                        flash(f"Error generating report with Ubuntu font, falling back to standard method: {str(e)}", 'warning')
                        # Fall back to standard method
                        pdf_file, filename = generate_custom_supplier_report(
                            quotation, 
                            selected_suppliers, 
                            selected_fields,
                            include_prices=include_prices,
                            include_company_header=include_company_header,
                            include_terms=include_terms,
                            group_by_supplier=group_by_supplier,
                            notes=notes if notes else None,
                            use_fpdf=False  # Default to WeasyPrint as a fallback
                        )
                else:
                    # Original PDF generation method
                    pdf_file, filename = generate_custom_supplier_report(
                        quotation, 
                        selected_suppliers, 
                        selected_fields,
                        include_prices=include_prices,
                        include_company_header=include_company_header,
                        include_terms=include_terms,
                        group_by_supplier=group_by_supplier,
                        notes=notes if notes else None,
                        use_fpdf=use_fpdf
                    )
                
                # Send the PDF as a download
                response = make_response(pdf_file)
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = f'attachment; filename={filename}'
                return response
                
            except Exception as e:
                logger.error(f"Error generating custom supplier report: {str(e)}")
                logger.error(traceback.format_exc())
                flash(f"Error generating report: {str(e)}", 'danger')
                return redirect(url_for('view_quotation', quotation_id=quotation_id))
        
        # GET request - show the form
        return render_template(
            'custom_supplier_report.html',
            quotation=quotation,
            suppliers=sorted(suppliers),
            available_fields=available_fields
        )
    
    @app.route('/quotation/<int:quotation_id>/delete')
    @login_required
    def delete_quotation(quotation_id):
        """Delete a quotation and its related items"""
        quotation = Quotation.query.get_or_404(quotation_id)
        
        try:
            # Delete the quotation (cascade will delete items)
            db.session.delete(quotation)
            db.session.commit()
            flash('Quotation deleted successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting quotation: {str(e)}")
            flash(f"Error deleting quotation: {str(e)}", 'danger')
        
        return redirect(url_for('quotations'))
        
    @app.route('/quotation/<int:quotation_id>/item/add', methods=['POST'])
    @login_required
    def add_quotation_item(quotation_id):
        """Add a new item to an existing quotation"""
        quotation = Quotation.query.get_or_404(quotation_id)
        
        try:
            # Get form data
            description = request.form.get('description')
            scientific_name = request.form.get('scientific_name')
            pot_size = request.form.get('pot_size')
            height = request.form.get('height')
            
            # Parse quantity with better error handling - using integers
            try:
                quantity = int(request.form.get('quantity', 1))
            except (ValueError, TypeError):
                quantity = 1
                logger.warning("Invalid quantity format in add quotation item, using default of 1")
            
            # Parse selling price with better error handling
            try:
                selling_price_raw = request.form.get('selling_price', '0')
                # Handle comma as decimal separator and remove currency symbols
                if isinstance(selling_price_raw, str):
                    selling_price_raw = selling_price_raw.replace('€', '').replace(',', '.').strip()
                    selling_price_raw = re.sub(r'[^\d.]', '', selling_price_raw) if selling_price_raw else '0'
                selling_price = float(selling_price_raw)
            except (ValueError, TypeError):
                selling_price = 0
                logger.warning("Invalid selling price format in add quotation item, using 0")
            
            # Parse VAT rate with better error handling
            try:
                vat_rate = float(request.form.get('vat_rate', 19))
            except (ValueError, TypeError):
                vat_rate = 19  # Default VAT rate
                logger.warning("Invalid VAT rate format in add quotation item, using default of 19%")
                
            # Get supplier information
            supplier = request.form.get('supplier')
            supplier_id = request.form.get('supplier_id')
            if supplier_id:
                try:
                    supplier_id = int(supplier_id)
                    # If we have a supplier_id, get the supplier name
                    supplier_obj = Supplier.query.get(supplier_id)
                    if supplier_obj:
                        supplier = supplier_obj.name
                except (ValueError, TypeError):
                    supplier_id = None
                    logger.warning("Invalid supplier_id in add quotation item, ignoring")
            
            # Parse cost price with better error handling
            try:
                cost_price_raw = request.form.get('cost_price', '0')
                # Handle comma as decimal separator and remove currency symbols
                if isinstance(cost_price_raw, str):
                    cost_price_raw = cost_price_raw.replace('€', '').replace(',', '.').strip()
                    cost_price_raw = re.sub(r'[^\d.]', '', cost_price_raw) if cost_price_raw else '0'
                cost_price = float(cost_price_raw)
            except (ValueError, TypeError):
                cost_price = 0
                logger.warning("Invalid cost price format in add quotation item, using 0")
                
            # Calculate total
            total = quantity * selling_price
            
            # Check for existing product with same scientific name and pot size
            product_id = None
            if scientific_name and pot_size:
                existing_product = Product.query.filter(
                    db.func.lower(Product.scientific_name) == scientific_name.lower(),
                    db.func.lower(Product.pot) == pot_size.lower()
                ).first()
                
                if existing_product:
                    logger.info(f"Found existing product in database: {existing_product.name} " +
                               f"({existing_product.scientific_name}, {existing_product.pot})")
                    product_id = existing_product.id
            
            # Create the new item
            new_item = QuotationItem(
                quotation_id=quotation.id,
                product_id=product_id,
                description=description,
                scientific_name=scientific_name,
                pot_size=pot_size,
                height=height,
                quantity=quantity,
                selling_price=selling_price,
                vat_rate=vat_rate,
                supplier=supplier,
                supplier_id=supplier_id if supplier_id else None,
                cost_price=cost_price,
                total=total
            )
            
            db.session.add(new_item)
            
            # Update quotation total
            quotation.total_amount = (quotation.total_amount or 0) + total
            db.session.commit()
            
            # Update supplier products based on the new item
            from utils.supplier_manager import update_supplier_from_quotation_item
            update_supplier_from_quotation_item(new_item)
            
            flash('Item added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding quotation item: {str(e)}")
            flash(f"Error adding item: {str(e)}", 'danger')
            
        return redirect(url_for('view_quotation', quotation_id=quotation_id))
        
    @app.route('/quotation/<int:quotation_id>/item/<int:item_id>', methods=['POST'])
    @login_required
    @with_db_reconnect(max_retries=3)
    def edit_quotation_item(quotation_id, item_id):
        """Edit an existing quotation item with AJAX support"""
        quotation = Quotation.query.get_or_404(quotation_id)
        item = QuotationItem.query.get_or_404(item_id)
        
        # Verify that the item belongs to this quotation
        if item.quotation_id != quotation.id:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': 'Item does not belong to this quotation!'})
            else:
                flash('Item does not belong to this quotation!', 'danger')
                return redirect(url_for('view_quotation', quotation_id=quotation_id))
            
        try:
            # Calculate old total to update quotation total
            old_total = item.total or (item.quantity * item.selling_price)
            
            # Update item fields
            item.description = request.form.get('description')
            item.scientific_name = request.form.get('scientific_name')
            item.pot_size = request.form.get('pot_size')
            item.height = request.form.get('height')
            
            # Parse quantity with bullet-proof error handling
            original_quantity = item.quantity  # Save original value for logging and fallback
            qty_raw = request.form.get('quantity')
            
            try:
                # Only update if we have a non-empty value
                if qty_raw and qty_raw.strip():
                    new_quantity = int(qty_raw)
                    if new_quantity <= 0:
                        raise ValueError("Quantity must be positive")
                    item.quantity = new_quantity
                    logger.info(f"Updated quantity for item {item_id} from {original_quantity} to {item.quantity}")
                else:
                    logger.info(f"Empty quantity submitted for item {item_id}, keeping original value: {original_quantity}")
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid quantity format '{qty_raw}' in edit quotation item {item_id}, keeping original value: {original_quantity}. Error: {str(e)}")
            
            # Parse selling price with better error handling
            try:
                selling_price_raw = request.form.get('selling_price', '0')
                # Handle comma as decimal separator and remove currency symbols
                if isinstance(selling_price_raw, str):
                    selling_price_raw = selling_price_raw.replace('€', '').replace(',', '.').strip()
                    selling_price_raw = re.sub(r'[^\d.]', '', selling_price_raw) if selling_price_raw else '0'
                item.selling_price = float(selling_price_raw)
            except (ValueError, TypeError):
                item.selling_price = 0
                logger.warning(f"Invalid selling price format in edit quotation item {item_id}, using 0")
            
            # Parse VAT rate with better error handling
            try:
                item.vat_rate = float(request.form.get('vat_rate', 19))
            except (ValueError, TypeError):
                item.vat_rate = 19  # Default VAT rate
                logger.warning(f"Invalid VAT rate format in edit quotation item {item_id}, using default of 19%")
                
            # Update supplier text field
            item.supplier = request.form.get('supplier')
            
            # Update supplier_id if provided
            supplier_id = request.form.get('supplier_id')
            if supplier_id:
                try:
                    item.supplier_id = int(supplier_id)
                    # If we have a valid supplier_id, get the supplier name
                    supplier_obj = Supplier.query.get(item.supplier_id)
                    if supplier_obj:
                        item.supplier = supplier_obj.name
                except (ValueError, TypeError):
                    logger.warning(f"Invalid supplier_id in edit quotation item {item_id}, ignoring")
            
            # Parse cost price with better error handling
            try:
                cost_price_raw = request.form.get('cost_price', '0')
                # Handle comma as decimal separator and remove currency symbols
                if isinstance(cost_price_raw, str):
                    cost_price_raw = cost_price_raw.replace('€', '').replace(',', '.').strip()
                    cost_price_raw = re.sub(r'[^\d.]', '', cost_price_raw) if cost_price_raw else '0'
                item.cost_price = float(cost_price_raw)
            except (ValueError, TypeError):
                item.cost_price = 0
                logger.warning(f"Invalid cost price format in edit quotation item {item_id}, using 0")
                
            # Check for existing product with same scientific name and pot size
            if item.scientific_name and item.pot_size:
                existing_product = Product.query.filter(
                    db.func.lower(Product.scientific_name) == item.scientific_name.lower(),
                    db.func.lower(Product.pot) == item.pot_size.lower()
                ).first()
                
                if existing_product:
                    logger.info(f"Found existing product in database: {existing_product.name} " +
                               f"({existing_product.scientific_name}, {existing_product.pot})")
                    item.product_id = existing_product.id
            
            # Calculate new total
            new_total = item.quantity * item.selling_price
            item.total = new_total
            
            # Update quotation total
            quotation.total_amount = (quotation.total_amount or 0) - old_total + new_total
            
            db.session.commit()
            
            # Update supplier products based on the updated item
            from utils.supplier_manager import update_supplier_from_quotation_item
            update_supplier_from_quotation_item(item)
            
            # If this is an AJAX request, return JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True,
                    'message': 'Item updated successfully!',
                    'item': {
                        'id': item.id,
                        'description': item.description,
                        'scientific_name': item.scientific_name or '',
                        'pot_size': item.pot_size or '',
                        'height': item.height or '',
                        'quantity': item.quantity,
                        'selling_price': item.selling_price,
                        'vat_rate': item.vat_rate,
                        'supplier': item.supplier or 'Not specified',
                        'total': item.total,
                        'position': item.position
                    },
                    'quotation_total': quotation.total_amount
                })
            else:
                # Standard form submission (fallback)
                flash('Item updated successfully!', 'success')
                return redirect(url_for('view_quotation', quotation_id=quotation_id))
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating quotation item: {str(e)}")
            
            # If this is an AJAX request, return JSON error
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': str(e)})
            else:
                # Standard form submission (fallback)
                flash(f"Error updating item: {str(e)}", 'danger')
                return redirect(url_for('view_quotation', quotation_id=quotation_id))
    
    @app.route('/quotation/<int:quotation_id>/reorder-items', methods=['POST'])
    @login_required
    @with_db_reconnect(max_retries=3)
    def reorder_drag_quotation_items(quotation_id):
        """Update the order of items in a quotation via AJAX"""
        quotation = Quotation.query.get_or_404(quotation_id)
        
        try:
            # Get the JSON data sent from the client
            data = request.get_json()
            
            if not data or 'items' not in data:
                return jsonify({'success': False, 'error': 'Invalid data format'}), 400
                
            items_data = data['items']
            
            # Start a transaction
            with db.session.begin_nested():
                for item_data in items_data:
                    item_id = item_data.get('id')
                    new_position = item_data.get('position')
                    
                    if not item_id or not new_position:
                        continue
                        
                    # Get the item and update its position
                    item = QuotationItem.query.filter_by(id=item_id, quotation_id=quotation_id).first()
                    if item:
                        item.position = new_position
            
            # Commit the changes to the database
            db.session.commit()
            
            # Log the successful reordering
            logger.info(f"Reordered items for quotation #{quotation.quotation_number} (ID: {quotation_id})")
            
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error reordering quotation items: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
        
    @app.route('/quotation/item/<int:item_id>/delete')
    @login_required
    @with_db_reconnect(max_retries=3)
    def delete_quotation_item(item_id):
        """Delete a quotation item"""
        item = QuotationItem.query.get_or_404(item_id)
        quotation_id = item.quotation_id
        
        try:
            # Get the quotation to update its total
            quotation = Quotation.query.get(quotation_id)
            
            if quotation:
                # Calculate item total
                item_total = item.total or (item.quantity * item.selling_price)
                
                # Update quotation total
                quotation.total_amount = max(0, (quotation.total_amount or 0) - item_total)
            
            # Delete the item
            db.session.delete(item)
            db.session.commit()
            
            flash('Item deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting quotation item: {str(e)}")
            flash(f"Error deleting item: {str(e)}", 'danger')
            
        return redirect(url_for('view_quotation', quotation_id=quotation_id))
    
    @app.route('/quotation/<int:quotation_id>/item/quick_add', methods=['POST'])
    @login_required
    @with_db_reconnect(max_retries=3)
    def quick_add_quotation_item(quotation_id):
        """Add a new quotation item via AJAX with minimal information"""
        quotation = Quotation.query.get_or_404(quotation_id)
        
        try:
            description = request.form.get('description', '')
            if not description:
                return jsonify({'error': 'Description is required'}), 400
                
            # Create a new item with the next position
            position = QuotationItem.query.filter_by(quotation_id=quotation_id).count()
            
            # Create the new item
            item = QuotationItem(
                quotation_id=quotation_id,
                description=description,
                quantity=1,
                selling_price=0,
                vat_rate=19.0,
                position=position
            )
            
            db.session.add(item)
            db.session.commit()
            
            # Return the new item details for the UI
            return jsonify({
                'id': item.id, 
                'description': item.description,
                'position': item.position
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding quotation item: {str(e)}")
            return jsonify({'error': str(e)}), 500
    

    
    @app.route('/supplier/quick_add', methods=['POST'])
    @login_required
    def quick_add_supplier():
        """Add a new supplier via AJAX for quotation editor"""
        try:
            name = request.form.get('name', '')
            if not name:
                return jsonify({'error': 'Supplier name is required'}), 400
                
            # Check if supplier with this name already exists
            existing = Supplier.query.filter(Supplier.name == name).first()
            if existing:
                # Return the existing supplier instead of error
                return jsonify({
                    'id': existing.id,
                    'name': existing.name
                })
                
            # Create new supplier
            supplier = Supplier(
                name=name,
                notes="Created from quotation editor"
            )
            
            db.session.add(supplier)
            db.session.commit()
            
            return jsonify({
                'id': supplier.id,
                'name': supplier.name
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding supplier: {str(e)}")
            return jsonify({'error': str(e)}), 500
        
    # Supplier Management Routes
    @app.route('/suppliers')
    @login_required
    def suppliers():
        """View and manage suppliers"""
        # Get search query parameter if any
        search_query = request.args.get('q', '')
        supplier_type = request.args.get('type', 'all')
        sort_by = request.args.get('sort', 'name_asc')
        
        # Start with the base query
        query = Supplier.query
        
        # Apply search filter if provided
        if search_query:
            query = query.filter(
                db.or_(
                    Supplier.name.ilike(f'%{search_query}%'),
                    Supplier.contact_person.ilike(f'%{search_query}%'),
                    Supplier.email.ilike(f'%{search_query}%')
                )
            )
        
        # Apply supplier type filter
        if supplier_type == 'inhouse':
            query = query.filter(Supplier.is_inhouse == True)
        elif supplier_type == 'external':
            query = query.filter(Supplier.is_inhouse == False)
        
        # Apply sorting
        if sort_by == 'name_desc':
            query = query.order_by(Supplier.name.desc())
        elif sort_by == 'newest':
            query = query.order_by(Supplier.created_at.desc())
        elif sort_by == 'oldest':
            query = query.order_by(Supplier.created_at)
        else:  # Default: name_asc
            query = query.order_by(Supplier.name)
        
        # Execute the query
        suppliers_list = query.all()
        
        # Count suppliers by type for metrics
        total_count = len(suppliers_list)
        inhouse_count = sum(1 for s in suppliers_list if s.is_inhouse)
        external_count = total_count - inhouse_count
        
        return render_template(
            'suppliers.html', 
            suppliers=suppliers_list,
            search_query=search_query,
            supplier_type=supplier_type,
            sort_by=sort_by,
            metrics={
                'total': total_count,
                'inhouse': inhouse_count,
                'external': external_count
            }
        )
        
    @app.route('/api/suppliers')
    @login_required
    def api_suppliers():
        """API endpoint to get suppliers as JSON"""
        try:
            format_type = request.args.get('format', 'detailed')
            query = request.args.get('q', '')
            
            # Base query
            suppliers_query = Supplier.query
            
            # Apply search filter if query provided
            if query:
                suppliers_query = suppliers_query.filter(
                    db.or_(
                        Supplier.name.ilike(f'%{query}%'),
                        Supplier.contact_person.ilike(f'%{query}%'),
                        Supplier.email.ilike(f'%{query}%')
                    )
                )
            
            # Order results by name
            suppliers_list = suppliers_query.order_by(Supplier.name).all()
            
            # Log the number of suppliers found for debugging
            logger.info(f"API suppliers found: {len(suppliers_list)}")
            
            # Format results based on requested format
            if format_type == 'simple':
                # Simple format: just id and name for dropdowns
                result = [{"id": s.id, "name": s.name} for s in suppliers_list]
            else:
                # Detailed format: full supplier information
                result = [s.to_dict() for s in suppliers_list]
            
            return jsonify({
                "status": "success",
                "count": len(result),
                "suppliers": result
            })
            
        except Exception as e:
            logger.error(f"Error in API suppliers endpoint: {str(e)}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500
        
    @app.route('/add_supplier', methods=['POST'])
    @login_required
    def add_supplier():
        """Add a new supplier or get existing one"""
        from utils.supplier_utils import get_supplier_by_name_or_create
        from utils.validation import is_valid_email, sanitize_input
        
        name = request.form.get('name', '').strip()
        contact_person = request.form.get('contact_person')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        notes = sanitize_input(request.form.get('notes', ''))
        is_inhouse = request.form.get('is_inhouse') == '1'
        
        if not name:
            flash('Supplier name is required.', 'danger')
            return redirect(url_for('suppliers'))
            
        # Validate email if provided
        if email and not is_valid_email(email):
            flash('Invalid email address format. Please check and try again.', 'danger')
            return redirect(url_for('suppliers'))
            
        try:
            supplier, created = get_supplier_by_name_or_create(
                name=name,
                contact_person=contact_person,
                email=email,
                phone=phone,
                address=address,
                notes=notes,
                is_inhouse=is_inhouse
            )
            
            if supplier:
                if created:
                    flash(f'Supplier "{supplier.name}" created successfully.', 'success')
                else:
                    flash(f'Supplier "{supplier.name}" already exists.', 'info')
            else:
                flash('Failed to add supplier. Please try again.', 'danger')
                
        except Exception as e:
            logger.error(f"Unexpected error in add_supplier route: {str(e)}")
            flash(f'Error adding supplier: {str(e)}', 'danger')
            
        return redirect(url_for('suppliers'))
        
    @app.route('/edit_supplier/<int:supplier_id>', methods=['GET', 'POST'])
    @login_required
    def edit_supplier(supplier_id):
        """Edit an existing supplier"""
        from utils.supplier_utils import update_supplier
        
        supplier = Supplier.query.get_or_404(supplier_id)
        
        # GET request - show the form with the supplier's data
        if request.method == 'GET':
            suppliers_list = Supplier.query.order_by(Supplier.name).all()
            return render_template('edit_supplier.html', supplier=supplier, suppliers=suppliers_list)
        
        # POST request - process the form
        name = request.form.get('name')
        contact_person = request.form.get('contact_person')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        notes = request.form.get('notes')
        is_inhouse = request.form.get('is_inhouse') == '1'
        
        if not name:
            flash('Supplier name is required.', 'danger')
            return redirect(url_for('suppliers'))
            
        # Validate email if provided
        from utils.validation import is_valid_email, sanitize_input
        if email and not is_valid_email(email):
            flash('Invalid email address format. Please check and try again.', 'danger')
            suppliers_list = Supplier.query.order_by(Supplier.name).all()
            return render_template('edit_supplier.html', supplier=supplier, suppliers=suppliers_list)
            
        # Sanitize notes
        notes = sanitize_input(notes)
            
        try:
            # Update the supplier using our utility function
            supplier, success, message = update_supplier(
                supplier_id=supplier_id,
                name=name,
                contact_person=contact_person,
                email=email,
                phone=phone,
                address=address,
                notes=notes,
                is_inhouse=is_inhouse
            )
            
            if success:
                flash(f'Supplier "{name}" updated successfully.', 'success')
            else:
                flash(message, 'danger')
                
        except Exception as e:
            logger.error(f"Unexpected error in edit_supplier route: {str(e)}")
            flash(f'Error updating supplier: {str(e)}', 'danger')
            
        return redirect(url_for('suppliers'))
        
    @app.route('/delete_supplier/<int:supplier_id>')
    @login_required
    def delete_supplier(supplier_id):
        """Delete a supplier"""
        from utils.supplier_utils import delete_supplier as delete_supplier_util
        
        try:
            # First, get the supplier name for the success message
            supplier = Supplier.query.get_or_404(supplier_id)
            supplier_name = supplier.name
            
            # Use our utility function to delete the supplier
            success, message = delete_supplier_util(supplier_id)
            
            if success:
                flash(message, 'success')
            else:
                flash(message, 'danger')
                
        except Exception as e:
            logger.error(f"Unexpected error in delete_supplier route: {str(e)}")
            flash(f'Error deleting supplier: {str(e)}', 'danger')
            
        return redirect(url_for('suppliers'))
    
    # Supplier Product Management Routes
    @app.route('/supplier_products')
    @login_required
    def supplier_products():
        """View and manage supplier products"""
        from utils.supplier_manager import search_supplier_products
        
        query = request.args.get('q', '')
        supplier_id = request.args.get('supplier_id')
        show_duplicates = request.args.get('show_duplicates') == '1'
        
        # Get all suppliers for the filter dropdown
        suppliers_list = Supplier.query.order_by(Supplier.name).all()
        
        # Get the current supplier if one is selected
        current_supplier = None
        if supplier_id:
            try:
                supplier_id = int(supplier_id)
                current_supplier = Supplier.query.get(supplier_id)
            except (ValueError, TypeError):
                pass
        
        # Search for products
        products = search_supplier_products(query, supplier_id, show_duplicates=show_duplicates, limit=100)
        
        return render_template(
            'supplier_products.html',
            supplier_products=products,
            suppliers=suppliers_list,
            current_supplier=current_supplier,
            query=query
        )
    
    @app.route('/add_supplier_product', methods=['GET', 'POST'])
    @login_required
    def add_supplier_product():
        """Add a new supplier product"""
        from datetime import datetime
        
        if request.method == 'POST':
            supplier_id = request.form.get('supplier_id')
            product_name = request.form.get('product_name')
            scientific_name = request.form.get('scientific_name')
            height = request.form.get('height')
            pot_size = request.form.get('pot_size')
            price = request.form.get('price')
            cost_price = request.form.get('cost_price')
            last_detected = request.form.get('last_detected')
            notes = request.form.get('notes')
            
            # Validate the required fields
            if not supplier_id or not product_name or not price:
                flash('Please fill in all required fields', 'danger')
                suppliers_list = Supplier.query.order_by(Supplier.name).all()
                return render_template('edit_supplier_product.html', suppliers=suppliers_list, today=datetime.utcnow())
            
            try:
                # Create a new supplier product
                new_product = SupplierProduct(
                    supplier_id=supplier_id,
                    product_name=product_name,
                    scientific_name=scientific_name,
                    height=height,
                    pot_size=pot_size,
                    price=float(price),
                    cost_price=float(cost_price) if cost_price else None,
                    last_detected=datetime.strptime(last_detected, '%Y-%m-%d') if last_detected else datetime.utcnow(),
                    notes=notes
                )
                
                db.session.add(new_product)
                db.session.commit()
                
                flash('Supplier product added successfully', 'success')
                return redirect(url_for('supplier_products', supplier_id=supplier_id))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error adding supplier product: {str(e)}")
                flash(f'Error adding supplier product: {str(e)}', 'danger')
        
        # GET request - show the form
        suppliers_list = Supplier.query.order_by(Supplier.name).all()
        return render_template('edit_supplier_product.html', suppliers=suppliers_list, today=datetime.utcnow())
    
    @app.route('/edit_supplier_product/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_supplier_product(id):
        """Edit an existing supplier product"""
        from datetime import datetime
        
        product = SupplierProduct.query.get_or_404(id)
        
        if request.method == 'POST':
            try:
                product.supplier_id = request.form.get('supplier_id')
                product.product_name = request.form.get('product_name')
                product.scientific_name = request.form.get('scientific_name')
                product.height = request.form.get('height')
                product.pot_size = request.form.get('pot_size')
                product.price = float(request.form.get('price'))
                
                cost_price = request.form.get('cost_price')
                product.cost_price = float(cost_price) if cost_price and cost_price.strip() else None
                
                last_detected = request.form.get('last_detected')
                product.last_detected = datetime.strptime(last_detected, '%Y-%m-%d') if last_detected else datetime.utcnow()
                
                product.notes = request.form.get('notes')
                
                db.session.commit()
                
                flash('Supplier product updated successfully', 'success')
                return redirect(url_for('supplier_products', supplier_id=product.supplier_id))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error updating supplier product: {str(e)}")
                flash(f'Error updating supplier product: {str(e)}', 'danger')
        
        # GET request - show the form
        suppliers_list = Supplier.query.order_by(Supplier.name).all()
        return render_template('edit_supplier_product.html', product=product, suppliers=suppliers_list, today=datetime.utcnow())
    
    @app.route('/delete_supplier_product/<int:id>', methods=['POST'])
    @login_required
    def delete_supplier_product(id):
        """Delete a supplier product"""
        product = SupplierProduct.query.get_or_404(id)
        supplier_id = product.supplier_id
        
        try:
            db.session.delete(product)
            db.session.commit()
            flash('Supplier product deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting supplier product: {str(e)}")
            flash(f'Error deleting supplier product: {str(e)}', 'danger')
            
        return redirect(url_for('supplier_products', supplier_id=supplier_id))
    
    @app.route('/batch_delete_supplier_products', methods=['POST'])
    @login_required
    def batch_delete_supplier_products():
        """Delete multiple supplier products at once"""
        product_ids = request.form.getlist('product_ids')
        
        if not product_ids:
            flash('No products selected for deletion', 'warning')
            return redirect(url_for('supplier_products'))
        
        success_count = 0
        error_count = 0
        supplier_id = None
        
        for product_id in product_ids:
            try:
                product_id = int(product_id)
                product = SupplierProduct.query.get(product_id)
                
                if product:
                    # Store supplier_id for redirect (use the first one)
                    if not supplier_id:
                        supplier_id = product.supplier_id
                        
                    db.session.delete(product)
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Error deleting supplier product ID {product_id}: {str(e)}")
        
        try:
            db.session.commit()
            if success_count > 0:
                flash(f'Successfully deleted {success_count} supplier products', 'success')
            if error_count > 0:
                flash(f'Failed to delete {error_count} supplier products', 'warning')
        except Exception as e:
            db.session.rollback()
            flash(f'Error during batch delete: {str(e)}', 'danger')
        
        return redirect(url_for('supplier_products', supplier_id=supplier_id))
        
    @app.route('/generate_supplier_report', methods=['GET', 'POST'])
    @login_required
    def generate_supplier_report():
        """Generate a customized report of selected supplier products"""
        import json
        from utils.pdf_generator import generate_supplier_products_pdf
        
        # Handle GET requests for print-friendly view
        if request.method == 'GET':
            product_ids = request.args.get('product_ids')
            fields = request.args.get('fields')
            report_format = request.args.get('format', 'pdf')
            group_by_supplier = request.args.get('group_by_supplier', 'true').lower() == 'true'
            include_header = request.args.get('include_header', 'true').lower() == 'true'
            
            if not product_ids:
                flash('No products selected for the report', 'warning')
                return redirect(url_for('supplier_products'))
            
            try:
                # Parse the JSON strings
                product_ids = json.loads(product_ids)
                fields = json.loads(fields) if fields else ["product_name", "scientific_name", "height", "pot_size", "price", "cost_price", "supplier"]
                
                # Get the products
                products = SupplierProduct.query.filter(SupplierProduct.id.in_(product_ids)).all()
                
                if not products:
                    flash('No valid products found for the report', 'warning')
                    return redirect(url_for('supplier_products'))
                
                # Get company settings for the header
                company = CompanySettings.query.first() if include_header else None
                
                # Group products by supplier if requested
                if group_by_supplier:
                    suppliers_dict = {}
                    for product in products:
                        if product.supplier_id not in suppliers_dict:
                            suppliers_dict[product.supplier_id] = {
                                'supplier': product.supplier,
                                'products': []
                            }
                        suppliers_dict[product.supplier_id]['products'].append(product)
                    
                    # Sort suppliers and products
                    suppliers_list = sorted(suppliers_dict.values(), key=lambda x: x['supplier'].name)
                    for supplier in suppliers_list:
                        supplier['products'].sort(key=lambda x: x.product_name)
                else:
                    # Just sort products by name without grouping
                    products.sort(key=lambda x: x.product_name)
                    suppliers_list = None
                
                # Render the print-friendly template
                return render_template(
                    'pdf/supplier_products_print.html',
                    products=products,
                    suppliers=suppliers_list,
                    fields=fields,
                    group_by_supplier=group_by_supplier,
                    include_header=include_header,
                    company=company,
                    date_generated=datetime.now().strftime('%Y-%m-%d %H:%M'),
                    products_count=len(products),
                    suppliers_count=len(suppliers_dict) if group_by_supplier else 0
                )
                
            except Exception as e:
                logger.error(f"Error generating supplier print report: {str(e)}")
                logger.error(traceback.format_exc())
                flash(f'Error generating report: {str(e)}', 'danger')
                return redirect(url_for('supplier_products'))
        
        # Handle POST requests for PDF download
        product_ids = request.form.get('product_ids')
        fields = request.form.get('fields')
        group_by_supplier = request.form.get('group_by_supplier', 'true').lower() == 'true'
        include_header = request.form.get('include_header', 'true').lower() == 'true'
        
        if not product_ids:
            flash('No products selected for the report', 'warning')
            return redirect(url_for('supplier_products'))
        
        try:
            # Parse the JSON strings
            product_ids = json.loads(product_ids)
            fields = json.loads(fields) if fields else ["product_name", "scientific_name", "height", "pot_size", "price", "cost_price", "supplier"]
            
            # Get the products
            products = SupplierProduct.query.filter(SupplierProduct.id.in_(product_ids)).all()
            
            if not products:
                flash('No valid products found for the report', 'warning')
                return redirect(url_for('supplier_products'))
            
            # Generate the PDF with customization options
            pdf_file, filename = generate_supplier_products_pdf(
                products, 
                fields=fields,
                group_by_supplier=group_by_supplier,
                include_header=include_header
            )
            
            # Send the PDF as a download
            response = make_response(pdf_file)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating supplier report: {str(e)}")
            flash(f'Error generating report: {str(e)}', 'danger')
            return redirect(url_for('supplier_products'))
    
    @app.route('/export_supplier_catalog/<int:supplier_id>')
    @login_required
    def export_supplier_catalog(supplier_id):
        """Export a catalog of all products from a specific supplier"""
        from utils.pdf_generator import generate_supplier_catalog_pdf
        
        supplier = Supplier.query.get_or_404(supplier_id)
        products = SupplierProduct.query.filter_by(supplier_id=supplier_id).order_by(SupplierProduct.product_name).all()
        
        if not products:
            flash('No products found for this supplier', 'warning')
            return redirect(url_for('supplier_products', supplier_id=supplier_id))
        
        try:
            # Generate the PDF
            pdf_file, filename = generate_supplier_catalog_pdf(supplier, products)
            
            # Send the PDF as a download
            response = make_response(pdf_file)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating supplier catalog: {str(e)}")
            flash(f'Error generating catalog: {str(e)}', 'danger')
            return redirect(url_for('supplier_products', supplier_id=supplier_id))
            
    @app.route('/supplier_duplicates')
    @login_required
    def supplier_duplicates():
        """View potential duplicate supplier products"""
        # Get all suppliers for the dropdown
        suppliers_list = Supplier.query.order_by(Supplier.name).all()
        
        # Get supplier_id from request
        supplier_id = request.args.get('supplier_id')
        threshold = float(request.args.get('threshold', 0.9))
        
        # Show the duplicate detection page with suppliers dropdown
        if not supplier_id:
            return render_template(
                'supplier_duplicates.html',
                suppliers=suppliers_list,
                duplicates=None,
                current_supplier=None,
                threshold=threshold
            )
        
        try:
            # Convert supplier_id to int
            supplier_id = int(supplier_id)
            
            # Get the current supplier
            current_supplier = Supplier.query.get(supplier_id)
            if not current_supplier:
                flash('Supplier not found', 'danger')
                return redirect(url_for('supplier_duplicates'))
            
            # Find potential duplicates
            duplicate_pairs = find_supplier_duplicates(supplier_id, threshold)
            
            # Check if OpenAI API is configured
            openai_available = bool(os.getenv("OPENAI_API_KEY"))
            
            return render_template(
                'supplier_duplicates.html',
                suppliers=suppliers_list,
                duplicates=duplicate_pairs,
                current_supplier=current_supplier,
                threshold=threshold,
                openai_available=openai_available
            )
            
        except Exception as e:
            logger.error(f"Error finding supplier duplicates: {str(e)}")
            flash(f'Error finding duplicates: {str(e)}', 'danger')
            return redirect(url_for('supplier_duplicates'))
    
    def test_openai_api():
        """Test if OpenAI API key is valid and working"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return False, "OpenAI API key not configured"
            
        try:
            # Initialize client with basic settings
            from openai import OpenAI
            client = OpenAI(api_key=api_key, timeout=10.0)
            
            # Simple test to list available models
            models = client.models.list()
            return True, f"API connection successful. Found {len(models.data)} models."
        except Exception as e:
            logger.error(f"OpenAI API test failed: {str(e)}")
            return False, f"API connection failed: {str(e)}"
    
    @app.route('/analyze_supplier_duplicates/<supplier_id>', methods=['POST'])
    def analyze_supplier_duplicates(supplier_id):
        """Analyze potential duplicates using OpenAI"""
        # Check if OpenAI API key exists in environment variables
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OpenAI API key not configured for duplicate analysis")
            flash('OpenAI API key is not configured. Please configure it in AI Settings.', 'warning')
            return redirect(url_for('ai_settings'))
        
        try:
            # Get threshold from form or use default if not provided
            threshold = float(request.form.get('threshold', 0.9))
            if not (0 < threshold <= 1):
                flash('Threshold must be between 0 and 1', 'warning')
                return redirect(url_for('supplier_duplicates', supplier_id=supplier_id))
            
            # Convert supplier_id to integer if needed
            try:
                supplier_id = int(supplier_id)
            except ValueError:
                logger.error(f"Invalid supplier ID: {supplier_id}")
                flash('Invalid supplier ID', 'danger')
                return redirect(url_for('supplier_duplicates'))
            
            # Find potential duplicates
            duplicate_pairs = find_supplier_duplicates(supplier_id, threshold)
            
            if not duplicate_pairs:
                flash('No potential duplicates found for this supplier with the current threshold.', 'info')
                return redirect(url_for('supplier_duplicates', supplier_id=supplier_id))
            
            # Analyze duplicates with OpenAI
            analysis_results = ask_openai_for_resolution(duplicate_pairs)
            
            if not analysis_results:
                flash('Failed to analyze duplicates. Please try again.', 'warning')
                return redirect(url_for('supplier_duplicates', supplier_id=supplier_id))
            
            # Convert analysis results to a serializable format
            serializable_results = []
            for result in analysis_results:
                # Create a serializable version of each result
                serializable_result = {
                    'pair': result['pair'],
                    'product1': {
                        'id': result['product1'].id,
                        'name': result['product1'].product_name,
                        'scientific_name': result['product1'].scientific_name,
                        'pot_size': result['product1'].pot_size,
                        'height': result['product1'].height,
                        'price': result['product1'].price,
                        'cost_price': result['product1'].cost_price
                    },
                    'product2': {
                        'id': result['product2'].id,
                        'name': result['product2'].product_name,
                        'scientific_name': result['product2'].scientific_name,
                        'pot_size': result['product2'].pot_size,
                        'height': result['product2'].height,
                        'price': result['product2'].price,
                        'cost_price': result['product2'].cost_price
                    },
                    'suggestion': result['suggestion'],
                    'is_duplicate': result['is_duplicate']
                }
                serializable_results.append(serializable_result)
            
            # Store serializable results in session for the results page
            session['duplicate_analysis'] = serializable_results
            
            # Redirect to results page
            return redirect(url_for('supplier_duplicate_results', supplier_id=supplier_id))
            
        except Exception as e:
            logger.exception(f"Error analyzing supplier duplicates: {str(e)}")
            flash(f'Error analyzing duplicates: {str(e)}', 'danger')
            return redirect(url_for('supplier_duplicates', supplier_id=supplier_id))
    
    @app.route('/supplier_duplicate_results/<int:supplier_id>')
    @login_required
    def supplier_duplicate_results(supplier_id):
        """Show analysis results for potential duplicate products"""
        # Get the current supplier
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            flash('Supplier not found', 'danger')
            return redirect(url_for('supplier_duplicates'))
        
        # Get analysis results from session
        analysis_results = session.get('duplicate_analysis', [])
        
        if not analysis_results:
            flash('No analysis results found. Please run the analysis again.', 'warning')
            return redirect(url_for('supplier_duplicates', supplier_id=supplier_id))
        
        return render_template(
            'supplier_duplicate_results.html',
            supplier=supplier,
            results=analysis_results
        )
    
    @app.route('/flag_supplier_duplicates/<int:supplier_id>', methods=['POST'])
    @login_required
    def flag_supplier_duplicates(supplier_id):
        """Flag selected products as duplicates"""
        try:
            # Get selected duplicate pairs from form
            selected_pairs = request.form.getlist('duplicate_pair')
            
            if not selected_pairs:
                flash('No duplicates selected', 'warning')
                return redirect(url_for('supplier_duplicate_results', supplier_id=supplier_id))
            
            # Get analysis results from session
            all_results = session.get('duplicate_analysis', [])
            
            # Filter only selected results
            selected_results = [
                result for result in all_results
                if f"{result['pair'][0]}_{result['pair'][1]}" in selected_pairs
            ]
            
            # Flag the selected duplicates
            result = flag_duplicate_products(selected_results)
            
            # Show results
            if result['success_count'] > 0:
                flash(f"Successfully flagged {result['success_count']} products as duplicates", 'success')
            if result['error_count'] > 0:
                flash(f"Failed to flag {result['error_count']} products", 'warning')
            
            # Clear session data
            session.pop('duplicate_analysis', None)
            
            return redirect(url_for('supplier_products', supplier_id=supplier_id))
            
        except Exception as e:
            logger.error(f"Error flagging supplier duplicates: {str(e)}")
            flash(f'Error flagging duplicates: {str(e)}', 'danger')
            return redirect(url_for('supplier_duplicate_results', supplier_id=supplier_id))
    
    @app.route('/company_settings')
    @login_required
    def company_settings():
        """View and manage company settings"""
        # Get or create company settings
        company = CompanySettings.query.first()
        if not company:
            company = CompanySettings()
            db.session.add(company)
            db.session.commit()
            
        return render_template('company_settings.html', company=company)
        
    @app.route('/save_company_settings', methods=['POST'])
    @login_required
    def save_company_settings():
        """Save company settings"""
        # Get or create company settings
        company = CompanySettings.query.first()
        if not company:
            company = CompanySettings()
            db.session.add(company)
            
        # Update company details - all fields are optional
        company.name = request.form.get('name') or None
        company.address_line1 = request.form.get('address_line1') or None
        company.address_line2 = request.form.get('address_line2') or None
        company.phone = request.form.get('phone') or None
        company.email = request.form.get('email') or None
        company.pdf_orientation = request.form.get('pdf_orientation', 'portrait')  # Default to portrait if not provided
        
        # Handle logo upload if provided
        if 'logo' in request.files and request.files['logo'].filename:
            logo_file = request.files['logo']
            if logo_file and allowed_file(logo_file.filename, {'png', 'jpg', 'jpeg', 'gif', 'svg'}):
                # Generate unique filename
                filename = secure_filename(logo_file.filename)
                unique_filename = f"logo_{uuid.uuid4().hex[:8]}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                logo_file.save(file_path)
                
                # Update logo path
                company.logo_path = file_path
        
        try:
            db.session.commit()
            flash('Company settings updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating company settings: {str(e)}")
            flash(f'Error updating company settings: {str(e)}', 'danger')
            
        return redirect(url_for('company_settings'))
        
    # AI Document Insights Routes
    @app.route('/ai-insights/settings', methods=['GET', 'POST'])
    @login_required
    def ai_settings():
        """AI document insights settings page"""
        from utils.ai_document_analyzer import get_document_analyzer, reset_document_analyzer
        
        # Get the document analyzer singleton
        document_analyzer = get_document_analyzer()
        
        if request.method == 'POST':
            api_key = request.form.get('openai_api_key')
            
            if api_key:
                try:
                    # Set the API key as an environment variable
                    os.environ["OPENAI_API_KEY"] = api_key
                    
                    # Reset the document analyzer to use the new API key
                    # This will clear the singleton instance and create a new one with the updated API key
                    document_analyzer = reset_document_analyzer()
                    
                    logger.info(f"API key set and document analyzer reset successfully. Enabled status: {document_analyzer.is_enabled()}")
                    
                    if document_analyzer.is_enabled():
                        flash('OpenAI API key has been set successfully.', 'success')
                    else:
                        flash('API key was set but document analyzer is not enabled. Please check the key format.', 'warning')
                except Exception as e:
                    flash(f'Error setting API key: {str(e)}', 'danger')
                    logger.error(f"Error setting OpenAI API key: {str(e)}")
            else:
                flash('Please provide a valid API key.', 'danger')
            
            return redirect(url_for('ai_settings'))
        
        # For GET requests, show the settings page
        return render_template(
            'ai/settings.html',
            api_key_set=bool(os.getenv("OPENAI_API_KEY")),
            is_enabled=document_analyzer.is_enabled()
        )
    
    @app.route('/ai-insights/status', methods=['GET'])
    @login_required
    def ai_status():
        """Check if AI document analysis is enabled"""
        from utils.ai_document_analyzer import get_document_analyzer
        
        # Get the document analyzer singleton
        document_analyzer = get_document_analyzer()
        
        # Check if API key is set and document analyzer is enabled
        api_key_set = bool(os.getenv("OPENAI_API_KEY"))
        is_enabled = document_analyzer.is_enabled()
        
        # Log status for debugging
        logger.debug(f"AI status check - API key set: {api_key_set}, Enabled: {is_enabled}")
        
        status = {
            "enabled": is_enabled,
            "api_key_set": api_key_set
        }
        return jsonify(status)
    
    @app.route('/healthcheck', methods=['GET'])
    def healthcheck():
        """API healthcheck endpoint"""
        from services.openai_utils import openai_health_check
        return jsonify({ "openai_healthy": openai_health_check() }), 200
    
    @app.route('/test-openai-api', methods=['GET'])
    @login_required
    def test_openai_api():
        """Test if OpenAI API key is valid and working"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return jsonify({
                "success": False,
                "message": "OpenAI API key not configured. Please provide an API key."
            })
            
        try:
            # Initialize client with robust settings
            from openai import OpenAI
            client = OpenAI(api_key=api_key, timeout=30.0)
            
            try:
                # Test a simple model query first to validate API key
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Test connection"}
                    ],
                    max_tokens=10,
                    temperature=0.3,
                )
                
                # If we got here, the API key is working for completions
                logger.info("OpenAI API test successful: chat completions working")
                
                # Now try listing models as a secondary test
                models = client.models.list()
                model_count = len(models.data)
                
                logger.info(f"OpenAI API models test successful. Found {model_count} models.")
                
                return jsonify({
                    "success": True,
                    "message": f"Connection successful! Your API key is valid and working. Found {model_count} available models."
                })
                
            except Exception as model_error:
                # Even if model listing fails, if we got a completion that's good enough
                logger.warning(f"Model listing failed but completions work: {str(model_error)}")
                return jsonify({
                    "success": True, 
                    "message": "Connection successful! Your API key is valid for generating completions."
                })
                
        except Exception as e:
            error_message = str(e)
            logger.error(f"OpenAI API test failed: {error_message}")
            
            # Provide a more user-friendly error message
            user_message = "Connection failed. Please check your API key."
            if "authentication" in error_message.lower():
                user_message = "Authentication failed. Please check if your API key is correct."
            elif "timeout" in error_message.lower():
                user_message = "Connection timed out. The OpenAI service might be experiencing issues."
            elif "rate limit" in error_message.lower():
                user_message = "Rate limit exceeded. Please try again later."
            
            return jsonify({
                "success": False,
                "message": f"{user_message} Technical details: {error_message}"
            })
    
    @app.route('/ai-insights/analyze', methods=['POST'])
    @login_required
    def analyze_document():
        """Analyze a document and return insights"""
        from utils.ai_document_analyzer import get_document_analyzer
        
        # Get the document analyzer singleton
        document_analyzer = get_document_analyzer()
        
        # Check if AI is enabled before proceeding
        if not document_analyzer.is_enabled():
            logger.warning("AI document analysis requested but the feature is not enabled")
            return jsonify({
                "error": "AI document analysis is not enabled. Please add your OpenAI API key in Settings."
            }), 400
        
        try:
            data = request.json
            
            # Validate required fields
            required_fields = ['document_type', 'document_id']
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Missing required field: {field}"}), 400
            
            # Get raw content if provided
            raw_content = data.get('content')
            
            # Log the analysis request
            logger.info(f"Document analysis requested for {data['document_type']} #{data['document_id']}")
            
            # Analyze the document
            insights = document_analyzer.analyze_document(
                data['document_type'], 
                data['document_id'],
                raw_content
            )
            
            # Check if there was an error
            if insights and 'error' in insights:
                logger.warning(f"Document analysis error: {insights['error']}")
                return jsonify(insights), 400
                
            return jsonify(insights)
            
        except Exception as e:
            logger.error(f"Error in document analysis endpoint: {str(e)}")
            return jsonify({"error": f"Analysis failed: {str(e)}"}), 500
    
    @app.route('/api/price-assistant', methods=['GET'])
    @login_required
    def price_assistant():
        """Get pricing suggestions for a product based on historical data"""
        from utils.price_assistant import get_price_assistant
        
        # Get required parameters
        scientific_name = request.args.get('scientific_name')
        pot_size = request.args.get('pot_size', '')
        customer_id = request.args.get('customer_id')
        
        # Validate parameters
        if not scientific_name:
            return jsonify({"error": "Scientific name is required"}), 400
        if not customer_id:
            return jsonify({"error": "Customer ID is required"}), 400
            
        try:
            customer_id = int(customer_id)
        except ValueError:
            return jsonify({"error": "Invalid customer ID"}), 400
            
        # Get price assistant
        price_assistant = get_price_assistant()
        
        # Get price history
        result = price_assistant.get_price_history(
            scientific_name=scientific_name,
            pot_size=pot_size,
            customer_id=customer_id
        )
        
        return jsonify(result)
    
    @app.route('/viber-settings', methods=['GET'])
    @login_required
    def viber_settings():
        """
        View and manage Viber integration settings
        """
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('dashboard'))
            
        # Get all suppliers for the mapping dropdown
        suppliers = Supplier.query.order_by(Supplier.name).all()
        
        # Check if Viber bot is configured
        from viber_integration import VIBER_AUTH_TOKEN, VIBER_SUPPLIER_MAPPING
        
        is_configured = bool(VIBER_AUTH_TOKEN)
        
        return render_template(
            'viber_settings.html',
            is_configured=is_configured,
            suppliers=suppliers,
            supplier_mapping=VIBER_SUPPLIER_MAPPING
        )
        
    @app.route('/viber-set-webhook', methods=['GET'])
    @login_required
    def viber_set_webhook():
        """
        Set the Viber webhook URL
        """
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('dashboard'))
            
        # Import the viber integration functions
        try:
            import requests
            # Get the current host for the webhook URL
            host = request.host_url.rstrip('/')
            webhook_url = f"{host}/viber-webhook"
            
            # Call the viber_integration module's set_webhook function directly
            from viber_integration import viber_bot
            if viber_bot:
                # Set the webhook directly through the Viber API
                result = viber_bot.set_webhook(webhook_url)
                if isinstance(result, dict) and result.get('status') == 0:
                    flash('Webhook set successfully to: ' + webhook_url, 'success')
                else:
                    flash(f'Error setting webhook: {result.get("status_message", "Unknown error")}', 'danger')
            else:
                flash('Viber bot is not configured. Please add VIBER_AUTH_TOKEN to your environment variables.', 'warning')
        except Exception as e:
            logger.error(f"Error setting Viber webhook: {str(e)}")
            flash(f'Error setting webhook: {str(e)}', 'danger')
            
        return redirect(url_for('viber_settings'))
        
    @app.route('/viber-update-mapping', methods=['POST'])
    @login_required
    def update_viber_mapping():
        """
        Update the mapping between Viber IDs and suppliers
        """
        if not current_user.is_admin:
            return jsonify({"status": "error", "message": "Unauthorized"}), 403
            
        try:
            data = request.json
            if not data or not isinstance(data, dict):
                return jsonify({"status": "error", "message": "Invalid data format"}), 400
                
            # Update the VIBER_SUPPLIER_MAPPING in the viber_integration module directly
            from viber_integration import VIBER_SUPPLIER_MAPPING
            
            # Update the global mapping in the module
            for viber_id, supplier_id in data.items():
                VIBER_SUPPLIER_MAPPING[viber_id] = supplier_id
                
            # Return success response
            response = jsonify({"status": "success", "mapping": VIBER_SUPPLIER_MAPPING})
            
            return response
        except Exception as e:
            logger.error(f"Error updating Viber mapping: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route('/viber-docs', methods=['GET'])
    @login_required
    def viber_docs():
        """
        View documentation for the Viber integration
        """
        return render_template('viber_integration_docs.html')
        
    # AI Insights Feedback API Routes
    @app.route('/api/feedback/submit', methods=['POST'])
    @login_required
    def submit_feedback():
        """Submit user feedback for AI-generated insights"""
        start_time = time.time()
        
        try:
            data = request.json
            
            # Validate required fields
            required_fields = ['document_type', 'document_id', 'rating']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'status': 'error', 
                        'message': f'Missing required field: {field}'
                    }), 400
            
            # Get feedback collector
            feedback_collector = get_feedback_collector()
            
            # Extract data
            document_type = data['document_type']
            document_id = data['document_id']
            rating = data['rating']
            comment = data.get('comment')
            insight_type = data.get('insight_type')
            user_id = current_user.id
            
            # Record feedback
            success = feedback_collector.add_feedback(
                document_type=document_type,
                document_id=document_id,
                user_id=user_id,
                rating=rating,
                comment=comment,
                insight_type=insight_type
            )
            
            # Calculate and log API request timing
            duration_ms = round((time.time() - start_time) * 1000, 2)
            log_api_request(
                endpoint='/api/feedback/submit',
                method='POST',
                status_code=200 if success else 500,
                duration_ms=duration_ms,
                user_id=user_id,
                document_type=document_type,
                document_id=document_id
            )
            
            if success:
                return jsonify({
                    'status': 'success',
                    'message': 'Feedback recorded successfully'
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to record feedback'
                }), 500
                
        except Exception as e:
            # Log the error with context
            log_with_context(
                'error',
                f"Error recording feedback: {str(e)}",
                traceback=traceback.format_exc()
            )
            
            return jsonify({
                'status': 'error',
                'message': f'Error recording feedback: {str(e)}'
            }), 500
    
    @app.route('/api/feedback/stats', methods=['GET'])
    @login_required
    def get_feedback_stats():
        """Get statistics on collected AI insights feedback"""
        start_time = time.time()
        
        try:
            # Get optional filters from query parameters
            document_type = request.args.get('document_type')
            days = request.args.get('days', 30)
            
            try:
                days = int(days)
            except ValueError:
                days = 30  # Default to 30 days if invalid
            
            # Get feedback collector
            feedback_collector = get_feedback_collector()
            
            # Get statistics
            stats = feedback_collector.get_feedback_stats(
                document_type=document_type,
                days=days
            )
            
            # Calculate and log API request timing
            duration_ms = round((time.time() - start_time) * 1000, 2)
            log_api_request(
                endpoint='/api/feedback/stats',
                method='GET',
                status_code=200,
                duration_ms=duration_ms,
                user_id=current_user.id,
                document_type=document_type,
                days=days
            )
            
            return jsonify({
                'status': 'success',
                'data': stats
            })
            
        except Exception as e:
            # Log the error with context
            log_with_context(
                'error',
                f"Error getting feedback stats: {str(e)}",
                traceback=traceback.format_exc()
            )
            
            return jsonify({
                'status': 'error',
                'message': f'Error getting feedback stats: {str(e)}'
            }), 500
    
    @app.route('/api/feedback/recent', methods=['GET'])
    @login_required
    def get_recent_feedback():
        """Get recent feedback entries for AI insights"""
        start_time = time.time()
        
        try:
            # Get optional filters from query parameters
            document_type = request.args.get('document_type')
            limit = request.args.get('limit', 10)
            
            try:
                limit = int(limit)
            except ValueError:
                limit = 10  # Default to 10 if invalid
            
            # Get feedback collector
            feedback_collector = get_feedback_collector()
            
            # Get recent entries
            entries = feedback_collector.get_recent_feedback(
                limit=limit,
                document_type=document_type
            )
            
            # Calculate and log API request timing
            duration_ms = round((time.time() - start_time) * 1000, 2)
            log_api_request(
                endpoint='/api/feedback/recent',
                method='GET',
                status_code=200,
                duration_ms=duration_ms,
                user_id=current_user.id,
                document_type=document_type,
                limit=limit
            )
            
            return jsonify({
                'status': 'success',
                'data': entries
            })
            
        except Exception as e:
            # Log the error with context
            log_with_context(
                'error',
                f"Error getting recent feedback: {str(e)}",
                traceback=traceback.format_exc()
            )
            
            return jsonify({
                'status': 'error',
                'message': f'Error getting recent feedback: {str(e)}'
            }), 500
            
    # AI Insights UI Feedback Page
    @app.route('/ai-insights/feedback', methods=['GET'])
    @login_required
    def ai_insights_feedback_dashboard():
        """Display the AI insights feedback dashboard"""
        # Get feedback collector
        feedback_collector = get_feedback_collector()
        
        # Get stats and recent entries
        stats = feedback_collector.get_feedback_stats()
        recent_entries = feedback_collector.get_recent_feedback(limit=10)
        
        return render_template(
            'ai_insights_feedback.html', 
            stats=stats,
            recent_entries=recent_entries
        )
