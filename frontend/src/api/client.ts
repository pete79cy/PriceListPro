import axios from 'axios';

// Configure Axios instance
const apiClient = axios.create({
  baseURL: process.env.NODE_ENV === 'production' 
    ? '/api' 
    : 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for handling cookies/sessions
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    // Handle errors here (e.g., refresh token, redirect to login, etc.)
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  // Check if user is authenticated
  checkAuth: async () => {
    try {
      const response = await apiClient.get('/auth/status');
      return response;
    } catch (error) {
      return { authenticated: false, user: null };
    }
  },

  // Login
  login: async (username: string, password: string) => {
    const response = await apiClient.post('/auth/login', { username, password });
    return response;
  },

  // Logout
  logout: async () => {
    const response = await apiClient.post('/auth/logout');
    return response;
  },
};

// Customer API
export const customerAPI = {
  // Get all customers
  getCustomers: async (params = {}) => {
    const response = await apiClient.get('/customers', { params });
    return response;
  },

  // Get customer by ID
  getCustomer: async (id: number) => {
    const response = await apiClient.get(`/customers/${id}`);
    return response;
  },

  // Create customer
  createCustomer: async (customerData: any) => {
    const response = await apiClient.post('/customers', customerData);
    return response;
  },

  // Update customer
  updateCustomer: async (id: number, customerData: any) => {
    const response = await apiClient.put(`/customers/${id}`, customerData);
    return response;
  },

  // Delete customer
  deleteCustomer: async (id: number) => {
    const response = await apiClient.delete(`/customers/${id}`);
    return response;
  },
};

// Product API
export const productAPI = {
  // Get all products
  getProducts: async (params = {}) => {
    const response = await apiClient.get('/products', { params });
    return response;
  },

  // Get product by ID
  getProduct: async (id: number) => {
    const response = await apiClient.get(`/products/${id}`);
    return response;
  },

  // Create product
  createProduct: async (productData: any) => {
    const response = await apiClient.post('/products', productData);
    return response;
  },

  // Update product
  updateProduct: async (id: number, productData: any) => {
    const response = await apiClient.put(`/products/${id}`, productData);
    return response;
  },

  // Delete product
  deleteProduct: async (id: number) => {
    const response = await apiClient.delete(`/products/${id}`);
    return response;
  },
};

// Price List API
export const priceListAPI = {
  // Get all price lists
  getPriceLists: async (params = {}) => {
    const response = await apiClient.get('/price-lists', { params });
    return response;
  },

  // Get customer-specific price lists
  getCustomerPriceLists: async (customerId: number, params = {}) => {
    const response = await apiClient.get(`/price-lists/customer/${customerId}`, { params });
    return response;
  },

  // Add product to customer price list
  addToPriceList: async (priceListData: any) => {
    const response = await apiClient.post('/price-lists', priceListData);
    return response;
  },

  // Update price list entry
  updatePriceList: async (id: number, priceListData: any) => {
    const response = await apiClient.put(`/price-lists/${id}`, priceListData);
    return response;
  },

  // Delete price list entry
  deletePriceList: async (id: number) => {
    const response = await apiClient.delete(`/price-lists/${id}`);
    return response;
  },

  // Get pending price updates
  getPendingUpdates: async () => {
    const response = await apiClient.get('/pending-updates');
    return response;
  },

  // Approve price update
  approveUpdate: async (updateId: number) => {
    const response = await apiClient.post(`/pending-updates/${updateId}/approve`);
    return response;
  },

  // Reject price update
  rejectUpdate: async (updateId: number) => {
    const response = await apiClient.post(`/pending-updates/${updateId}/reject`);
    return response;
  },
};

// Document API
export const documentAPI = {
  // Get all invoices
  getInvoices: async (params = {}) => {
    const response = await apiClient.get('/invoices', { params });
    return response;
  },

  // Get invoice by ID
  getInvoice: async (id: number) => {
    const response = await apiClient.get(`/invoices/${id}`);
    return response;
  },

  // Get all quotations
  getQuotations: async (params = {}) => {
    const response = await apiClient.get('/quotations', { params });
    return response;
  },

  // Get quotation by ID
  getQuotation: async (id: number) => {
    const response = await apiClient.get(`/quotations/${id}`);
    return response;
  },

  // Create quotation
  createQuotation: async (quotationData: any) => {
    const response = await apiClient.post('/quotations', quotationData);
    return response;
  },

  // Export quotation as PDF
  exportQuotation: async (id: number) => {
    // Using window.open for direct download
    window.open(`/api/quotations/${id}/export`, '_blank');
    return { success: true };
  },
};

// Search API
export const searchAPI = {
  // Global search
  search: async (query: string) => {
    const response = await apiClient.get('/search', { params: { q: query } });
    return response;
  },
};

export default apiClient;