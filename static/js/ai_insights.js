/**
 * AI Document Insights - JavaScript functionality
 * Provides real-time document analysis using OpenAI
 */

// AI Insights Handler Class
class AIInsightsHandler {
    constructor() {
        // UI Elements
        this.sidebar = document.getElementById('aiInsightsSidebar');
        this.showButton = document.getElementById('showAiInsights');
        this.closeButton = document.getElementById('closeAiInsights');
        this.refreshButton = document.getElementById('refreshAiInsights');
        this.loadingSpinner = document.getElementById('aiLoadingSpinner');
        this.errorMessage = document.getElementById('aiErrorMessage');
        this.errorText = document.getElementById('aiErrorText');
        this.apiMissing = document.getElementById('aiApiMissing');
        this.insightsContent = document.getElementById('aiInsightsContent');
        this.retryButton = document.getElementById('aiRetryButton');
        
        // Document-specific elements
        this.documentTitle = document.getElementById('aiDocumentTitle');
        this.documentMeta = document.getElementById('aiDocumentMeta');
        this.timestamp = document.getElementById('aiTimestamp');
        
        // Insights content sections
        this.keyObservationsContent = document.getElementById('aiKeyObservationsContent');
        this.pricingAnalysisContent = document.getElementById('aiPricingAnalysisContent');
        this.businessRecommendationsContent = document.getElementById('aiBusinessRecommendationsContent');
        this.otherInsights = document.getElementById('aiOtherInsights');
        
        // Current document context
        this.currentDocumentType = null;
        this.currentDocumentId = null;
        
        // Initialize event listeners
        this.initEventListeners();
        
        // Check if API key is configured
        this.checkAPIStatus();
    }
    
