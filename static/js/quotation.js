/**
 * Quotation management JavaScript functions
 */

// Initialize edit buttons on document load
document.addEventListener('DOMContentLoaded', function() {
    // Setup the supplier dropdown event handlers
    setupSupplierDropdowns();
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

// Confirmation for deleting items
function confirmDelete(deleteUrl) {
    document.getElementById('confirmDeleteBtn').href = deleteUrl;
    var deleteModal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
    deleteModal.show();
}

// Add price suggestion handlers
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('priceAssistBtn')) {
        document.getElementById('priceAssistBtn').addEventListener('click', function() {
            getPriceSuggestion('scientific_name', 'pot_size', 'selling_price');
        });
    }
    
    if (document.getElementById('editPriceAssistBtn')) {
        document.getElementById('editPriceAssistBtn').addEventListener('click', function() {
            getPriceSuggestion('edit_scientific_name', 'edit_pot_size', 'edit_selling_price');
        });
    }
});

// Function to get price suggestions
function getPriceSuggestion(scientificNameId, potSizeId, sellingPriceId) {
    const scientificName = document.getElementById(scientificNameId).value.trim();
    const potSize = document.getElementById(potSizeId).value.trim();
    const customerId = document.getElementById('customer-id').value;
    
    if (!scientificName) {
        showPriceAssistantMessage("Please enter a scientific name first", "warning");
        return;
    }
    
    // Show loading indicator
    showPriceAssistantMessage("Looking for historical prices...", "info");
    
    // Call the price assistant API
    fetch(`/api/price-assistant?scientific_name=${encodeURIComponent(scientificName)}&pot_size=${encodeURIComponent(potSize)}&customer_id=${customerId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                showPriceAssistantMessage(data.error, "danger");
                return;
            }
            
            if (data.suggested_price) {
                // Update the price field
                document.getElementById(sellingPriceId).value = data.suggested_price;
                showPriceAssistantMessage(`Price suggestion: ${data.suggested_price.toFixed(2)} € (based on ${data.source})`, "success");
            } else {
                showPriceAssistantMessage("No historical price data found for this product", "warning");
            }
        })
        .catch(error => {
            console.error('Error fetching price suggestions:', error);
            showPriceAssistantMessage("Error retrieving price data: " + error.message, "danger");
        });
}

// Show a message to the user
function showPriceAssistantMessage(message, type) {
    // Create a Bootstrap toast notification
    const toastId = 'priceAssistantToast';
    let toast = document.getElementById(toastId);
    
    if (!toast) {
        // Create toast container if it doesn't exist
        toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-' + type;
        toast.id = toastId;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        toast.style.position = 'fixed';
        toast.style.bottom = '20px';
        toast.style.right = '20px';
        toast.style.zIndex = '9999';
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
    } else {
        // Update existing toast
        toast.className = 'toast align-items-center text-white bg-' + type;
        toast.querySelector('.toast-body').textContent = message;
    }
    
    // Show the toast
    const bsToast = new bootstrap.Toast(toast, { delay: 5000 });
    bsToast.show();
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
