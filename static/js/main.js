document.addEventListener('DOMContentLoaded', function() {
  // Check if Bootstrap is loaded
  if (typeof bootstrap !== 'undefined') {
    // Enable all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Enable all dropdowns
    var dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
    dropdownElementList.map(function (dropdownToggleEl) {
      return new bootstrap.Dropdown(dropdownToggleEl);
    });
    
    // Auto-dismiss alerts after 5 seconds
    var alertList = document.querySelectorAll('.alert');
    alertList.forEach(function(alert) {
      setTimeout(function() {
        var bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
      }, 5000);
    });
  } else {
    console.warn('Bootstrap not loaded, skipping Bootstrap initialization');
  }
});
