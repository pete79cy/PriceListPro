document.addEventListener('DOMContentLoaded', function() {
  const searchForm = document.getElementById('search-form');
  const searchQuery = document.getElementById('search-query');
  const customerSelect = document.getElementById('customer-select');
  const searchSpinner = document.getElementById('search-spinner');
  const searchResults = document.getElementById('search-results');
  const resultsContainer = document.getElementById('results-container');
  const noResults = document.getElementById('no-results');

  // Check if there's a query parameter in the URL
  const urlParams = new URLSearchParams(window.location.search);
  const queryParam = urlParams.get('q');
  
  if (queryParam) {
    searchQuery.value = queryParam;
    // Automatically perform the search
    performSearch();
  }

  // Function to perform search
  function performSearch() {
    const query = searchQuery.value.trim();
    const customerId = customerSelect.value;

    if (!query) {
      return;
    }

    // Hide initial state if present
    const initialState = document.getElementById('initial-state');
    if (initialState) initialState.classList.add('hidden');

    // Show loading spinner (Tailwind uses 'hidden' class)
    searchSpinner.classList.remove('hidden');
    searchResults.classList.add('hidden');
    noResults.classList.add('hidden');

    // Make AJAX request to search API
    fetch(`/api/search?q=${encodeURIComponent(query)}&customer_id=${customerId}`)
      .then(response => {
        if (response.redirected || response.headers.get('content-type') === null ||
            !response.headers.get('content-type').includes('application/json')) {
          return response.text().then(text => {
            try {
              return JSON.parse(text);
            } catch (err) {
              console.error("Non-JSON response from server:", text.substring(0, 200));
              throw new Error("Unexpected server response. Please refresh the page and try again.");
            }
          });
        }
        return response.json();
      })
      .then(data => {
        // Hide spinner
        searchSpinner.classList.add('hidden');

        if (data.error && !data.results) {
          throw new Error(data.error);
        }

        if (data.results && data.results.length > 0) {
          // Show results
          renderSearchResults(data);
          searchResults.classList.remove('hidden');
        } else {
          // Show no results message
          noResults.classList.remove('hidden');
        }
      })
      .catch(error => {
        console.error('Search error:', error);
        searchSpinner.classList.add('hidden');

        // Show error message (Tailwind styled)
        resultsContainer.innerHTML = `
          <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
            <span class="material-symbols-outlined text-red-500">error</span>
            An error occurred while searching. Please try again.
          </div>
        `;
        searchResults.classList.remove('hidden');
      });
  }

  // Handle the search form submission
  searchForm.addEventListener('submit', function(e) {
    e.preventDefault();
    performSearch();
  });

  // Function to render search results
  function renderSearchResults(data) {
    // Get customer name
    const customerName = customerSelect.value ? customerSelect.options[customerSelect.selectedIndex].text : 'All Customers';
    const isGeneralSearch = !customerSelect.value;

    // Create header (Tailwind styled)
    let html = `
      <div class="bg-emerald-50 border border-emerald-200 text-emerald-700 px-4 py-3 rounded-lg flex items-center gap-2 mb-6">
        <span class="material-symbols-outlined text-emerald-500">check_circle</span>
        Found ${data.results.length} matching products${isGeneralSearch ? ' (general search)' : ' for <strong>' + customerName + '</strong>'}
      </div>
    `;

    // Create cards for each result (Tailwind grid)
    html += '<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">';

    data.results.forEach(result => {
      // Handle pricing display for different search types
      let priceDisplay = '';
      if (result.current_price !== null && result.current_price !== undefined) {
        const formattedPrice = new Intl.NumberFormat('de-DE', {
          style: 'currency',
          currency: 'EUR'
        }).format(result.current_price);
        
        priceDisplay = `
          <div class="text-center py-4">
            <span class="text-3xl font-bold text-slate-900">${formattedPrice}</span>
            <div class="text-sm text-slate-500 mt-1">${result.customer_specific ? 'Customer Price' : 'General Price'}</div>
            ${result.price_note ? `<div class="text-sm text-blue-600 mt-1">${result.price_note}</div>` : ''}
          </div>
        `;
      } else {
        priceDisplay = `
          <div class="text-center py-4">
            <span class="text-slate-400">No Price Available</span>
            <div class="text-sm text-slate-400 mt-1">Select a customer for pricing</div>
          </div>
        `;
      }

      html += `
        <div class="bg-white rounded-xl border border-slate-200 overflow-hidden flex flex-col">
          <div class="${result.customer_specific ? 'bg-primary' : 'bg-slate-500'} text-white px-4 py-3">
            <h5 class="font-semibold text-sm">${result.product_name}</h5>
          </div>
          <div class="p-4 flex-1 flex flex-col">
            ${result.sku ? `<p class="text-sm text-slate-600 mb-2"><span class="font-medium">SKU:</span> ${result.sku}</p>` : ''}
            ${result.description ? `<p class="text-sm text-slate-600 mb-3"><span class="font-medium">Description:</span> ${result.description}</p>` : ''}

            ${priceDisplay}

            ${result.price_history && result.price_history.length > 1 ? `
              <details class="mt-auto border-t border-slate-100 pt-3">
                <summary class="text-sm font-medium text-slate-700 cursor-pointer hover:text-primary">
                  Price History (${result.price_history.length} entries)
                </summary>
                <div class="mt-2 overflow-x-auto">
                  <table class="w-full text-sm">
                    <thead>
                      <tr class="border-b border-slate-100">
                        <th class="text-left py-2 text-slate-600 font-medium">Price</th>
                        <th class="text-left py-2 text-slate-600 font-medium">Effective Date</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-50">
                      ${result.price_history.map(price => `
                        <tr>
                          <td class="py-2 text-slate-900">${new Intl.NumberFormat('de-DE', {
                            style: 'currency',
                            currency: 'EUR'
                          }).format(price.price)}</td>
                          <td class="py-2 text-slate-500">${price.effective_date || 'N/A'}</td>
                        </tr>
                      `).join('')}
                    </tbody>
                  </table>
                </div>
              </details>
            ` : ''}
          </div>
        </div>
      `;
    });

    html += '</div>';

    // Update the results container
    resultsContainer.innerHTML = html;
  }
});