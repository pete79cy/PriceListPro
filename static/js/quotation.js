/**
 * Quotation management JavaScript functions
 */

// Initialize edit buttons on document load
document.addEventListener('DOMContentLoaded', function() {
    // Setup the supplier dropdown event handlers
    setupSupplierDropdowns();
    
    // Setup AJAX form submission for edit item form
    setupAjaxFormSubmission();
    
    var editButtons = document.querySelectorAll('.edit-item-btn');
    editButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var id = this.getAttribute('data-id');
            var description = this.getAttribute('data-description');
            var scientificName = this.getAttribute('data-scientific-name');
            var potSize = this.getAttribute('data-pot-size');
            var height = this.getAttribute('data-height');
            var quantity = this.getAttribute('data-quantity');
            var sellingPrice = this.getAttribute('data-selling-price');
            var vatRate = this.getAttribute('data-vat-rate');
            var supplier = this.getAttribute('data-supplier');
            var costPrice = this.getAttribute('data-cost-price');
            var supplierId = this.getAttribute('data-supplier-id');
            
            // Store the item ID for later use (highlighting)
            document.getElementById('editItemForm').setAttribute('data-item-id', id);
            
            // Set form action URL
            var quotationId = document.getElementById('quotation-id').value;
            document.getElementById('editItemForm').action = "/quotation/" + quotationId + "/item/" + id;
            
            // Fill the form fields with the item data
            document.getElementById('edit_description').value = description;
            document.getElementById('edit_scientific_name').value = scientificName;
            document.getElementById('edit_pot_size').value = potSize;
            document.getElementById('edit_height').value = height;
            document.getElementById('edit_quantity').value = quantity;
            document.getElementById('edit_selling_price').value = sellingPrice;
            document.getElementById('edit_vat_rate').value = vatRate;
            document.getElementById('edit_supplier').value = supplier;
            document.getElementById('edit_cost_price').value = costPrice;
            
            // Handle supplier selection
            var supplierIdSelect = document.getElementById('edit_supplier_id');
            if (supplierIdSelect) {
                if (supplierId) {
                    supplierIdSelect.value = supplierId;
                } else {
                    supplierIdSelect.value = "";
                }
                
                // If supplier exists but not in dropdown, select "custom" option
                if (supplier && !supplierId) {
                    document.getElementById('edit_manual_supplier_container').classList.remove('d-none');
                }
            }
            
            // Show the modal
            var editModal = new bootstrap.Modal(document.getElementById('editItemModal'));
            editModal.show();
        });
    });
});

// Setup AJAX form submission
function setupAjaxFormSubmission() {
    const editItemForm = document.getElementById('editItemForm');
    if (editItemForm) {
        editItemForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const itemId = this.getAttribute('data-item-id');
            const formData = new FormData(this);
            
            // Show processing indicator
            const submitBtn = document.querySelector('#editItemModal .btn-primary');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
            submitBtn.disabled = true;
            
            // Create a function to reset button state that we can call in multiple places
            const resetButton = function() {
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
            };
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                
                // First get the response as text
                return response.text().then(text => {
                    try {
                        // Try to parse the text as JSON
                        return JSON.parse(text);
                    } catch (err) {
                        console.error('Error parsing JSON:', err);
                        console.log('Raw response:', text);
                        throw new Error('Error parsing server response. Please try again.');
                    }
                });
            })
            .then(data => {
                if (!data || !data.success) {
                    throw new Error(data?.error || 'Unknown server error');
                }
                
                // Close the modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('editItemModal'));
                modal.hide();
                
                // Show success message
                showToast(data.message || 'Item updated successfully!', 'success');
                
                // Update the item in the table without reloading the page
                if (data.item) {
                    updateItemInTable(itemId, data.item);
                    
                    // Highlight the updated row
                    highlightRow(itemId);
                } else {
                    console.warn('Server response missing item data');
                    // Fallback to page reload if item data is missing
                    window.location.reload();
                }
                
                // Reset button state on success too
                resetButton();
            })
            .catch(error => {
                console.error('Error:', error);
                
                // Create a more user-friendly message for database errors
                let errorMessage = error.message;
                if (errorMessage.includes('SSL connection') || 
                    errorMessage.includes('database') || 
                    errorMessage.includes('connection')) {
                    errorMessage = 'Database connection error. Your changes will be saved when connection is restored.';
                }
                
                showToast('Error updating item: ' + errorMessage, 'danger');
                
                // Always reset button state
                resetButton();
                
                // Close the modal on severe errors to allow retry
                if (errorMessage.includes('parsing server response')) {
                    setTimeout(() => {
                        try {
                            const modal = bootstrap.Modal.getInstance(document.getElementById('editItemModal'));
                            if (modal) modal.hide();
                        } catch (e) {
                            console.error('Error closing modal:', e);
                        }
                    }, 1500);
                }
            });
        });
    }
}

