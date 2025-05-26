document.addEventListener('DOMContentLoaded', function() {
  const searchForm = document.getElementById('search-form');
  const searchQuery = document.getElementById('search-query');
  const customerSelect = document.getElementById('customer-select');
  const searchSpinner = document.getElementById('search-spinner');
  const searchResults = document.getElementById('search-results');
  const resultsContainer = document.getElementById('results-container');
  const noResults = document.getElementById('no-results');

  // Handle the search form submission
  searchForm.addEventListener('submit', function(e) {
    e.preventDefault();

    const query = searchQuery.value.trim();
    const customerId = customerSelect.value;

    if (!query) {
      return;
    }

    // Show loading spinner
    searchSpinner.classList.remove('d-none');
    searchResults.classList.add('d-none');
    noResults.classList.add('d-none');

    // Make AJAX request to search API
    fetch(`/api/search?q=${encodeURIComponent(query)}&customer_id=${customerId}`)
      .then(response => {
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
        // Hide spinner
        searchSpinner.classList.add('d-none');

        if (data.results && data.results.length > 0) {
          // Show results
          renderSearchResults(data);
          searchResults.classList.remove('d-none');
        } else {
          // Show no results message
          noResults.classList.remove('d-none');
        }
      })
      .catch(error => {
        console.error('Search error:', error);
        searchSpinner.classList.add('d-none');

        // Show error message
        resultsContainer.innerHTML = `
          <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>
            An error occurred while searching. Please try again.
          </div>
        `;
        searchResults.classList.remove('d-none');
      });
  });

  // Function to render search results
  function renderSearchResults(data) {
    // Get customer name
    const customerName = customerSelect.value ? customerSelect.options[customerSelect.selectedIndex].text : 'All Customers';
    const isGeneralSearch = !customerSelect.value;

    // Create header
    let html = `
      <div class="alert alert-success mb-4">
        <i class="fas fa-check-circle me-2"></i>
        Found ${data.results.length} matching products${isGeneralSearch ? ' (general search)' : ' for <strong>' + customerName + '</strong>'}
      </div>
    `;

    // Create cards for each result
    html += '<div class="row">';

    data.results.forEach(result => {
      // Handle pricing display for different search types
      let priceDisplay = '';
      if (result.current_price !== null && result.current_price !== undefined) {
        const formattedPrice = new Intl.NumberFormat('de-DE', {
          style: 'currency',
          currency: 'EUR'
        }).format(result.current_price);
        
        priceDisplay = `
          <div class="text-center mb-3">
            <span class="display-6">${formattedPrice}</span>
            <div class="text-muted small">${result.customer_specific ? 'Customer Price' : 'General Price'}</div>
            ${result.price_note ? `<div class="text-info small">${result.price_note}</div>` : ''}
          </div>
        `;
      } else {
        priceDisplay = `
          <div class="text-center mb-3">
            <span class="text-muted">No Price Available</span>
            <div class="text-muted small">Select a customer for pricing</div>
          </div>
        `;
      }

      html += `
        <div class="col-md-6 col-lg-4 mb-4">
          <div class="card h-100">
            <div class="card-header ${result.customer_specific ? 'bg-primary' : 'bg-secondary'} text-white">
              <h5 class="mb-0">${result.product_name}</h5>
            </div>
            <div class="card-body">
              ${result.sku ? `<p class="mb-2"><strong>SKU:</strong> ${result.sku}</p>` : ''}
              ${result.description ? `<p class="mb-3"><strong>Description:</strong> ${result.description}</p>` : ''}

              ${priceDisplay}

              ${result.price_history && result.price_history.length > 1 ? `
                <div class="accordion" id="priceHistory${result.product_id}">
                  <div class="accordion-item">
                    <h2 class="accordion-header">
                      <button class="accordion-button collapsed" type="button" 
                              data-bs-toggle="collapse" 
                              data-bs-target="#priceCollapse${result.product_id}">
                        Price History (${result.price_history.length} entries)
                      </button>
                    </h2>
                    <div id="priceCollapse${result.product_id}" class="accordion-collapse collapse">
                      <div class="accordion-body p-0">
                        <table class="table table-sm mb-0">
                          <thead>
                            <tr>
                              <th>Price</th>
                              <th>Effective Date</th>
                            </tr>
                          </thead>
                          <tbody>
                            ${result.price_history.map(price => `
                              <tr>
                                <td>${new Intl.NumberFormat('de-DE', {
                                  style: 'currency',
                                  currency: 'EUR'
                                }).format(price.price)}</td>
                                <td>${price.effective_date || 'N/A'}</td>
                              </tr>
                            `).join('')}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                </div>
              ` : ''}
            </div>
          </div>
        </div>
      `;
    });

    html += '</div>';

    // Update the results container
    resultsContainer.innerHTML = html;
  }
});