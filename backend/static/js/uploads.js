document.addEventListener('DOMContentLoaded', function() {
  // File input custom styling
  const fileInputs = document.querySelectorAll('input[type="file"]');
  
  fileInputs.forEach(input => {
    input.addEventListener('change', function(e) {
      const fileName = e.target.files[0]?.name;
      const label = this.nextElementSibling;
      
      if (label && label.classList.contains('form-file-label')) {
        const labelText = label.querySelector('.form-file-text');
        if (labelText) {
          labelText.textContent = fileName || 'Choose file...';
        }
      }
    });
  });
  
  // Form validation
  const forms = document.querySelectorAll('form');
  
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      if (!form.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
      }
      
      form.classList.add('was-validated');
    });
  });
});