// Update item values in the table without page reload
function updateItemInTable(itemId, item) {
    const row = document.querySelector('.item-row[data-id="'+itemId+'"]');
    if (!row) return;
    
    // Get data from item object or formData depending on what's passed
    const description = item.description || '';
    const scientificName = item.scientific_name || '';
    const potSize = item.pot_size || '';
    const height = item.height || '';
    const quantity = item.quantity || 1;
    const sellingPrice = item.selling_price || 0;
    const vatRate = item.vat_rate || 19;
    const supplier = item.supplier || 'Not specified';
    const total = item.total || (quantity * sellingPrice);
    
    // Update the row cells
    const cells = row.querySelectorAll('td');
    cells[2].textContent = description;
    cells[3].innerHTML = '<em>' + scientificName + '</em>';
    cells[4].textContent = potSize;
    cells[5].textContent = height;
    cells[6].textContent = parseInt(quantity).toString();
    
    // Format the selling price with currency
    const currency = document.querySelector('#quotation-currency')?.value || '€';
    cells[7].textContent = currency + ' ' + parseFloat(sellingPrice).toFixed(2);
    
    cells[8].textContent = parseFloat(vatRate).toFixed(1) + '%';
    cells[9].textContent = supplier;
    cells[10].textContent = currency + ' ' + parseFloat(total).toFixed(2);
    
    // Update data attributes for future edits
    const editBtn = row.querySelector('.edit-item-btn');
    if (editBtn) {
        editBtn.setAttribute('data-description', description);
        editBtn.setAttribute('data-scientific-name', scientificName);
        editBtn.setAttribute('data-pot-size', potSize);
        editBtn.setAttribute('data-height', height);
        editBtn.setAttribute('data-quantity', quantity);
        editBtn.setAttribute('data-selling-price', sellingPrice);
        editBtn.setAttribute('data-vat-rate', vatRate);
        editBtn.setAttribute('data-supplier', supplier);
    }
    
    // Update total at the bottom of the table
    updateQuotationTotal();
}

// Highlight a row to show it was updated
function highlightRow(itemId) {
    const row = document.querySelector('.item-row[data-id="'+itemId+'"]');
    if (!row) return;
    
    // Add highlight class
    row.classList.add('highlight-row');
    
    // Scroll to the row
    row.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    // Remove highlight after 2 seconds
    setTimeout(() => {
        row.classList.remove('highlight-row');
    }, 2000);
}

// Update the quotation total based on item totals
function updateQuotationTotal() {
    let total = 0;
    const items = document.querySelectorAll('.item-row');
    
    items.forEach(item => {
        const itemTotal = parseFloat(item.querySelector('td:nth-last-child(2)').textContent.replace(/[^0-9.-]+/g, '')) || 0;
        total += itemTotal;
    });
    
    // Update the total in the footer
    const totalRow = document.querySelector('tfoot .text-end');
    if (totalRow) {
        const currency = document.querySelector('#quotation-currency')?.value || '€';
        totalRow.textContent = currency + ' ' + total.toFixed(2);
    }
}

