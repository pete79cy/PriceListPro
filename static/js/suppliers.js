/**
 * Supplier Management JavaScript
 * Handles dynamic filtering, sorting, and UI interactions for supplier management
 */

document.addEventListener('DOMContentLoaded', function() {
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Delete confirmation
    window.confirmDelete = function(id, name) {
        document.getElementById('delete-supplier-name').textContent = name;
        document.getElementById('delete-supplier-btn').href = `/delete_supplier/${id}`;
        const deleteModal = new bootstrap.Modal(document.getElementById('deleteSupplierModal'));
        deleteModal.show();
    };
    
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Client-side search and filtering
    const searchInput = document.getElementById('supplier-search');
    const typeFilter = document.getElementById('supplier-type-filter');
    const sortSelect = document.getElementById('supplier-sort');
    
    function filterSuppliers() {
        const searchTerm = searchInput.value.toLowerCase();
        const filterType = typeFilter.value;
        const sortBy = sortSelect.value;
        
        // Get all supplier items
        const supplierItems = document.querySelectorAll('.supplier-item');
        let visibleCount = 0;
        
        supplierItems.forEach(item => {
            const supplierName = item.dataset.name;
            const supplierType = item.dataset.type;
            const createdTime = parseFloat(item.dataset.created);
            
            // Apply search filter
            const matchesSearch = !searchTerm || 
                                 supplierName.includes(searchTerm) || 
                                 (item.textContent.toLowerCase().includes(searchTerm));
            
            // Apply type filter
            const matchesType = (filterType === 'all') || 
                                (filterType === 'inhouse' && supplierType === 'inhouse') ||
                                (filterType === 'external' && supplierType === 'external');
            
            // Show/hide based on filters
            if (matchesSearch && matchesType) {
                item.style.display = '';
                visibleCount++;
            } else {
                item.style.display = 'none';
            }
        });
        
        // Update empty state if no results
        const emptyResults = document.getElementById('empty-results');
        const resultsCount = document.getElementById('results-count');
        if (emptyResults) {
            if (visibleCount === 0) {
                emptyResults.classList.remove('d-none');
                if (searchTerm) {
                    document.getElementById('search-term').textContent = `"${searchTerm}"`;
                }
            } else {
                emptyResults.classList.add('d-none');
            }
        }
        
        if (resultsCount) {
            resultsCount.textContent = visibleCount;
        }
        
        // Apply sorting to the visible items
        applySort(sortBy);
    }
    
    function applySort(sortBy) {
        // Apply sorting to cards view
        const cardsContainer = document.querySelector('#cards-view .row');
        if (cardsContainer) {
            const cards = Array.from(cardsContainer.querySelectorAll('.supplier-item:not([style*="display: none"])'));
            sortItems(cards, sortBy);
            cards.forEach(card => cardsContainer.appendChild(card));
        }
        
        // Apply sorting to list view
        const listContainer = document.querySelector('#list-view tbody');
        if (listContainer) {
            const rows = Array.from(listContainer.querySelectorAll('.supplier-item:not([style*="display: none"])'));
            sortItems(rows, sortBy);
            rows.forEach(row => listContainer.appendChild(row));
        }
    }
    
    function sortItems(items, sortBy) {
        items.sort((a, b) => {
            const aName = a.dataset.name;
            const bName = b.dataset.name;
            const aCreated = parseFloat(a.dataset.created);
            const bCreated = parseFloat(b.dataset.created);
            
            switch(sortBy) {
                case 'name_asc':
                    return aName.localeCompare(bName);
                case 'name_desc':
                    return bName.localeCompare(aName);
                case 'newest':
                    return bCreated - aCreated;
                case 'oldest':
                    return aCreated - bCreated;
                default:
                    return 0;
            }
        });
    }
    
    // Add event listeners for filtering and sorting
    if (searchInput) {
        searchInput.addEventListener('input', filterSuppliers);
    }
    
    if (typeFilter) {
        typeFilter.addEventListener('change', filterSuppliers);
    }
    
    if (sortSelect) {
        sortSelect.addEventListener('change', filterSuppliers);
    }
    
    // Initialize filtering on page load
    if (searchInput || typeFilter || sortSelect) {
        filterSuppliers();
    }
    
    // Handle flash messages as toasts
    const toastContainer = document.querySelector('.toast-container');
    if (toastContainer) {
        const messages = toastContainer.querySelectorAll('.toast');
        messages.forEach(toast => {
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
        });
    }
    
    // Toggle view modes (card/list)
    const viewTabs = document.querySelectorAll('#viewTabs button');
    if (viewTabs.length > 0) {
        // Check if a saved preference exists
        const savedView = localStorage.getItem('supplier_view_mode');
        if (savedView) {
            // Activate the saved tab
            const tabToActivate = document.querySelector(`#viewTabs button[data-bs-target="#${savedView}"]`);
            if (tabToActivate) {
                const tab = new bootstrap.Tab(tabToActivate);
                tab.show();
            }
        }
        
        // Save preference when tab changes
        viewTabs.forEach(tab => {
            tab.addEventListener('shown.bs.tab', function(event) {
                const target = event.target.getAttribute('data-bs-target').substring(1); // Remove the #
                localStorage.setItem('supplier_view_mode', target);
            });
        });
    }
});
