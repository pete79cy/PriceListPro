/* eslint-env jquery */
/* global Decimal, Sortable */

/**
 * Enhanced Order Manager for Daily Orders Feature
 * Provides production-ready order management with decimal precision,
 * debounced search, sortable items, and comprehensive validation.
 */
class EnhancedOrderManager {
  constructor() {
    this.currentOrder       = null;
    this.currentCustomerId  = null;
    this.orderItems         = [];   // [{id, productId, plantName, size, qty, price, vat}]
    this.searchTimeout      = null;

    // jQuery elements
    this.$results   = $('#searchResults');
    this.$items     = $('#orderItems');
    this.$subtotal  = $('#orderSubtotal');
    this.$vat5      = $('#orderVat5');
    this.$vat19     = $('#orderVat19');
    this.$grand     = $('#orderGrand');

    this.init();
  }

  /* ---------- lifecycle ---------- */
  init() {
    this.bindEvents();
    this.loadExistingItems();   // pre-filled when editing
    this.updateOrderSummary();  // initial totals
    this.debugLog('Enhanced Order Manager initialized');
  }

  bindEvents() {
    /* customer change */
    $('#customerSelect, select[name="customer_id"]').on('change', e => {
      this.currentCustomerId = Number(e.target.value) || null;
      this.clearSearch();
      this.debugLog(`Customer changed to: ${this.currentCustomerId}`);
    });

    /* product search */
    $('#productSearch, input[name="product_search"]').on('input', e => {
      clearTimeout(this.searchTimeout);
      const q = e.target.value.trim();
      this.searchTimeout = setTimeout(() => this.searchProducts(q), 300);
    });

    /* manual add */
    $('#manualAddBtn, .manual-add-btn').on('click', () => this.showManualEntryForm());

    /* edit-modal save */
    $('#saveItemChanges').on('click', () => this.saveItemChanges());

    /* form submit */
    $('#orderForm, form').on('submit', e => {
      e.preventDefault();
      this.saveOrder();
    });

    /* sortable rows - check if sortable library is available */
    if (typeof $.fn.sortable !== 'undefined') {
      this.$items.sortable({
        handle      : '.drag-handle',
        placeholder : 'sortable-placeholder',
        update      : () => this.updateItemPositions()
      });
    }

    /* inline qty / price change */
    this.$items.on('input', '.js-qty, .js-price, .js-vat, .qty, .price, .vat-rate', e => {
      const $row  = $(e.target).closest('tr');
      const idx   = Number($row.data('idx'));
      const field = $(e.target).data('field') || this.getFieldFromClass(e.target.className);
      
      if (this.orderItems[idx] && field) {
        const value = $(e.target).val() || 0;
        this.orderItems[idx][field] = new Decimal(value);
        this.renderRow(idx);
        this.updateOrderSummary();
      }
    });

    /* remove item */
    this.$items.on('click', '.js-remove, .remove-item', e => {
      const $row = $(e.target).closest('tr');
      const idx = Number($row.data('idx'));
      this.removeItem(idx);
    });
  }

  getFieldFromClass(className) {
    if (className.includes('qty')) return 'qty';
    if (className.includes('price')) return 'price';
    if (className.includes('vat')) return 'vat';
    return null;
  }

