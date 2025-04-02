import os
import uuid
import traceback
from datetime import datetime
from flask import render_template, request, redirect, url_for, jsonify, flash, send_from_directory, session
from werkzeug.utils import secure_filename
from app import db
from models import User, Customer, Product, PriceList, Invoice, InvoiceItem, FileUpload, ProductUpdateRequest
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from utils.excel_parser import parse_excel_file
from utils.pdf_parser import extract_text_from_pdf, extract_invoice_data
from utils.search import search_price_list
from utils.logger import logger
from utils.excel_template import ensure_template_exists
from utils.product_management import approve_price_update, reject_price_update

# Log that routes module was loaded
logger.info("Routes module loaded")

def register_routes(app):
    
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
            # Get some stats for the dashboard
            pending_update_count = ProductUpdateRequest.query.filter_by(status='Pending').count()
            
            stats = {
                'customers': Customer.query.count(),
                'products': Product.query.count(),
                'price_lists': PriceList.query.count(),
                'invoices': Invoice.query.count(),
                'pending_updates': pending_update_count
            }
            return render_template('dashboard.html', stats=stats, pending_update_count=pending_update_count)
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
        # Get some stats for the dashboard
        pending_update_count = ProductUpdateRequest.query.filter_by(status='Pending').count()
        
        stats = {
            'customers': Customer.query.count(),
            'products': Product.query.count(),
            'price_lists': PriceList.query.count(),
            'invoices': Invoice.query.count(),
            'pending_updates': pending_update_count
        }
        return render_template('dashboard.html', stats=stats, pending_update_count=pending_update_count)
    
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
            
            if customer_id:  # Update existing
                customer = Customer.query.get_or_404(customer_id)
                customer.name = name
                customer.email = email
                customer.phone = phone
                customer.address = address
                flash(f'Customer {name} updated successfully!', 'success')
            else:  # Create new
                customer = Customer(name=name, email=email, phone=phone, address=address)
                db.session.add(customer)
                flash(f'Customer {name} added successfully!', 'success')
            
            db.session.commit()
            return redirect(url_for('customers'))
        
        # GET request - show customers
        customers_list = Customer.query.all()
        return render_template('customers.html', customers=customers_list)
    
    @app.route('/customers/<int:customer_id>/delete', methods=['POST'])
    @login_required
    def delete_customer(customer_id):
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        flash(f'Customer {customer.name} deleted successfully!', 'success')
        return redirect(url_for('customers'))
    
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
    
    @app.route('/download/template')
    @login_required
    def download_template():
        """Provide a downloadable Excel template for price lists"""
        template_path = ensure_template_exists(app.static_folder)
        return send_from_directory(os.path.dirname(template_path), os.path.basename(template_path), 
                                 as_attachment=True, download_name="price_list_template.xlsx")
    
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
        
        # Get all unique categories for filter dropdown
        categories = db.session.query(Product.category).filter(Product.category != None, Product.category != '').distinct().order_by(Product.category).all()
        categories = [c[0] for c in categories]  # Extract the category names
        
        return render_template('price_lists.html', 
                              price_lists=price_lists, 
                              customers=customers,
                              categories=categories,
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
