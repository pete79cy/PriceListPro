import os
import uuid
import traceback
from datetime import datetime
from flask import render_template, request, redirect, url_for, jsonify, flash, send_from_directory
from werkzeug.utils import secure_filename
from app import db
from models import Customer, Product, PriceList, Invoice, InvoiceItem, FileUpload
from utils.excel_parser import parse_excel_file
from utils.pdf_parser import extract_text_from_pdf, extract_invoice_data
from utils.search import search_price_list
from utils.logger import logger
from utils.excel_template import ensure_template_exists

# Log that routes module was loaded
logger.info("Routes module loaded")

def register_routes(app):
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Helper function to check allowed file extensions
    def allowed_file(filename, extensions):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions
    
    @app.route('/')
    def index():
        # Get some stats for the dashboard
        stats = {
            'customers': Customer.query.count(),
            'products': Product.query.count(),
            'price_lists': PriceList.query.count(),
            'invoices': Invoice.query.count()
        }
        return render_template('index.html', stats=stats)
    
    @app.route('/uploads', methods=['GET'])
    def uploads():
        customers = Customer.query.all()
        recent_uploads = FileUpload.query.order_by(FileUpload.upload_date.desc()).limit(10).all()
        return render_template('uploads.html', customers=customers, recent_uploads=recent_uploads)
    
    @app.route('/upload/excel', methods=['POST'])
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
                
                # Add invoice items
                for item in invoice_data.get('items', []):
                    # Try to find product by name, scientific name, or description
                    product = None
                    
                    # If scientific name is available in the item data
                    if item.get('scientific_name'):
                        product = Product.query.filter(
                            Product.scientific_name.ilike(f"%{item['scientific_name']}%")
                        ).first()
                    
                    # If not found by scientific name, try by regular name
                    if not product:
                        product = Product.query.filter(
                            Product.name.ilike(f"%{item['description']}%")
                        ).first()
                        
                    # If product is found, check if pot size matches if available
                    if product and item.get('pot_size') and product.pot:
                        if item['pot_size'].lower() not in product.pot.lower():
                            # Try to find a better match with matching pot size
                            better_match = Product.query.filter(
                                Product.name.ilike(f"%{item['description']}%"),
                                Product.pot.ilike(f"%{item['pot_size']}%")
                            ).first()
                            if better_match:
                                product = better_match
                    
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
                
                # Update upload record
                upload.processed = True
                upload.processing_notes = f"Successfully processed. Created invoice #{invoice.invoice_number} with {len(invoice_data.get('items', []))} items."
                db.session.commit()
                
                flash(f'Successfully uploaded and processed: {filename}. Created invoice #{invoice.invoice_number}.', 'success')
            except Exception as e:
                upload.processing_notes = f"Error processing file: {str(e)}"
                db.session.commit()
                flash(f'Error processing file: {str(e)}', 'danger')
            
            return redirect(url_for('uploads'))
        
        flash('Invalid file type. Please upload PDF files only.', 'danger')
        return redirect(request.url)
    
    @app.route('/customers', methods=['GET', 'POST'])
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
    def delete_customer(customer_id):
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        flash(f'Customer {customer.name} deleted successfully!', 'success')
        return redirect(url_for('customers'))
    
    @app.route('/products', methods=['GET', 'POST'])
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
    def delete_product(product_id):
        product = Product.query.get_or_404(product_id)
        # Delete associated price list entries first
        PriceList.query.filter_by(product_id=product_id).delete()
        # Then delete the product
        db.session.delete(product)
        db.session.commit()
        flash(f'Product {product.name} deleted successfully!', 'success')
        return redirect(url_for('products'))

    @app.route('/products/batch-delete', methods=['POST'])
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
    def search():
        customers = Customer.query.all()
        return render_template('search.html', customers=customers)
    
    @app.route('/api/search', methods=['GET'])
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
    def download_template():
        """Provide a downloadable Excel template for price lists"""
        template_path = ensure_template_exists(app.static_folder)
        return send_from_directory(os.path.dirname(template_path), os.path.basename(template_path), 
                                 as_attachment=True, download_name="price_list_template.xlsx")
    
    @app.route('/price-lists')
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
    
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        
    @app.route('/test-encoding', methods=['GET', 'POST'])
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