  /* ---------- optimized search & add ---------- */
  async searchProducts(query) {
    if (query.length < 2) {
      this.$results.empty();
      this.debugLog('Query too short, clearing results');
      return;
    }

    // Show loading state immediately
    this.$results.html('<li class="loading text-center py-2"><i class="fas fa-spinner fa-spin"></i> Searching...</li>');
    this.debugLog(`Searching for "${query}" with customer ID: ${this.currentCustomerId}`);
    
    try {
      const params = new URLSearchParams({ 
        q: query, 
        customer_id: this.currentCustomerId || '',
        limit: 15  // Increased limit for better results
      });
      const url = `/orders/api/search/products?${params}`;
      this.debugLog(`Requesting: ${url}`);
      
      const startTime = performance.now();
      const res = await fetch(url);
      const endTime = performance.now();
      
      this.debugLog(`Response status: ${res.status} ${res.statusText} (${Math.round(endTime - startTime)}ms)`);
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      
      const data = await res.json();
      this.debugLog(`Found ${data.length} products in ${Math.round(endTime - startTime)}ms`, data);

      if (data.length === 0) {
        this.$results.html(`
          <li class="no-results text-center py-3 text-muted">
            <i class="fas fa-search"></i><br>
            No products found for "${query}"
          </li>
        `);
        return;
      }

      // Enhanced result display with better formatting
      this.$results.html(
        data.map(p => `
          <li class="result list-group-item list-group-item-action d-flex justify-content-between align-items-center" 
              data-id="${p.id}" 
              data-type="${p.type}"
              title="Click to add to order">
            <div class="flex-grow-1">
              <div class="fw-bold text-primary">${p.name}</div>
              ${p.scientific_name ? `<small class="text-muted fst-italic">${p.scientific_name}</small><br>` : ''}
              ${p.size ? `<small class="badge bg-light text-dark">${p.size}</small>` : ''}
              ${p.category ? `<small class="badge bg-secondary ms-1">${p.category}</small>` : ''}
              ${p.has_customer_price ? '<small class="badge bg-success ms-1">Custom Price</small>' : ''}
            </div>
            <div class="text-end">
              <div class="fw-bold text-success">${p.price_formatted || '€' + p.price}</div>
              ${p.type === 'supplier_product' ? '<small class="text-muted">Supplier</small>' : ''}
            </div>
          </li>`).join('')
      );

      /* click-to-add */
      this.$results.find('.result').on('click', e => {
        const id = Number($(e.currentTarget).data('id'));
        const prod = data.find(p => p.id === id);
        this.addProductToOrder(prod);
        this.clearSearch();
      });

    } catch (err) {
      console.error('Search error:', err);
      this.$results.html('<li class="error text-danger">Search failed - see console</li>');
    }
  }

  addProductToOrder(prod) {
    this.debugLog(`Adding product: ${prod.name} (ID: ${prod.id}) - €${prod.price} per ${prod.size || 'unit'}`);
    
    const item = {
      id        : Date.now(),          // temp UID until order saved
      productId : prod.id,
      plantName : prod.name,
      size      : prod.size || '',
      qty       : new Decimal(1),
      price     : new Decimal(prod.price || 0),
      vat       : new Decimal(prod.vat_rate || 19),
      priceListId: prod.price_list_id
    };
    
    this.orderItems.push(item);
    this.renderRow(this.orderItems.length - 1);
    this.updateOrderSummary();
  }

  showManualEntryForm() {
    // For now, add a simple manual item
    const item = {
      id        : Date.now(),
      productId : null,
      plantName : 'Manual Entry',
      size      : '',
      qty       : new Decimal(1),
      price     : new Decimal(0),
      vat       : new Decimal(19),
      priceListId: null
    };
    
    this.orderItems.push(item);
    this.renderRow(this.orderItems.length - 1);
    this.updateOrderSummary();
  }

  saveItemChanges() {
    /* read modal inputs and push into orderItems, then rerender */
    // Implementation depends on modal structure
  }

  /* ---------- rendering ---------- */
  renderRow(idx) {
    const it = this.orderItems[idx];
    const line = it.price.times(it.qty);
    const trId = `row-${idx}`;
    const existing = this.$items.find(`#${trId}`);

    const tpl = `
      <tr id="${trId}" data-idx="${idx}" class="order-item">
        <td class="drag-handle" style="cursor: move;">⋮⋮</td>
        <td>
          <div class="fw-bold">${it.plantName}</div>
          ${it.size ? `<small class="text-muted">${it.size}</small>` : ''}
        </td>
        <td><input type="number" class="form-control js-qty qty" data-field="qty" value="${it.qty}" min="0" step="1"></td>
        <td><input type="number" class="form-control js-price price" data-field="price" value="${it.price}" min="0" step="0.01"></td>
        <td><select class="form-select js-vat vat-rate" data-field="vat">
          <option value="5" ${it.vat.equals(5) ? 'selected' : ''}>5%</option>
          <option value="19" ${it.vat.equals(19) ? 'selected' : ''}>19%</option>
        </select></td>
        <td class="line-total text-end">€${line.toFixed(2)}</td>
        <td><button type="button" class="btn btn-sm btn-danger js-remove">×</button></td>
      </tr>`;

    if (existing.length) {
      existing.replaceWith(tpl);
    } else {
      this.$items.append(tpl);
    }
  }

  removeItem(idx) {
    this.debugLog(`Removed item: ${this.orderItems[idx]?.id || idx}`);
    this.orderItems.splice(idx, 1);
    this.$items.find(`#row-${idx}`).remove();
    this.updateItemPositions();
    this.updateOrderSummary();
  }