    // Set up event listeners
    initEventListeners() {
        if (this.showButton) {
            this.showButton.addEventListener('click', () => this.showSidebar());
        }
        
        if (this.closeButton) {
            this.closeButton.addEventListener('click', () => this.hideSidebar());
        }
        
        if (this.refreshButton) {
            this.refreshButton.addEventListener('click', () => this.refreshInsights());
        }
        
        if (this.retryButton) {
            this.retryButton.addEventListener('click', () => this.refreshInsights());
        }
        
        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.sidebar && this.sidebar.classList.contains('show')) {
                this.hideSidebar();
            }
        });
    }
    
    // Show the sidebar
    showSidebar() {
        if (this.sidebar) {
            this.sidebar.classList.add('show');
            if (this.showButton) {
                this.showButton.classList.add('d-none');
            }
            
            // Auto-refresh insights if needed
            if (this.currentDocumentId && !this.insightsLoaded) {
                this.refreshInsights();
            }
        }
    }
    
    // Hide the sidebar
    hideSidebar() {
        console.log('Hiding AI insights sidebar');
        if (this.sidebar) {
            // Force remove the show class
            this.sidebar.className = this.sidebar.className.replace(/\bshow\b/g, '');
            
            // Try an alternative approach as well
            document.getElementById('aiInsightsSidebar').classList.remove('show');
            
            if (this.showButton) {
                this.showButton.classList.remove('d-none');
            }
        } else {
            console.error('Sidebar element not found in hideSidebar()');
        }
    }
    
    // Toggle sidebar visibility
    toggleSidebar() {
        if (this.sidebar && this.sidebar.classList.contains('show')) {
            this.hideSidebar();
        } else {
            this.showSidebar();
        }
    }
    
    // Check if the OpenAI API is configured
    checkAPIStatus() {
        fetch('/ai-insights/status')
            .then(response => response.json())
            .then(data => {
                if (!data.enabled) {
                    this.showApiMissingMessage();
                } else if (this.showButton) {
                    // Only show the button if we have AI enabled
                    this.showButton.classList.remove('d-none');
                }
            })
            .catch(error => {
                console.error('Error checking AI status:', error);
            });
    }
    
    // Set the current document context
    setDocumentContext(type, id, title = null) {
        this.currentDocumentType = type;
        this.currentDocumentId = id;
        this.insightsLoaded = false;
        
        if (title && this.documentTitle) {
            this.documentTitle.textContent = title;
        }
        
        // Show the insights button if we have a valid document
        if (this.showButton && type && id) {
            this.showButton.classList.remove('d-none');
        }
    }
    
    // Refresh or load insights for the current document
    refreshInsights() {
        if (!this.currentDocumentType || !this.currentDocumentId) {
            console.error('No document context set');
            return;
        }
        
        this.showLoading();
        
        // Prepare request data
        const requestData = {
            document_type: this.currentDocumentType,
            document_id: this.currentDocumentId
        };
        
        // Send request to the server
        fetch('/ai-insights/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                if (data.error.includes('API key')) {
                    this.showApiMissingMessage();
                } else {
                    this.showErrorMessage(data.error);
                }
            } else {
                this.displayInsights(data);
                this.insightsLoaded = true;
            }
        })
        .catch(error => {
            console.error('Error fetching insights:', error);
            this.showErrorMessage('Network error while fetching insights. Please try again.');
        });
    }
    
    // Display the insights in the sidebar
    displayInsights(data) {
        // Hide loading and error states
        this.hideLoading();
        this.hideError();
        this.hideApiMissingMessage();
        
        // Show insights content
        if (this.insightsContent) {
            this.insightsContent.classList.remove('d-none');
        }
        
        // Set timestamp
        if (this.timestamp) {
            const date = new Date(data.timestamp);
            this.timestamp.textContent = date.toLocaleString();
        }
        
        // Populate standard insight sections
        if (data.insights) {
            const insights = data.insights;
            
            // Key observations (might be under different names)
            if (insights.key_observations && this.keyObservationsContent) {
                this.keyObservationsContent.textContent = insights.key_observations;
                document.getElementById('aiKeyObservations').classList.remove('d-none');
            } else {
                document.getElementById('aiKeyObservations').classList.add('d-none');
            }
            
            // Pricing analysis
            if (insights.pricing_analysis && this.pricingAnalysisContent) {
                this.pricingAnalysisContent.textContent = insights.pricing_analysis;
                document.getElementById('aiPricingAnalysis').classList.remove('d-none');
            } else {
                document.getElementById('aiPricingAnalysis').classList.add('d-none');
            }
            
            // Business recommendations
            if (insights.business_recommendations && this.businessRecommendationsContent) {
                this.businessRecommendationsContent.textContent = insights.business_recommendations;
                document.getElementById('aiBusinessRecommendations').classList.remove('d-none');
            } else {
                document.getElementById('aiBusinessRecommendations').classList.add('d-none');
            }
            
            // Add any other insights that don't fit the standard categories
            if (this.otherInsights) {
                this.otherInsights.innerHTML = '';
                
                for (const [key, value] of Object.entries(insights)) {
                    // Skip the ones we've already handled
                    if (['key_observations', 'pricing_analysis', 'business_recommendations', 'overview'].includes(key)) {
                        continue;
                    }
                    
                    // Create a new section for this insight
                    const section = document.createElement('div');
                    section.className = 'ai-insight-section';
                    
                    // Format the title (convert snake_case to Title Case)
                    const title = key.split('_')
                        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                        .join(' ');
                    
                    // Add the icon based on the insight type
                    let icon = 'fas fa-info-circle';
                    if (key.includes('data')) icon = 'fas fa-database';
                    if (key.includes('customer')) icon = 'fas fa-users';
                    if (key.includes('price') || key.includes('cost')) icon = 'fas fa-tag';
                    if (key.includes('trend') || key.includes('pattern')) icon = 'fas fa-chart-line';
                    if (key.includes('suggest') || key.includes('recommend')) icon = 'fas fa-lightbulb';
                    
                    section.innerHTML = `
                        <h6><i class="${icon} me-2"></i> ${title}</h6>
                        <div class="ai-insight-content">${value}</div>
                    `;
                    
                    this.otherInsights.appendChild(section);
                }
            }
        }
    }
    
    // Show loading spinner
    showLoading() {
        if (this.loadingSpinner) {
            this.loadingSpinner.classList.remove('d-none');
        }
        if (this.errorMessage) {
            this.errorMessage.classList.add('d-none');
        }
        if (this.insightsContent) {
            this.insightsContent.classList.add('d-none');
        }
        if (this.apiMissing) {
            this.apiMissing.classList.add('d-none');
        }
    }
    
    // Hide loading spinner
    hideLoading() {
        if (this.loadingSpinner) {
            this.loadingSpinner.classList.add('d-none');
        }
    }
    
    // Show error message
    showErrorMessage(message) {
        this.hideLoading();
        if (this.errorMessage) {
            this.errorMessage.classList.remove('d-none');
        }
        if (this.errorText) {
            this.errorText.textContent = message;
        }
        if (this.insightsContent) {
            this.insightsContent.classList.add('d-none');
        }
    }
    
    // Hide error message
    hideError() {
        if (this.errorMessage) {
            this.errorMessage.classList.add('d-none');
        }
    }
    
    // Show API missing message
    showApiMissingMessage() {
        this.hideLoading();
        this.hideError();
        if (this.apiMissing) {
            this.apiMissing.classList.remove('d-none');
        }
        if (this.insightsContent) {
            this.insightsContent.classList.add('d-none');
        }
    }
    
    // Hide API missing message
    hideApiMissingMessage() {
        if (this.apiMissing) {
            this.apiMissing.classList.add('d-none');
        }
    }
}

// Initialize on DOM content loaded
document.addEventListener('DOMContentLoaded', () => {
    // Create global AI insights instance
    window.aiInsights = new AIInsightsHandler();
});