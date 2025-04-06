/**
 * AI Insights Feedback Dashboard JavaScript
 * Handles chart rendering and interactive feedback elements
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the feedback dashboard page
    const ratingChart = document.getElementById('ratingDistributionChart');
    const docTypeChart = document.getElementById('documentTypeChart');
    
    if (ratingChart && docTypeChart) {
        initializeDashboardCharts(ratingChart, docTypeChart);
    }
    
    // Initialize any feedback forms on the page
    initializeFeedbackForms();
});

/**
 * Initialize dashboard charts
 */
function initializeDashboardCharts(ratingChart, docTypeChart) {
    // Rating distribution chart
    if (ratingChart) {
        try {
            const ratingData = JSON.parse(ratingChart.dataset.ratings);
            new Chart(ratingChart, {
                type: 'bar',
                data: {
                    labels: Object.keys(ratingData),
                    datasets: [{
                        label: 'Rating Distribution',
                        data: Object.values(ratingData),
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.5)',
                            'rgba(255, 159, 64, 0.5)',
                            'rgba(255, 205, 86, 0.5)',
                            'rgba(75, 192, 192, 0.5)',
                            'rgba(54, 162, 235, 0.5)'
                        ],
                        borderColor: [
                            'rgb(255, 99, 132)',
                            'rgb(255, 159, 64)',
                            'rgb(255, 205, 86)',
                            'rgb(75, 192, 192)',
                            'rgb(54, 162, 235)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                }
            });
        } catch (e) {
            console.error('Error initializing rating chart:', e);
        }
    }
    
    // Document type chart
    if (docTypeChart) {
        try {
            const docTypeData = JSON.parse(docTypeChart.dataset.counts);
            new Chart(docTypeChart, {
                type: 'pie',
                data: {
                    labels: Object.keys(docTypeData),
                    datasets: [{
                        label: 'Document Types',
                        data: Object.values(docTypeData),
                        backgroundColor: [
                            'rgba(54, 162, 235, 0.5)',
                            'rgba(75, 192, 192, 0.5)',
                            'rgba(255, 205, 86, 0.5)',
                            'rgba(255, 99, 132, 0.5)'
                        ],
                        borderColor: [
                            'rgb(54, 162, 235)',
                            'rgb(75, 192, 192)',
                            'rgb(255, 205, 86)',
                            'rgb(255, 99, 132)'
                        ],
                        borderWidth: 1
                    }]
                }
            });
        } catch (e) {
            console.error('Error initializing document type chart:', e);
        }
    }
}

/**
 * Initialize feedback form rating stars and submission
 */
function initializeFeedbackForms() {
    // Find all feedback forms on the page
    document.querySelectorAll('.ai-feedback-form').forEach(form => {
        const stars = form.querySelectorAll('.rating-star');
        const ratingInput = form.querySelector('input[name="rating"]');
        const submitButton = form.querySelector('button[type="submit"]');
        const thankYouMessage = form.querySelector('.feedback-thank-you');
        
        // Star rating functionality
        stars.forEach(star => {
            // Set initial state
            if (ratingInput.value >= star.dataset.rating) {
                star.classList.add('active');
            }
            
            // Handle click events
            star.addEventListener('click', function() {
                const rating = parseInt(this.dataset.rating);
                ratingInput.value = rating;
                
                // Update star appearance
                stars.forEach(s => {
                    if (parseInt(s.dataset.rating) <= rating) {
                        s.classList.add('active');
                    } else {
                        s.classList.remove('active');
                    }
                });
                
                // Enable submit if a rating is selected
                if (submitButton) {
                    submitButton.disabled = false;
                }
            });
        });
        
        // Handle form submission via AJAX
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            fetch('/api/feedback/submit', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Hide form, show thank you message
                    form.querySelector('.form-content').style.display = 'none';
                    if (thankYouMessage) {
                        thankYouMessage.style.display = 'block';
                    }
                } else {
                    alert('Error submitting feedback: ' + (data.message || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error submitting feedback:', error);
                alert('Error submitting feedback. Please try again.');
            });
        });
    });
}
