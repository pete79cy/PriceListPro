/**
 * Quotation management JavaScript functions
 */

// Initialize edit buttons on document load
document.addEventListener('DOMContentLoaded', function() {
    // Setup the supplier dropdown event handlers
    setupSupplierDropdowns();
    
    // Setup AJAX form submission for edit item form
    setupAjaxFormSubmission();
    
    // Note: Edit button click handlers are now managed in the template's inline JS
    // using the Tailwind-based modal system (initEditItemButtons function)
});

// Setup AJAX form submission
function setupAjaxFormSubmission() {
    const editItemForm = document.getElementById('editItemForm');
    if (editItemForm) {
        editItemForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const itemId = this.getAttribute('data-item-id');
            const formData = new FormData(this);
            
            // Show processing indicator - find button by type=submit in the form
            const submitBtn = editItemForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn ? submitBtn.innerHTML : '';
            if (submitBtn) {
                submitBtn.innerHTML = '<span class="material-symbols-outlined animate-spin text-[16px]">progress_activity</span> Saving...';
                submitBtn.disabled = true;
            }
            
            // Create a function to reset button state that we can call in multiple places
            const resetButton = function() {
                if (submitBtn) {
                    submitBtn.innerHTML = originalBtnText;
                    submitBtn.disabled = false;
                }
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
                
                // Close the modal using the Tailwind modal system
                if (typeof closeModal === 'function') {
                    closeModal('editItemModal');
                } else {
                    // Fallback: hide the modal manually
                    const modal = document.getElementById('editItemModal');
                    if (modal) modal.classList.add('hidden');
                }
                
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
                            if (typeof closeModal === 'function') {
                                closeModal('editItemModal');
                            } else {
                                const modal = document.getElementById('editItemModal');
                                if (modal) modal.classList.add('hidden');
                            }
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

// Show toast notification (Tailwind-compatible)
function showToast(message, type) {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'fixed bottom-4 right-4 z-50 flex flex-col gap-2';
        document.body.appendChild(toastContainer);
    }
    
    // Map type to Tailwind color classes
    const typeStyles = {
        'success': 'bg-emerald-500 text-white',
        'danger': 'bg-red-500 text-white',
        'warning': 'bg-amber-500 text-white',
        'info': 'bg-blue-500 text-white',
        'primary': 'bg-primary text-white'
    };
    const colorClass = typeStyles[type] || typeStyles['info'];
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `${colorClass} px-4 py-3 rounded-lg shadow-lg flex items-center justify-between gap-3 min-w-[280px] transform transition-all duration-300 translate-x-full`;
    toast.setAttribute('role', 'alert');
    
    toast.innerHTML = `
        <span class="text-sm font-medium">${message}</span>
        <button type="button" class="text-white/80 hover:text-white transition-colors" aria-label="Close">
            <span class="material-symbols-outlined text-[18px]">close</span>
        </button>
    `;
    
    toastContainer.appendChild(toast);
    
    // Animate in
    requestAnimationFrame(() => {
        toast.classList.remove('translate-x-full');
        toast.classList.add('translate-x-0');
    });
    
    // Close button handler
    toast.querySelector('button').addEventListener('click', function() {
        closeToast(toast);
    });
    
    // Auto-hide after 5 seconds
    setTimeout(() => closeToast(toast), 5000);
    
    function closeToast(toastEl) {
        toastEl.classList.add('translate-x-full');
        toastEl.classList.remove('translate-x-0');
        setTimeout(() => toastEl.remove(), 300);
    }
}

// Confirmation for deleting items
function confirmDelete(deleteUrl) {
    document.getElementById('confirmDeleteBtn').href = deleteUrl;
    if (typeof openModal === 'function') {
        openModal('deleteConfirmModal');
    } else {
        const modal = document.getElementById('deleteConfirmModal');
        if (modal) modal.classList.remove('hidden');
    }
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
            console.log('AI API Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.text().then(text => {
                console.log('AI API Response text:', text);
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
            console.log('AI API Response data:', data);
            if (data.error) {
                console.log('AI API returned error:', data.error);
                showToast(data.error, "danger");
                return;
            }
            
            if (data.suggested_price) {
                console.log('AI suggested price:', data.suggested_price);
                // Update the price field
                document.getElementById(sellingPriceId).value = data.suggested_price.toFixed(2);
                
                // Detect if using Tier 1 (customer data) or Tier 2 (global fallback)
                const rationale = data.rationale || '';
                const isGlobalFallback = rationale.toUpperCase().includes('NO CUSTOMER HISTORY') || 
                                         rationale.toUpperCase().includes('GLOBAL') ||
                                         rationale.toUpperCase().includes('FALLBACK');
                
                // Build enhanced toast message with tier indicator
                let tierBadge = '';
                let toastType = 'success';
                let borderColor = '#28a745'; // Green for customer data
                let shadowColor = 'rgba(40, 167, 69, 0.25)';
                
                if (isGlobalFallback) {
                    tierBadge = '⚠️ [Global Fallback] ';
                    toastType = 'warning';
                    borderColor = '#ffc107'; // Yellow for global fallback
                    shadowColor = 'rgba(255, 193, 7, 0.25)';
                } else {
                    tierBadge = '✓ [Customer History] ';
                }
                
                // Show AI rationale with tier badge
                if (rationale) {
                    showToast(tierBadge + '€' + data.suggested_price.toFixed(2) + ' - ' + rationale, toastType);
                } else {
                    showToast(tierBadge + '€' + data.suggested_price.toFixed(2) + ' (based on ' + data.source + ')', toastType);
                }
                
                // Add visual indicator that this is an AI suggestion
                const priceField = document.getElementById(sellingPriceId);
                if (priceField) {
                    priceField.style.borderColor = borderColor;
                    priceField.style.boxShadow = '0 0 0 0.2rem ' + shadowColor;
                    
                    // Remove the visual indicator after 3 seconds
                    setTimeout(() => {
                        priceField.style.borderColor = '';
                        priceField.style.boxShadow = '';
                    }, 3000);
                    
                    // Trigger recalculation if the function exists
                    if (typeof updateRowTotal === 'function') {
                        updateRowTotal(priceField);
                    }
                }
            } else {
                console.log('No price suggestion available');
                showToast("No price suggestion available for this product", "warning");
            }
        })
        .catch(error => {
            console.error('Error fetching AI price suggestions:', error);
            showToast("Error retrieving AI price data: " + error.message, "danger");
        })
        .finally(() => {
            // Restore button state with detailed logging
            console.log('Restoring button state. Button exists:', !!button);
            if (button) {
                console.log('Original text:', originalText);
                // Force restoration of button text and state
                setTimeout(() => {
                    button.innerHTML = '<i class="fas fa-robot me-1"></i> AI Suggest';
                    button.disabled = false;
                    console.log('Button restored successfully');
                }, 100);
            } else {
                console.warn('Button not found for restoration');
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
