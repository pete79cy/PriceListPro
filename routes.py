import os
import uuid
from datetime import datetime
from flask import render_template, request, redirect, url_for, jsonify, flash, send_from_directory
from werkzeug.utils import secure_filename
from app import db
from models import Customer, Product, PriceList, Invoice, InvoiceItem, FileUpload
from utils.excel_parser import parse_excel_file
from utils.pdf_parser import extract_text_from_pdf, extract_invoice_data
from utils.search import search_price_list

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
                # Process the excel file
                result = parse_excel_file(file_path, customer_id, upload.id)
                
                # Update upload record
                upload.processed = True
                upload.processing_notes = f"Successfully processed. Added {result['new_products']} products and {result['price_entries']} price list entries."
                db.session.commit()
                
                flash(f'Successfully uploaded and processed: {filename}. Added {result["new_products"]} products and {result["price_entries"]} price list entries.', 'success')
            except Exception as e:
                upload.processing_notes = f"Error processing file: {str(e)}"
                db.session.commit()
                flash(f'Error processing file: {str(e)}', 'danger')
            
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
                    file_path=unique_filename
                )
                db.session.add(invoice)
                db.session.commit()
                
                # Add invoice items
                for item in invoice_data.get('items', []):
                    # Try to find product by name or description
                    product = Product.query.filter(
                        Product.name.ilike(f"%{item['description']}%")
                    ).first()
                    
                    invoice_item = InvoiceItem(
                        invoice_id=invoice.id,
                        product_id=product.id if product else None,
                        description=item['description'],
                        quantity=item.get('quantity', 1),
                        price=item.get('price', 0),
                        vat=item.get('vat', 0),
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
            sku = request.form.get('sku')
            description = request.form.get('description')
            
            if product_id:  # Update existing
                product = Product.query.get_or_404(product_id)
                product.name = name
                product.sku = sku
                product.description = description
                flash(f'Product {name} updated successfully!', 'success')
            else:  # Create new
                product = Product(name=name, sku=sku, description=description)
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
        db.session.delete(product)
        db.session.commit()
        flash(f'Product {product.name} deleted successfully!', 'success')
        return redirect(url_for('products'))
    
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
    
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
