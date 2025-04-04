import React, { useState, useEffect, useContext } from 'react';
import { Container, Row, Col, Card, Alert, Table, Button } from 'react-bootstrap';
import apiClient from '../api/client';
import { AuthContext } from '../App';

// Define types for dashboard data
interface DashboardStats {
  customerCount: number;
  productCount: number;
  quotationCount: number;
  invoiceCount: number;
  pendingUpdateCount: number;
}

interface RecentQuotation {
  id: number;
  quotation_number: string;
  customer_name: string;
  quotation_date: string;
  total_amount: number;
}

interface RecentInvoice {
  id: number;
  invoice_number: string;
  customer_name: string;
  invoice_date: string;
  total_amount: number;
}

const Dashboard: React.FC = () => {
  const { authState } = useContext(AuthContext);
  const [stats, setStats] = useState<DashboardStats>({
    customerCount: 0,
    productCount: 0,
    quotationCount: 0,
    invoiceCount: 0,
    pendingUpdateCount: 0
  });
  const [recentQuotations, setRecentQuotations] = useState<RecentQuotation[]>([]);
  const [recentInvoices, setRecentInvoices] = useState<RecentInvoice[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Fetch various stats
        const [customersRes, productsRes, quotationsRes, invoicesRes] = await Promise.all([
          apiClient.get('/customers'),
          apiClient.get('/products'),
          apiClient.get('/quotations'),
          apiClient.get('/invoices')
        ]);

        // Fetch recent quotations and invoices
        const recentQuotationsData = quotationsRes.data.quotations.slice(0, 5);
        const recentInvoicesData = invoicesRes.data.invoices.slice(0, 5);

        setStats({
          customerCount: customersRes.data.customers.length,
          productCount: productsRes.data.products.length,
          quotationCount: quotationsRes.data.quotations.length,
          invoiceCount: invoicesRes.data.invoices.length,
          pendingUpdateCount: 0 // We'll update this once we have a proper endpoint
        });

        setRecentQuotations(recentQuotationsData);
        setRecentInvoices(recentInvoicesData);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again later.');
        setLoading(false);
      }
    };

    if (authState.isAuthenticated) {
      fetchDashboardData();
    }
  }, [authState.isAuthenticated]);

  if (loading) {
    return (
      <Container className="py-4">
        <Alert variant="info">Loading dashboard data...</Alert>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="py-4">
        <Alert variant="danger">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container className="py-4">
      <h1 className="mb-4">Dashboard</h1>
      
      {/* Stats Cards */}
      <Row className="mb-4">
        <Col md={3} sm={6} className="mb-3">
          <Card className="text-center h-100">
            <Card.Body>
              <Card.Title>{stats.customerCount}</Card.Title>
              <Card.Text>Customers</Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3} sm={6} className="mb-3">
          <Card className="text-center h-100">
            <Card.Body>
              <Card.Title>{stats.productCount}</Card.Title>
              <Card.Text>Products</Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3} sm={6} className="mb-3">
          <Card className="text-center h-100">
            <Card.Body>
              <Card.Title>{stats.quotationCount}</Card.Title>
              <Card.Text>Quotations</Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3} sm={6} className="mb-3">
          <Card className="text-center h-100">
            <Card.Body>
              <Card.Title>{stats.invoiceCount}</Card.Title>
              <Card.Text>Invoices</Card.Text>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Recent Quotations */}
      <Card className="mb-4">
        <Card.Header className="d-flex justify-content-between align-items-center">
          <h5 className="mb-0">Recent Quotations</h5>
          <Button size="sm" variant="outline-primary" href="/quotations">View All</Button>
        </Card.Header>
        <Card.Body>
          {recentQuotations.length > 0 ? (
            <Table responsive hover>
              <thead>
                <tr>
                  <th>Number</th>
                  <th>Customer</th>
                  <th>Date</th>
                  <th>Amount</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {recentQuotations.map((quotation) => (
                  <tr key={quotation.id}>
                    <td>{quotation.quotation_number}</td>
                    <td>{quotation.customer_name}</td>
                    <td>{new Date(quotation.quotation_date).toLocaleDateString()}</td>
                    <td>€{quotation.total_amount?.toFixed(2) || '0.00'}</td>
                    <td>
                      <Button size="sm" variant="outline-primary" href={`/quotations/${quotation.id}`}>View</Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          ) : (
            <p className="mb-0">No recent quotations found.</p>
          )}
        </Card.Body>
      </Card>

      {/* Recent Invoices */}
      <Card>
        <Card.Header className="d-flex justify-content-between align-items-center">
          <h5 className="mb-0">Recent Invoices</h5>
          <Button size="sm" variant="outline-primary" href="/invoices">View All</Button>
        </Card.Header>
        <Card.Body>
          {recentInvoices.length > 0 ? (
            <Table responsive hover>
              <thead>
                <tr>
                  <th>Number</th>
                  <th>Customer</th>
                  <th>Date</th>
                  <th>Amount</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {recentInvoices.map((invoice) => (
                  <tr key={invoice.id}>
                    <td>{invoice.invoice_number}</td>
                    <td>{invoice.customer_name}</td>
                    <td>{new Date(invoice.invoice_date).toLocaleDateString()}</td>
                    <td>€{invoice.total_amount?.toFixed(2) || '0.00'}</td>
                    <td>
                      <Button size="sm" variant="outline-primary" href={`/invoices/${invoice.id}`}>View</Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          ) : (
            <p className="mb-0">No recent invoices found.</p>
          )}
        </Card.Body>
      </Card>
    </Container>
  );
};

export default Dashboard;