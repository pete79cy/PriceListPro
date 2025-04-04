import React from 'react';
import { Container, Row, Col, Button, Card } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FaLeaf, FaBoxOpen, FaClipboardList, FaFileInvoice, FaUserFriends, FaChartLine } from 'react-icons/fa';

/**
 * Home page component
 */
const Home: React.FC = () => {
  return (
    <div>
      {/* Hero section */}
      <div className="bg-primary text-white py-5">
        <Container className="py-5">
          <Row className="align-items-center">
            <Col lg={6} className="mb-5 mb-lg-0">
              <h1 className="display-4 fw-bold mb-4">Streamline Your Plant Pricing Management</h1>
              <p className="lead mb-4">
                Efficiently manage your plant inventory, customer-specific pricing, and document generation with our all-in-one solution.
              </p>
              <div className="d-flex gap-3">
                <Button 
                  as={Link} 
                  to="/login" 
                  variant="light" 
                  size="lg" 
                  className="fw-bold"
                >
                  Get Started
                </Button>
                <Button 
                  as={Link} 
                  to="#features" 
                  variant="outline-light" 
                  size="lg"
                >
                  Learn More
                </Button>
              </div>
            </Col>
            <Col lg={6} className="text-center">
              <FaLeaf className="display-1 text-white" style={{ opacity: 0.8 }} />
            </Col>
          </Row>
        </Container>
      </div>

      {/* Features section */}
      <div className="py-5" id="features">
        <Container className="py-5">
          <Row className="text-center mb-5">
            <Col>
              <h2 className="display-5 fw-bold">Key Features</h2>
              <p className="lead text-muted">
                Everything you need to manage your plant inventory and pricing
              </p>
            </Col>
          </Row>
          
          <Row className="g-4">
            <Col md={4}>
              <Card className="h-100 shadow-sm border-0">
                <Card.Body className="p-4 text-center">
                  <div className="rounded-circle bg-primary p-3 d-inline-flex mb-3">
                    <FaBoxOpen className="text-white fs-2" />
                  </div>
                  <Card.Title className="fw-bold mb-3">Product Management</Card.Title>
                  <Card.Text className="text-muted">
                    Easily add, edit, and organize your plant inventory with detailed information including scientific names, categories, and pot sizes.
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
            
            <Col md={4}>
              <Card className="h-100 shadow-sm border-0">
                <Card.Body className="p-4 text-center">
                  <div className="rounded-circle bg-primary p-3 d-inline-flex mb-3">
                    <FaUserFriends className="text-white fs-2" />
                  </div>
                  <Card.Title className="fw-bold mb-3">Customer Management</Card.Title>
                  <Card.Text className="text-muted">
                    Maintain a comprehensive customer database with contact information and customer-specific pricing.
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
            
            <Col md={4}>
              <Card className="h-100 shadow-sm border-0">
                <Card.Body className="p-4 text-center">
                  <div className="rounded-circle bg-primary p-3 d-inline-flex mb-3">
                    <FaClipboardList className="text-white fs-2" />
                  </div>
                  <Card.Title className="fw-bold mb-3">Price Lists</Card.Title>
                  <Card.Text className="text-muted">
                    Create and manage customer-specific price lists with effective dates, ensuring accurate pricing for every customer.
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
            
            <Col md={4}>
              <Card className="h-100 shadow-sm border-0">
                <Card.Body className="p-4 text-center">
                  <div className="rounded-circle bg-primary p-3 d-inline-flex mb-3">
                    <FaFileInvoice className="text-white fs-2" />
                  </div>
                  <Card.Title className="fw-bold mb-3">Document Management</Card.Title>
                  <Card.Text className="text-muted">
                    Generate professional quotations and invoices, and extract data from uploaded documents with intelligent parsing.
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
            
            <Col md={4}>
              <Card className="h-100 shadow-sm border-0">
                <Card.Body className="p-4 text-center">
                  <div className="rounded-circle bg-primary p-3 d-inline-flex mb-3">
                    <FaChartLine className="text-white fs-2" />
                  </div>
                  <Card.Title className="fw-bold mb-3">Price Update Workflow</Card.Title>
                  <Card.Text className="text-muted">
                    Streamlined approval process for price updates, ensuring control over pricing changes across your inventory.
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
            
            <Col md={4}>
              <Card className="h-100 shadow-sm border-0 d-flex align-items-center justify-content-center">
                <Card.Body className="p-4 text-center">
                  <Link to="/login" className="btn btn-primary btn-lg">
                    Get Started Now
                  </Link>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Container>
      </div>
    </div>
  );
};

export default Home;