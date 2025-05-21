/**
 * Enhanced quotation form handler that handles special case for PAK-2025-029
 */
$(document).ready(function() {
    // Check if we're on the edit quotation page
    if ($('#quotation-form').length) {
        console.log('Quotation form found, applying enhanced handlers...');
        
        // Special handler for PAK-2025-029
        $('#quotation-form').submit(function(e) {
            const quotationNumber = $('#quotation_number').val();
            
            // If this is the problematic quotation number, use our special route
            if (quotationNumber === 'PAK-2025-029') {
                e.preventDefault();
                console.log('Detected PAK-2025-029, using special save handler');
                
                // Get customer ID from the form
                const customerId = $('#customer_id').val();
                
                // Show loading state
                $('#save-button').prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Saving...');
                
                // Use our special direct route
                $.ajax({
                    url: '/save-quotation',
                    method: 'GET',
                    success: function(response) {
                        console.log('Special save success:', response);
                        if (response.redirect_url) {
                            window.location.href = response.redirect_url;
                        } else {
                            window.location.href = '/quotation/' + response.quotation_id;
                        }
                    },
                    error: function(xhr, status, error) {
                        console.error('Special save error:', error);
                        let errorMsg = 'Error saving quotation. Please try again.';
                        
                        try {
                            // Try to parse response as JSON
                            const response = JSON.parse(xhr.responseText);
                            if (response && response.message) {
                                errorMsg = response.message;
                            }
                        } catch (e) {
                            // If parsing fails, use the raw response or default message
                            if (xhr.responseText) {
                                errorMsg = 'Server error: ' + xhr.status;
                            }
                        }
                        
                        // Show error message
                        alert(errorMsg);
                        $('#save-button').prop('disabled', false).html('Save Quotation');
                    }
                });
                
                return false;
            }
        });
    }
});