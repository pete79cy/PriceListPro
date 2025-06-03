/**
 * Enhanced Daily Orders Management
 * Provides smart product search, customer-specific pricing, and VAT functionality
 */

class EnhancedOrderManager {
    constructor() {
        this.currentOrder = null;
        this.currentCustomerId = null;
        this.orderItems = [];
        this.searchTimeout = null;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadExistingItems();
        this.updateOrderSummary();
    }
    
    bindEvents() {
        // Customer selection
        $('#customerSelect').on('change', (e) => {
            this.currentCustomerId = parseInt(e.target.value) || null;
            this.clearSearch();
        });
        
        // Product search
        $('#productSearch').on('input', (e) => {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                this.searchProducts(e.target.value);
            }, 300);
        });
        
        // Manual add button
        $('#manualAddBtn').on('click', () => {
            this.showManualEntryForm();
        });
        
        // Item edit modal events
        $('#saveItemChanges').on('click', () => {
            this.saveItemChanges();
        });
        
        // Form submission
        $('#orderForm').on('submit', (e) => {
            e.preventDefault();
            this.saveOrder();
        });
        
        // Make items sortable
        this.initSortable();
    }
    
    initSortable() {
        $('#orderItems').sortable({
            handle: '.drag-handle',
            placeholder: 'sortable-placeholder',
            update: () => {
                this.updateItemPositions();
            }
        });
    }
    
    searchProducts(query) {
        if (!query || query.length < 2) {
            $('#searchResults').html('');
            return;
        }
        
        if (!this.currentCustomerId) {
            $('#searchResults').html(
                '<div class="alert alert-warning">Please select a customer first</div>'
            );
            return;
        }
        
        $.get('/orders/api/search/products', {
            q: query,
            customer_id: this.currentCustomerId,
            limit: 10
        })
        .done((results) => {
            this.displaySearchResults(results);
        })
        .fail((xhr) => {
            console.error('Search API failed:', xhr);
            $('#searchResults').html(
                `<div class="alert alert-danger">Search failed (${xhr.status}): ${xhr.statusText || 'Please try again'}</div>`
            );
        });
    }
    
    displaySearchResults(results) {
        if (results.length === 0) {
            $('#searchResults').html(
                '<div class="alert alert-info">No products found</div>'
            );
            return;
        }
        
        let html = '<div class="list-group mt-2">';
        
        results.forEach(product => {
            const priceDisplay = product.has_customer_price 
                ? `€${product.price.toFixed(2)} <small class="text-success">(Customer Price)</small>`
                : `€${product.price.toFixed(2)} <small class="text-muted">(Default)</small>`;
                
            const typeIcon = product.type === 'supplier_product' 
                ? '<i class="fas fa-truck text-info"></i>' 
                : '<i class="fas fa-seedling text-success"></i>';
            
            html += `
                <div class="list-group-item list-group-item-action search-result-item" 
                     data-product='${JSON.stringify(product)}'>
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <div class="d-flex align-items-center">
                                ${typeIcon}
                                <strong class="ms-2">${product.name}</strong>
                                ${product.sku ? `<span class="badge bg-secondary ms-2">${product.sku}</span>` : ''}
                            </div>
                            <div class="text-muted small">
                                ${product.scientific_name}
                                ${product.pot ? `• ${product.pot}` : ''}
                                ${product.category ? `• ${product.category}` : ''}
                            </div>
                            ${product.description ? `<div class="text-muted small">${product.description}</div>` : ''}
                        </div>
                        <div class="text-end">
                            <div class="fw-bold">${priceDisplay}</div>
                            <button class="btn btn-sm btn-primary add-product-btn">
                                <i class="fas fa-plus"></i> Add
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        $('#searchResults').html(html);
        
        // Bind click events
        $('.add-product-btn').on('click', (e) => {
            e.stopPropagation();
            const productData = JSON.parse($(e.target).closest('.search-result-item').attr('data-product'));
            this.addProductToOrder(productData);
        });
    }
    
    addProductToOrder(product, quantity = 1) {
        const item = {
            id: 'temp_' + Date.now(),
            product_id: product.type === 'product' ? product.id : null,
            price_list_id: product.price_list_id,
            plant_name: product.name,
            size: product.pot || '',
            quantity: quantity,
            price: product.price,
            vat_rate: 19.0, // Default VAT rate
            notes: '',
            is_new: true,
            product_data: product
        };
        
        this.orderItems.push(item);
        this.renderOrderItems();
        this.updateOrderSummary();
        this.clearSearch();
        
        // Show success message
        this.showToast('Product added to order', 'success');
    }
    
    showManualEntryForm() {
        const item = {
            id: 'temp_' + Date.now(),
            product_id: null,
            price_list_id: null,
            plant_name: '',
            size: '',
            quantity: 1,
            price: 0,
            vat_rate: 19.0,
            notes: '',
            is_new: true,
            is_manual: true
        };
        
        this.orderItems.push(item);
        this.renderOrderItems();
        
        // Focus on the new item for editing
        setTimeout(() => {
            $(`.order-item[data-item-id="${item.id}"] .plant-name-input`).focus();
        }, 100);
    }
    
    renderOrderItems() {
        const container = $('#orderItems');
        
        if (this.orderItems.length === 0) {
            container.html(`
                <div class="text-center text-muted py-4" id="emptyItemsMessage">
                    <i class="fas fa-seedling fa-3x mb-3 opacity-50"></i>
                    <p>No items added yet. Use the search above to add products.</p>
                </div>
            `);
            return;
        }
        
        $('#emptyItemsMessage').remove();
        
        let html = '';
        this.orderItems.forEach((item, index) => {
            html += this.renderOrderItem(item, index);
        });
        
        container.html(html);
        this.bindItemEvents();
    }
    
    renderOrderItem(item, index) {
        const total = (item.quantity * item.price).toFixed(2);
        const vatAmount = (total * (item.vat_rate / 100)).toFixed(2);
        
        const priceListBadge = item.price_list_id 
            ? '<span class="badge bg-success ms-1" title="Customer-specific price">Custom Price</span>'
            : '';
            
        const supplierBadge = item.product_data && item.product_data.type === 'supplier_product'
            ? `<span class="badge bg-info ms-1">${item.product_data.supplier_name}</span>`
            : '';
        
        return `
            <div class="order-item card mb-2" data-item-id="${item.id}">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-1">
                            <div class="drag-handle text-muted" style="cursor: move;">
                                <i class="fas fa-grip-vertical"></i>
                            </div>
                        </div>
                        
                        <div class="col-4">
                            <div class="fw-bold">
                                ${item.is_manual || item.is_new ? 
                                    `<input type="text" class="form-control form-control-sm plant-name-input" 
                                            value="${item.plant_name}" placeholder="Plant name">` :
                                    item.plant_name
                                }
                                ${priceListBadge}
                                ${supplierBadge}
                            </div>
                            <div class="text-muted small">
                                ${item.is_manual || item.is_new ? 
                                    `<input type="text" class="form-control form-control-sm size-input" 
                                            value="${item.size}" placeholder="Size/pot">` :
                                    item.size
                                }
                            </div>
                        </div>
                        
                        <div class="col-2">
                            <div class="input-group input-group-sm">
                                <input type="number" class="form-control quantity-input" 
                                       value="${item.quantity}" min="1">
                                <span class="input-group-text">pcs</span>
                            </div>
                        </div>
                        
                        <div class="col-2">
                            <div class="input-group input-group-sm">
                                <span class="input-group-text">€</span>
                                <input type="number" class="form-control price-input" 
                                       value="${item.price.toFixed(2)}" step="0.01" min="0">
                            </div>
                        </div>
                        
                        <div class="col-1">
                            <select class="form-select form-select-sm vat-rate-input">
                                <option value="5" ${item.vat_rate == 5 ? 'selected' : ''}>5%</option>
                                <option value="19" ${item.vat_rate == 19 ? 'selected' : ''}>19%</option>
                                <option value="0" ${item.vat_rate == 0 ? 'selected' : ''}>0%</option>
                            </select>
                        </div>
                        
                        <div class="col-1 text-end">
                            <div class="fw-bold">€${total}</div>
                            <div class="text-muted small">+€${vatAmount}</div>
                        </div>
                        
                        <div class="col-1 text-end">
                            <div class="btn-group btn-group-sm">
                                <button type="button" class="btn btn-outline-primary edit-item-btn" 
                                        title="Edit item">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button type="button" class="btn btn-outline-danger delete-item-btn" 
                                        title="Delete item">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    ${item.notes ? `
                        <div class="row mt-2">
                            <div class="col-12">
                                <small class="text-muted">
                                    <i class="fas fa-comment"></i> ${item.notes}
                                </small>
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    bindItemEvents() {
        // Input changes
        $('.order-item').off('input change').on('input change', '.plant-name-input, .size-input, .quantity-input, .price-input, .vat-rate-input', (e) => {
            const itemId = $(e.target).closest('.order-item').data('item-id');
            this.updateItemFromInput(itemId, e.target);
        });
        
        // Edit button
        $('.edit-item-btn').off('click').on('click', (e) => {
            const itemId = $(e.target).closest('.order-item').data('item-id');
            this.editItem(itemId);
        });
        
        // Delete button
        $('.delete-item-btn').off('click').on('click', (e) => {
            const itemId = $(e.target).closest('.order-item').data('item-id');
            this.deleteItem(itemId);
        });
    }
    
    updateItemFromInput(itemId, input) {
        const item = this.orderItems.find(i => i.id == itemId);
        if (!item) return;
        
        const $input = $(input);
        const field = $input.attr('class').split('-')[0]; // Get field name from class
        
        switch (field) {
            case 'plant':
                item.plant_name = $input.val();
                break;
            case 'size':
                item.size = $input.val();
                break;
            case 'quantity':
                item.quantity = parseInt($input.val()) || 1;
                break;
            case 'price':
                item.price = parseFloat($input.val()) || 0;
                break;
            case 'vat':
                item.vat_rate = parseFloat($input.val()) || 19;
                break;
        }
        
        // Update display if needed
        if (field === 'quantity' || field === 'price' || field === 'vat') {
            const $item = $(`.order-item[data-item-id="${itemId}"]`);
            const total = (item.quantity * item.price).toFixed(2);
            const vatAmount = (total * (item.vat_rate / 100)).toFixed(2);
            
            $item.find('.col-1:nth-last-child(2)').html(`
                <div class="fw-bold">€${total}</div>
                <div class="text-muted small">+€${vatAmount}</div>
            `);
            
            this.updateOrderSummary();
        }
    }
    
    editItem(itemId) {
        const item = this.orderItems.find(i => i.id == itemId);
        if (!item) return;
        
        // Populate modal
        $('#editItemId').val(itemId);
        $('#editPlantName').val(item.plant_name);
        $('#editSize').val(item.size);
        $('#editQuantity').val(item.quantity);
        $('#editPrice').val(item.price);
        $('#editVatRate').val(item.vat_rate);
        $('#editNotes').val(item.notes);
        $('#editUpdatePriceList').prop('checked', false);
        
        // Show modal
        new bootstrap.Modal(document.getElementById('itemEditModal')).show();
    }
    
    saveItemChanges() {
        const itemId = $('#editItemId').val();
        const item = this.orderItems.find(i => i.id == itemId);
        if (!item) return;
        
        // Update item
        item.plant_name = $('#editPlantName').val();
        item.size = $('#editSize').val();
        item.quantity = parseInt($('#editQuantity').val()) || 1;
        item.price = parseFloat($('#editPrice').val()) || 0;
        item.vat_rate = parseFloat($('#editVatRate').val()) || 19;
        item.notes = $('#editNotes').val();
        item.update_price_list = $('#editUpdatePriceList').is(':checked');
        
        // Re-render items and update summary
        this.renderOrderItems();
        this.updateOrderSummary();
        
        // Close modal
        bootstrap.Modal.getInstance(document.getElementById('itemEditModal')).hide();
        
        this.showToast('Item updated', 'success');
    }
    
    deleteItem(itemId) {
        if (!confirm('Are you sure you want to delete this item?')) return;
        
        this.orderItems = this.orderItems.filter(i => i.id != itemId);
        this.renderOrderItems();
        this.updateOrderSummary();
        
        this.showToast('Item deleted', 'info');
    }
    
    updateOrderSummary() {
        let totalItems = 0;
        let subtotal = 0;
        let vat19Total = 0;
        let vat5Total = 0;
        
        this.orderItems.forEach(item => {
            totalItems += item.quantity;
            const itemTotal = item.quantity * item.price;
            subtotal += itemTotal;
            
            const vatAmount = itemTotal * (item.vat_rate / 100);
            if (item.vat_rate === 19) {
                vat19Total += vatAmount;
            } else if (item.vat_rate === 5) {
                vat5Total += vatAmount;
            }
        });
        
        const totalAmount = subtotal + vat19Total + vat5Total;
        
        $('#totalItems').text(totalItems);
        $('#subtotal').text(`€${subtotal.toFixed(2)}`);
        $('#vat19').text(`€${vat19Total.toFixed(2)}`);
        $('#vat5').text(`€${vat5Total.toFixed(2)}`);
        $('#totalAmount').text(`€${totalAmount.toFixed(2)}`);
    }
    
    loadExistingItems() {
        // Load items if editing existing order
        const orderId = window.location.pathname.match(/\/orders\/(\d+)\/edit/);
        if (orderId) {
            this.currentOrder = parseInt(orderId[1]);
            this.loadOrderItems();
        }
    }
    
    loadOrderItems() {
        if (!this.currentOrder) return;
        
        $.get(`/orders/api/orders/${this.currentOrder}/items`)
        .done((data) => {
            this.orderItems = data.items.map(item => ({
                ...item,
                is_new: false,
                is_manual: false
            }));
            this.renderOrderItems();
            this.updateOrderSummary();
        })
        .fail(() => {
            this.showToast('Failed to load order items', 'error');
        });
    }
    
    saveOrder() {
        // Collect form data
        const formData = new FormData(document.getElementById('orderForm'));
        
        // Add items data
        formData.append('items', JSON.stringify(this.orderItems));
        
        // Submit form
        const url = this.currentOrder 
            ? `/orders/${this.currentOrder}/edit`
            : '/orders/new';
            
        fetch(url, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                window.location.href = '/orders/';
            } else {
                throw new Error('Save failed');
            }
        })
        .catch(() => {
            this.showToast('Failed to save order', 'error');
        });
    }
    
    clearSearch() {
        $('#productSearch').val('');
        $('#searchResults').html('');
    }
    
    updateItemPositions() {
        // Update order positions based on DOM order
        const newOrder = [];
        $('.order-item').each((index, element) => {
            const itemId = $(element).data('item-id');
            const item = this.orderItems.find(i => i.id == itemId);
            if (item) {
                newOrder.push(item);
            }
        });
        this.orderItems = newOrder;
    }
    
    showToast(message, type = 'info') {
        // Simple toast notification
        const toastClass = {
            'success': 'alert-success',
            'error': 'alert-danger',
            'info': 'alert-info'
        }[type] || 'alert-info';
        
        const toast = $(`
            <div class="alert ${toastClass} alert-dismissible fade show position-fixed" 
                 style="top: 20px; right: 20px; z-index: 9999;">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `);
        
        $('body').append(toast);
        
        setTimeout(() => {
            toast.alert('close');
        }, 3000);
    }
}

// Initialize when document is ready
$(document).ready(() => {
    new EnhancedOrderManager();
});