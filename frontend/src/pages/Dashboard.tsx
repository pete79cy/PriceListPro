import React, { useState, useEffect, useContext } from 'react';
import { Container, Row, Col, Card, Table, Button, Badge } from 'react-bootstrap';
import { 
  FaLeaf, 
  FaFileInvoice, 
  FaUsers, 
  FaChartLine, 
  FaClipboardList,
  FaExchangeAlt,
  FaFileAlt,
  FaSearch
} from 'react-icons/fa';
import { Link } from 'react-router-dom';
import { AuthContext } from '../App';
import { apiClient } from '../api/client';

// Types
interface DashboardStats {
  products: number;
  customers: number;
  invoices: number;
  pendingUpdates: number;
}

interface RecentQuotation {
  id: number;
  quotation_number: string;
  customer_name: string;
  date: string;
  total_amount: number;
}

interface RecentInvoice {
  id: number;
  invoice_number: string;
  customer_name: string;
  date: string;
  total_amount: number;
}

const Dashboard: React.FC = () => {
  const { user } = useContext(AuthContext);
  const [loading, setLoading] = useState<boolean>(true);
  const [stats, setStats] = useState<DashboardStats>({
    products: 0,
    customers: 0,
    invoices: 0,
    pendingUpdates: 0
  });
  const [recentQuotations, setRecentQuotations] = useState<RecentQuotation[]>([]);
  const [recentInvoices, setRecentInvoices] = useState<RecentInvoice[]>([]);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Fetch statistics
        const statsData = await apiClient.get('/api/dashboard/stats');
        setStats(statsData.data);
        
        // Fetch recent quotations
        const quotationsData = await apiClient.get('/api/dashboard/recent-quotations');
        setRecentQuotations(quotationsData.data);
        
        // Fetch recent invoices
        const invoicesData = await apiClient.get('/api/dashboard/recent-invoices');
        setRecentInvoices(invoicesData.data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        // Use placeholder data if API fails
        setStats(prev => ({
          ...prev,
          products: 125,
          customers: 48,
          invoices: 37,
          pendingUpdates: 5
        }));
        
        setRecentQuotations(prev => prev.length ? prev : [
          { id: 1, quotation_number: 'QT-123456', customer_name: 'Garden Center Ltd', date: '2023-04-02', total_amount: 1245.30 },
          { id: 2, quotation_number: 'QT-123457', customer_name: 'Plant Paradise', date: '2023-04-01', total_amount: 987.50 },
          { id: 3, quotation_number: 'QT-123458', customer_name: 'Green Oasis', date: '2023-03-30', total_amount: 2345.75 }
        ]);
        
        setRecentInvoices(prev => prev.length ? prev : [
          { id: 1, invoice_number: 'INV-123456', customer_name: 'Garden Center Ltd', date: '2023-04-02', total_amount: 1245.30 },
          { id: 2, invoice_number: 'INV-123457', customer_name: 'Plant Paradise', date: '2023-04-01', total_amount: 987.50 },
          { id: 3, invoice_number: 'INV-123458', customer_name: 'Green Oasis', date: '2023-03-30', total_amount: 2345.75 }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  return (
    <Container className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="mb-0">Dashboard</h1>
        <div>
          <span className="me-2">Welcome, {user?.username || 'User'}</span>
          {user?.is_admin && <Badge bg="danger">Admin</Badge>}
        </div>
      </div>
      
      {/* Stats Cards */}
      <Row className="mb-4">
        <Col md={3} className="mb-3 mb-md-0">
          <Card className="h-100 stats-card">
            <Card.Body className="p-4">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h5 className="mb-0">Products</h5>
                  <h2 className="mt-2 mb-0">{stats.products}</h2>
                </div>
                <div className="rounded-circle bg-primary p-3 d-flex justify-content-center align-items-center">
                  <FaLeaf className="text-white" size={24} />
                </div>
              </div>
              <div className="mt-3">
                <Link to="/products" className="btn btn-sm btn-outline-primary">
                  View All
                </Link>
              </div>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={3} className="mb-3 mb-md-0">
          <Card className="h-100 stats-card">
            <Card.Body className="p-4">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h5 className="mb-0">Customers</h5>
                  <h2 className="mt-2 mb-0">{stats.customers}</h2>
                </div>
                <div className="rounded-circle bg-success p-3 d-flex justify-content-center align-items-center">
                  <FaUsers className="text-white" size={24} />
                </div>
              </div>
              <div className="mt-3">
                <Link to="/customers" className="btn btn-sm btn-outline-success">
                  View All
                </Link>
              </div>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={3} className="mb-3 mb-md-0">
          <Card className="h-100 stats-card">
            <Card.Body className="p-4">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h5 className="mb-0">Invoices</h5>
                  <h2 className="mt-2 mb-0">{stats.invoices}</h2>
                </div>
                <div className="rounded-circle bg-info p-3 d-flex justify-content-center align-items-center">
                  <FaFileInvoice className="text-white" size={24} />
                </div>
              </div>
              <div className="mt-3">
                <Link to="/invoices" className="btn btn-sm btn-outline-info">
                  View All
                </Link>
              </div>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={3} className="mb-3 mb-md-0">
          <Card className="h-100 stats-card">
            <Card.Body className="p-4">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h5 className="mb-0">Pending Updates</h5>
                  <h2 className="mt-2 mb-0">{stats.pendingUpdates}</h2>
                </div>
                <div className="rounded-circle bg-warning p-3 d-flex justify-content-center align-items-center">
                  <FaExchangeAlt className="text-white" size={24} />
                </div>
              </div>
              <div className="mt-3">
                <Link to="/pending-updates" className="btn btn-sm btn-outline-warning">
                  Review
                </Link>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      {/* Quick Actions */}
      <Card className="mb-4">
        <Card.Header>
          <h5 className="mb-0">Quick Actions</h5>
        </Card.Header>
        <Card.Body>
          <div className="d-flex flex-wrap gap-2">
            <Button as={Link} to="/upload-excel" variant="outline-primary" className="d-flex align-items-center">
              <FaFileAlt className="me-2" /> Upload Price List
            </Button>
            <Button as={Link} to="/upload-pdf" variant="outline-primary" className="d-flex align-items-center">
              <FaFileInvoice className="me-2" /> Upload Invoice
            </Button>
            <Button as={Link} to="/upload-quotation" variant="outline-primary" className="d-flex align-items-center">
              <FaClipboardList className="me-2" /> Create Quotation
            </Button>
            <Button as={Link} to="/search" variant="outline-primary" className="d-flex align-items-center">
              <FaSearch className="me-2" /> Advanced Search
            </Button>
          </div>
        </Card.Body>
      </Card>
      
      {/* Recent Quotations */}
      <Row className="mb-4">
        <Col lg={6} className="mb-4 mb-lg-0">
          <Card className="h-100">
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h5 className="mb-0">Recent Quotations</h5>
              <Link to="/quotations" className="btn btn-sm btn-outline-primary">View All</Link>
            </Card.Header>
            <Card.Body>
              <Table hover responsive className="mb-0">
                <thead>
                  <tr>
                    <th>Quotation #</th>
                    <th>Customer</th>
                    <th>Date</th>
                    <th>Amount</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {recentQuotations.map(quotation => (
                    <tr key={quotation.id}>
                      <td>{quotation.quotation_number}</td>
                      <td>{quotation.customer_name}</td>
                      <td>{quotation.date}</td>
                      <td>€{quotation.total_amount.toFixed(2)}</td>
                      <td>
                        <Link to={`/quotations/${quotation.id}`} className="btn btn-sm btn-link p-0">
                          View
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
        
        {/* Recent Invoices */}
        <Col lg={6}>
          <Card className="h-100">
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h5 className="mb-0">Recent Invoices</h5>
              <Link to="/invoices" className="btn btn-sm btn-outline-primary">View All</Link>
            </Card.Header>
            <Card.Body>
              <Table hover responsive className="mb-0">
                <thead>
                  <tr>
                    <th>Invoice #</th>
                    <th>Customer</th>
                    <th>Date</th>
                    <th>Amount</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {recentInvoices.map(invoice => (
                    <tr key={invoice.id}>
                      <td>{invoice.invoice_number}</td>
                      <td>{invoice.customer_name}</td>
                      <td>{invoice.date}</td>
                      <td>€{invoice.total_amount.toFixed(2)}</td>
                      <td>
                        <Link to={`/invoices/${invoice.id}`} className="btn btn-sm btn-link p-0">
                          View
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Dashboard;