import api from './client';

// Auth services
export const authService = {
  login: (username: string, password: string) => 
    api.post('/api/login', { username, password }),
  
  logout: () => 
    api.post('/api/logout'),
  
  getCurrentUser: () => 
    api.get('/api/current-user')
};

// Product services
export const productService = {
  getProducts: (page = 1, limit = 10, search = '') => 
    api.get(`/api/products?page=${page}&limit=${limit}&search=${search}`),
  
  getProduct: (id: number) => 
    api.get(`/api/products/${id}`),
  
  createProduct: (data: any) => 
    api.post('/api/products', data),
  
  updateProduct: (id: number, data: any) => 
    api.put(`/api/products/${id}`, data),
  
  deleteProduct: (id: number) => 
    api.delete(`/api/products/${id}`)
};

// Customer services
export const customerService = {
  getCustomers: (page = 1, limit = 10, search = '') => 
    api.get(`/api/customers?page=${page}&limit=${limit}&search=${search}`),
  
  getCustomer: (id: number) => 
    api.get(`/api/customers/${id}`),
  
  createCustomer: (data: any) => 
    api.post('/api/customers', data),
  
  updateCustomer: (id: number, data: any) => 
    api.put(`/api/customers/${id}`, data),
  
  deleteCustomer: (id: number) => 
    api.delete(`/api/customers/${id}`)
};

// Price list services
export const priceListService = {
  getPriceLists: (page = 1, limit = 10, customerId = null, productId = null) => {
    let url = `/api/price-lists?page=${page}&limit=${limit}`;
    if (customerId) url += `&customer_id=${customerId}`;
    if (productId) url += `&product_id=${productId}`;
    return api.get(url);
  },
  
  getPriceList: (id: number) => 
    api.get(`/api/price-lists/${id}`),
  
  createPriceList: (data: any) => 
    api.post('/api/price-lists', data),
  
  updatePriceList: (id: number, data: any) => 
    api.put(`/api/price-lists/${id}`, data),
  
  deletePriceList: (id: number) => 
    api.delete(`/api/price-lists/${id}`)
};

// Invoice services
export const invoiceService = {
  getInvoices: (page = 1, limit = 10, customerId = null) => {
    let url = `/api/invoices?page=${page}&limit=${limit}`;
    if (customerId) url += `&customer_id=${customerId}`;
    return api.get(url);
  },
  
  getInvoice: (id: number) => 
    api.get(`/api/invoices/${id}`),
  
  createInvoice: (data: any) => 
    api.post('/api/invoices', data),
  
  updateInvoice: (id: number, data: any) => 
    api.put(`/api/invoices/${id}`, data),
  
  deleteInvoice: (id: number) => 
    api.delete(`/api/invoices/${id}`)
};

// Quotation services
export const quotationService = {
  getQuotations: (page = 1, limit = 10, customerId = null) => {
    let url = `/api/quotations?page=${page}&limit=${limit}`;
    if (customerId) url += `&customer_id=${customerId}`;
    return api.get(url);
  },
  
  getQuotation: (id: number) => 
    api.get(`/api/quotations/${id}`),
  
  createQuotation: (data: any) => 
    api.post('/api/quotations', data),
  
  updateQuotation: (id: number, data: any) => 
    api.put(`/api/quotations/${id}`, data),
  
  deleteQuotation: (id: number) => 
    api.delete(`/api/quotations/${id}`)
};

// Dashboard service
export const dashboardService = {
  getStats: () => 
    api.get('/api/dashboard/stats')
};

// AI Document service
export const aiDocumentService = {
  checkStatus: () => 
    api.get('/api/ai/status'),
  
  analyzeDocument: (documentId: number) => 
    api.post(`/api/analyze-document/${documentId}`)
};

export default {
  authService,
  productService,
  customerService,
  priceListService,
  invoiceService,
  quotationService,
  dashboardService,
  aiDocumentService
};