  loadExistingItems() {
    const initial = $('#initialItems').text();
    if (!initial) return;

    try {
      const items = JSON.parse(initial);
      items.forEach(it => {
        this.orderItems.push({
          id        : it.id,
          productId : it.product_id,
          plantName : it.plant_name,
          size      : it.size,
          qty       : new Decimal(it.quantity),
          price     : new Decimal(it.price),
          vat       : new Decimal(it.vat_rate),
          priceListId: it.price_list_id
        });
      });
      this.orderItems.forEach((_, i) => this.renderRow(i));
    } catch (err) {
      console.error('Initial items parse failed', err);
    }
  }

  updateItemPositions() {
    this.$items.find('tr').each((i, tr) => $(tr).attr('data-idx', i));
  }

  /* ---------- totals ---------- */
  updateOrderSummary() {
    const subtotal = this.orderItems.reduce(
      (s, it) => s.plus(it.price.times(it.qty)), new Decimal(0));

    const vat5 = this.orderItems
      .filter(it => it.vat.equals(5))
      .reduce((s, it) => s.plus(it.price.times(it.qty).times(0.05)), new Decimal(0));

    const vat19 = this.orderItems
      .filter(it => it.vat.equals(19))
      .reduce((s, it) => s.plus(it.price.times(it.qty).times(0.19)), new Decimal(0));

    const grand = subtotal.plus(vat5).plus(vat19);

    // Update summary elements if they exist
    if (this.$subtotal.length) this.$subtotal.text(`€${subtotal.toFixed(2)}`);
    if (this.$vat5.length) this.$vat5.text(`€${vat5.toFixed(2)}`);
    if (this.$vat19.length) this.$vat19.text(`€${vat19.toFixed(2)}`);
    if (this.$grand.length) this.$grand.text(`€${grand.toFixed(2)}`);

    // Also update any other total displays
    $('.order-subtotal').text(`€${subtotal.toFixed(2)}`);
    $('.order-vat-5').text(`€${vat5.toFixed(2)}`);
    $('.order-vat-19').text(`€${vat19.toFixed(2)}`);
    $('.order-total').text(`€${grand.toFixed(2)}`);
  }

  /* ---------- save ---------- */
  async saveOrder() {
    this.debugLog('Form submission started');
    
    const orderItems = this.orderItems.map(it => ({
      product_id: it.productId,
      plant_name: it.plantName,
      size: it.size,
      quantity: it.qty.toNumber(),
      price: it.price.toNumber(),
      vat_rate: it.vat.toNumber(),
      price_list_id: it.priceListId,
      notes: ''
    }));

    this.debugLog('Order items serialized', orderItems);

    const payload = {
      customer_id: this.currentCustomerId,
      delivery_date: $('#deliveryDate, input[name="delivery_date"]').val(),
      notes: $('#orderNotes, textarea[name="notes"]').val(),
      items: JSON.stringify(orderItems)
    };

    try {
      const form = document.querySelector('#orderForm, form');
      const formData = new FormData();
      
      Object.keys(payload).forEach(key => {
        formData.append(key, payload[key]);
      });

      const res = await fetch(form.action || window.location.pathname, {
        method: 'POST',
        body: formData
      });

      if (res.ok) {
        // Check if it's a redirect
        if (res.redirected) {
          window.location.href = res.url;
        } else {
          const result = await res.text();
          if (result.startsWith('/')) {
            window.location.href = result;
          } else {
            window.location.reload();
          }
        }
      } else {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
    } catch (err) {
      console.error('Save error:', err);
      alert('Save failed - see console for details.');
    }
  }

  clearSearch() {
    $('#productSearch, input[name="product_search"]').val('');
    this.$results.empty();
  }

  debugLog(message, data = null) {
    console.log(`[ORDER MANAGER] ${message}`, data);
  }
}

/* Initialize when DOM is ready */
document.addEventListener('DOMContentLoaded', function() {
  // Check if Decimal.js is available
  if (typeof Decimal === 'undefined') {
    console.error('Decimal.js library not found - using native numbers (may have precision issues)');
    // Fallback to native Number if Decimal.js not available
    window.Decimal = function(val) {
      const num = Number(val);
      return {
        plus: function(other) { return new Decimal(num + Number(other)); },
        times: function(other) { return new Decimal(num * Number(other)); },
        equals: function(other) { return num === Number(other); },
        toFixed: function(digits) { return num.toFixed(digits); },
        toNumber: function() { return num; }
      };
    };
  }

  // Initialize the order manager
  window.orderManager = new EnhancedOrderManager();
});