// Show toast notification
function showToast(message, type) {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white bg-' + type + ' border-0';
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = '<div class="d-flex">' +
                       '<div class="toast-body">' + message + '</div>' +
                       '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>' +
                       '</div>';
    
    toastContainer.appendChild(toast);
    
    // Show the toast
    const bsToast = new bootstrap.Toast(toast, { delay: 5000 });
    bsToast.show();
    
    // Remove it after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Confirmation for deleting items
function confirmDelete(deleteUrl) {
    document.getElementById('confirmDeleteBtn').href = deleteUrl;
    var deleteModal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
    deleteModal.show();
}

// Add AI price suggestion handlers
document.addEventListener('DOMContentLoaded', function() {
    // Handle suggest button clicks for all suggest price buttons
    document.addEventListener('click', function(event) {
        if (event.target.closest('.suggest-price-btn')) {
            const button = event.target.closest('.suggest-price-btn');
            const scientificNameId = button.getAttribute('data-scientific-name-id');
            const potSizeId = button.getAttribute('data-pot-size-id');
            const priceId = button.getAttribute('data-price-id');
            const costPriceId = button.getAttribute('data-cost-price-id');
            
            if (scientificNameId && potSizeId && priceId) {
                getPriceSuggestion(scientificNameId, potSizeId, priceId, costPriceId);
            }
        }
    });
    
    // Legacy handlers for backwards compatibility
    if (document.getElementById('priceAssistBtn')) {
        document.getElementById('priceAssistBtn').addEventListener('click', function() {
            getPriceSuggestion('scientific_name', 'pot_size', 'selling_price', 'cost_price');
        });
    }
    
    if (document.getElementById('editPriceAssistBtn')) {
        document.getElementById('editPriceAssistBtn').addEventListener('click', function() {
            getPriceSuggestion('edit_scientific_name', 'edit_pot_size', 'edit_selling_price', 'edit_cost_price');
        });
    }
    
    // Add highlight-row style if not already in stylesheet
    if (!document.getElementById('highlight-style')) {
        const style = document.createElement('style');
        style.id = 'highlight-style';
        style.textContent = '.highlight-row {' +
                           'animation: highlight-fade 2s;' +
                           '}' +
                           '@keyframes highlight-fade {' +
                           '0% { background-color: rgba(255, 255, 0, 0.5); }' +
                           '100% { background-color: transparent; }' +
                           '}';
        document.head.appendChild(style);
    }
    
    // Add hidden input for currency
    const currencyText = document.querySelector('.fw-bold .text-end')?.textContent || '';
    const currencySymbol = currencyText.trim().split(' ')[0] || '€';
    
    const currencyInput = document.createElement('input');
    currencyInput.type = 'hidden';
    currencyInput.id = 'quotation-currency';
    currencyInput.value = currencySymbol;
    document.body.appendChild(currencyInput);
});

// Function to get AI-powered price suggestions
function getPriceSuggestion(scientificNameId, potSizeId, sellingPriceId, costPriceId = null) {
    const scientificName = document.getElementById(scientificNameId).value.trim();
    const potSize = document.getElementById(potSizeId).value.trim();
    const customerId = document.getElementById('customer-id').value;
    const costPrice = costPriceId ? document.getElementById(costPriceId).value.trim() : null;
    
    if (!scientificName) {
        showToast("Please enter a scientific name first", "warning");
        return;
    }
    
    // Show AI loading indicator
    const button = document.querySelector(`[data-price-id="${sellingPriceId}"]`);
    const originalText = button ? button.innerHTML : '<i class="fas fa-robot me-1"></i> AI Suggest';
    if (button) {
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> AI Thinking...';
        button.disabled = true;
    }
    
    // Build API URL with parameters
    let apiUrl = '/api/price-assistant?scientific_name=' + encodeURIComponent(scientificName) + 
                '&pot_size=' + encodeURIComponent(potSize) + 
                '&customer_id=' + customerId + 
                '&use_ai=true';
    
    if (costPrice && !isNaN(parseFloat(costPrice))) {
        apiUrl += '&cost_price=' + encodeURIComponent(costPrice);
    }
    
    // Call the AI price assistant API
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text().then(text => {
                try {
                    return JSON.parse(text);
                } catch (err) {
                    console.error("Error parsing JSON:", err);
                    console.log("Raw response:", text);
                    throw new Error("Error parsing server response. Please try again.");
                }
            });
        })
        .then(data => {
            if (data.error) {
                showToast(data.error, "danger");
                return;
            }
            
            if (data.suggested_price) {
                // Update the price field
                document.getElementById(sellingPriceId).value = data.suggested_price.toFixed(2);
                
                // Show AI rationale if available
                if (data.rationale) {
                    showToast('AI Suggestion: €' + data.suggested_price.toFixed(2) + ' - ' + data.rationale, "success");
                } else {
                    showToast('AI Price suggestion: €' + data.suggested_price.toFixed(2) + ' (based on ' + data.source + ')', "success");
                }
                
                // Add visual indicator that this is an AI suggestion
                const priceField = document.getElementById(sellingPriceId);
                priceField.style.borderColor = '#28a745';
                priceField.style.boxShadow = '0 0 0 0.2rem rgba(40, 167, 69, 0.25)';
                
                // Remove the visual indicator after 3 seconds
                setTimeout(() => {
                    priceField.style.borderColor = '';
                    priceField.style.boxShadow = '';
                }, 3000);
                
                // Trigger recalculation if the function exists
                if (typeof updateRowTotal === 'function') {
                    updateRowTotal(priceField);
                }
            } else {
                showToast("No price suggestion available for this product", "warning");
            }
        })
        .catch(error => {
            console.error('Error fetching AI price suggestions:', error);
            showToast("Error retrieving AI price data: " + error.message, "danger");
        })
        .finally(() => {
            // Restore button state
            if (button) {
                button.innerHTML = originalText;
                button.disabled = false;
            }
        });
}

// Setup supplier dropdown functionality
function setupSupplierDropdowns() {
    // Add event handlers for supplier dropdowns
    const supplierIdSelect = document.getElementById('supplier_id');
    const editSupplierIdSelect = document.getElementById('edit_supplier_id');
    
    if (supplierIdSelect) {
        supplierIdSelect.addEventListener('change', function() {
            const manualContainer = document.getElementById('manual_supplier_container');
            const supplierInput = document.getElementById('supplier');
            
            if (this.value) {
                // If a supplier is selected, hide manual input and set supplier name
                manualContainer.classList.add('d-none');
                // Get the selected option's text
                const selectedOption = this.options[this.selectedIndex];
                supplierInput.value = selectedOption.text;
            } else {
                // If "custom" option is selected, show manual input
                manualContainer.classList.remove('d-none');
                supplierInput.value = '';
            }
        });
    }
    
    if (editSupplierIdSelect) {
        editSupplierIdSelect.addEventListener('change', function() {
            const manualContainer = document.getElementById('edit_manual_supplier_container');
            const supplierInput = document.getElementById('edit_supplier');
            
            if (this.value) {
                // If a supplier is selected, hide manual input and set supplier name
                manualContainer.classList.add('d-none');
                // Get the selected option's text
                const selectedOption = this.options[this.selectedIndex];
                supplierInput.value = selectedOption.text;
            } else {
                // If "custom" option is selected, show manual input
                manualContainer.classList.remove('d-none');
                supplierInput.value = '';
            }
        });
    }
}
