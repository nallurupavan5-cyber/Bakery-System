// ====================================================
// Cashier POS Engine
// ====================================================

const POS = {
  cart: [],
  taxPercent: 5.0,
  currency: '$',

  init: function (taxRate, currencySymbol) {
    this.taxPercent = parseFloat(taxRate) || 5.0;
    this.currency = currencySymbol || '$';
    this.bindEvents();
    this.render();
  },

  bindEvents: function () {
    const self = this;

    // Search filter for POS products
    const searchInput = document.getElementById('posProductSearch');
    if (searchInput) {
      searchInput.addEventListener('input', function () {
        const query = this.value.toLowerCase().trim();
        document.querySelectorAll('.pos-tile-item').forEach(function (tile) {
          const name = tile.getAttribute('data-name').toLowerCase();
          const cat = tile.getAttribute('data-category').toLowerCase();
          tile.style.display = (name.includes(query) || cat.includes(query)) ? '' : 'none';
        });
      });
    }

    // Category filter pills
    document.querySelectorAll('.pos-cat-pill').forEach(function (pill) {
      pill.addEventListener('click', function () {
        document.querySelectorAll('.pos-cat-pill').forEach(p => p.classList.remove('active'));
        this.classList.add('active');
        const catId = this.getAttribute('data-cat-id');
        document.querySelectorAll('.pos-tile-item').forEach(function (tile) {
          if (!catId || tile.getAttribute('data-cat-id') === catId) {
            tile.style.display = '';
          } else {
            tile.style.display = 'none';
          }
        });
      });
    });

    // Discount input listener
    const discInput = document.getElementById('posDiscountInput');
    if (discInput) {
      discInput.addEventListener('input', function () {
        self.render();
      });
    }

    // Customer type switch (walk-in vs registered)
    document.querySelectorAll('input[name="posCustomerType"]').forEach(function (radio) {
      radio.addEventListener('change', function () {
        const val = this.value;
        const regSection = document.getElementById('posRegisteredCustomerSection');
        const newSection = document.getElementById('posNewCustomerSection');
        if (regSection) regSection.style.display = (val === 'registered') ? 'block' : 'none';
        if (newSection) newSection.style.display = (val === 'new') ? 'block' : 'none';
      });
    });

    // Payment mode options
    document.querySelectorAll('.btn-pay-option').forEach(function (btn) {
      btn.addEventListener('click', function () {
        document.querySelectorAll('.btn-pay-option').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        const mode = this.getAttribute('data-mode');
        document.getElementById('posSelectedPaymentMode').value = mode;
      });
    });
  },

  addItem: function (productId, name, price) {
    const existing = this.cart.find(it => it.product_id === productId);
    if (existing) {
      existing.quantity += 1;
    } else {
      this.cart.push({
        product_id: productId,
        name: name,
        price: parseFloat(price),
        quantity: 1
      });
    }
    this.render();
  },

  updateQty: function (productId, delta) {
    const item = this.cart.find(it => it.product_id === productId);
    if (item) {
      item.quantity += delta;
      if (item.quantity <= 0) {
        this.removeItem(productId);
        return;
      }
    }
    this.render();
  },

  removeItem: function (productId) {
    this.cart = this.cart.filter(it => it.product_id !== productId);
    this.render();
  },

  clearCart: function () {
    this.cart = [];
    this.render();
  },

  calculate: function () {
    let subtotal = 0.0;
    this.cart.forEach(it => {
      subtotal += it.price * it.quantity;
    });

    const discInput = document.getElementById('posDiscountInput');
    const discVal = discInput ? parseFloat(discInput.value) || 0.0 : 0.0;
    const discType = document.getElementById('posDiscountType') ? document.getElementById('posDiscountType').value : 'amount';

    let discount = 0.0;
    if (discType === 'percent') {
      discount = (subtotal * discVal) / 100.0;
    } else {
      discount = discVal;
    }
    discount = Math.min(discount, subtotal);

    const taxable = Math.max(0, subtotal - discount);
    const tax = (taxable * this.taxPercent) / 100.0;
    const total = Math.max(0, subtotal - discount + tax);

    return {
      subtotal: subtotal.toFixed(2),
      discount: discount.toFixed(2),
      tax: tax.toFixed(2),
      total: total.toFixed(2)
    };
  },

  render: function () {
    const container = document.getElementById('posCartItemsList');
    if (!container) return;

    if (this.cart.length === 0) {
      container.innerHTML = `
        <div class="text-center py-5 text-muted">
          <i class="bi bi-cart-x fs-1 d-block mb-2 text-secondary"></i>
          <span>Cart is empty. Select items to start billing.</span>
        </div>`;
    } else {
      let html = '';
      this.cart.forEach(it => {
        const lineTotal = (it.price * it.quantity).toFixed(2);
        html += `
          <div class="pos-cart-item">
            <div style="flex: 1; padding-right: 0.5rem;">
              <div class="fw-bold text-truncate" style="max-width: 170px;">${it.name}</div>
              <small class="text-muted">${this.currency}${it.price.toFixed(2)} each</small>
            </div>
            <div class="d-flex align-items-center gap-2">
              <button class="pos-qty-btn" onclick="POS.updateQty(${it.product_id}, -1)">-</button>
              <span class="fw-bold" style="min-width: 20px; text-align: center;">${it.quantity}</span>
              <button class="pos-qty-btn" onclick="POS.updateQty(${it.product_id}, 1)">+</button>
            </div>
            <div class="text-end fw-bold" style="min-width: 65px;">
              ${this.currency}${lineTotal}
            </div>
            <button class="btn btn-sm text-danger ms-2" onclick="POS.removeItem(${it.product_id})" title="Remove item">
              <i class="bi bi-trash"></i>
            </button>
          </div>`;
      });
      container.innerHTML = html;
    }

    const totals = this.calculate();
    document.getElementById('posSubtotalDisplay').innerText = `${this.currency}${totals.subtotal}`;
    document.getElementById('posDiscountDisplay').innerText = `-${this.currency}${totals.discount}`;
    document.getElementById('posTaxDisplay').innerText = `+${this.currency}${totals.tax}`;
    document.getElementById('posTotalDisplay').innerText = `${this.currency}${totals.total}`;

    const checkoutBtn = document.getElementById('posCompleteBtn');
    if (checkoutBtn) {
      checkoutBtn.disabled = (this.cart.length === 0);
    }
  },

  processCheckout: function () {
    if (this.cart.length === 0) {
      alert('Please add at least one item to the cart.');
      return;
    }

    const customerType = document.querySelector('input[name="posCustomerType"]:checked').value;
    const custId = document.getElementById('posCustomerSelect') ? document.getElementById('posCustomerSelect').value : null;
    const newName = document.getElementById('posNewCustomerName') ? document.getElementById('posNewCustomerName').value : '';
    const newPhone = document.getElementById('posNewCustomerPhone') ? document.getElementById('posNewCustomerPhone').value : '';
    const newEmail = document.getElementById('posNewCustomerEmail') ? document.getElementById('posNewCustomerEmail').value : '';
    const paymentMode = document.getElementById('posSelectedPaymentMode').value || 'Cash';
    const discInput = document.getElementById('posDiscountInput');
    const discType = document.getElementById('posDiscountType') ? document.getElementById('posDiscountType').value : 'amount';
    const discVal = discInput ? parseFloat(discInput.value) || 0.0 : 0.0;

    const totals = this.calculate();

    const payload = {
      customer_type: customerType,
      customer_id: custId,
      new_customer_name: newName,
      new_customer_phone: newPhone,
      new_customer_email: newEmail,
      payment_mode: paymentMode,
      payment_status: 'Paid',
      discount_amount: discType === 'amount' ? discVal : 0.0,
      discount_percent: discType === 'percent' ? discVal : 0.0,
      tax_percent: this.taxPercent,
      items: this.cart
    };

    const checkoutBtn = document.getElementById('posCompleteBtn');
    checkoutBtn.disabled = true;
    checkoutBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';

    fetch('/cashier/pos/checkout', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })
      .then(res => res.json())
      .then(data => {
        checkoutBtn.disabled = false;
        checkoutBtn.innerHTML = '<i class="bi bi-check2-circle me-1"></i> Charge & Generate Invoice';

        if (data.success) {
          POS.clearCart();
          // Open Invoice view
          window.location.href = data.invoice_url;
        } else {
          alert('Checkout failed: ' + (data.message || 'Unknown error'));
        }
      })
      .catch(err => {
        checkoutBtn.disabled = false;
        checkoutBtn.innerHTML = '<i class="bi bi-check2-circle me-1"></i> Charge & Generate Invoice';
        alert('Network or server error during checkout: ' + err.message);
      });
  }
};
