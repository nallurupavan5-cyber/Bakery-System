// ====================================================
// Sweet Delights Bakery - Core Client JavaScript
// ====================================================

document.addEventListener('DOMContentLoaded', function () {
  // 1. Auto-dismiss flash alerts after 5 seconds
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) {
        bsAlert.close();
      }
    }, 5000);
  });

  // 2. Quantity input steppers on product detail / cart
  document.querySelectorAll('.qty-decrement').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const input = this.parentElement.querySelector('input[type="number"]');
      if (input) {
        let val = parseInt(input.value) || 1;
        if (val > 1) {
          input.value = val - 1;
          input.dispatchEvent(new Event('change'));
        }
      }
    });
  });

  document.querySelectorAll('.qty-increment').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const input = this.parentElement.querySelector('input[type="number"]');
      if (input) {
        let val = parseInt(input.value) || 1;
        input.value = val + 1;
        input.dispatchEvent(new Event('change'));
      }
    });
  });

  // 3. Table live search filter
  const tableSearchInput = document.getElementById('tableSearchInput');
  if (tableSearchInput) {
    tableSearchInput.addEventListener('input', function () {
      const filter = this.value.toLowerCase();
      const targetTable = document.querySelector(this.getAttribute('data-table') || '.searchable-table');
      if (targetTable) {
        const rows = targetTable.querySelectorAll('tbody tr');
        rows.forEach(function (row) {
          const text = row.textContent.toLowerCase();
          row.style.display = text.includes(filter) ? '' : 'none';
        });
      }
    });
  }
});

// Helper for Web Share API
function shareInvoice(invoiceNumber, totalAmount, invoiceUrl) {
  if (navigator.share) {
    navigator.share({
      title: `Bakery Invoice #${invoiceNumber}`,
      text: `Invoice #${invoiceNumber} for $${totalAmount} from Sweet Delights Bakery.`,
      url: invoiceUrl || window.location.href
    }).catch(function (error) {
      console.log('Share canceled or error:', error);
    });
  } else {
    // Fallback: Copy link to clipboard
    navigator.clipboard.writeText(invoiceUrl || window.location.href).then(function () {
      alert('Invoice URL copied to clipboard!');
    });
  }
}
