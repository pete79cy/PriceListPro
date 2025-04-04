import React from 'react';
import { Container, Row, Col, Button, Card } from 'react-bootstrap';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <div>
      {/* Hero Section */}
      <section className="py-5 text-center bg-light">
        <Container>
          <h1 className="display-4">Plant Pricing System</h1>
          <p className="lead mb-4">
            A comprehensive solution for managing plant inventory, customer pricing, and quotations
          </p>
          <Link to="/login">
            <Button variant="primary" size="lg">Get Started</Button>
          </Link>
        </Container>
      </section>

      {/* Features Section */}
      <section className="py-5">
        <Container>
          <h2 className="text-center mb-5">Key Features</h2>
          <Row>
            <Col md={4} className="mb-4">
              <Card className="h-100">
                <Card.Body>
                  <Card.Title>Customer Management</Card.Title>
                  <Card.Text>
                    Easily manage customer information, contacts, and customer-specific pricing.
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
            <Col md={4} className="mb-4">
              <Card className="h-100">
                <Card.Body>
                  <Card.Title>Product Catalog</Card.Title>
                  <Card.Text>
                    Maintain a comprehensive plant catalog with scientific names, categories, and more.
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
            <Col md={4} className="mb-4">
              <Card className="h-100">
                <Card.Body>
                  <Card.Title>Price List Management</Card.Title>
                  <Card.Text>
                    Set up customer-specific price lists and manage pricing efficiently.
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
            <Col md={4} className="mb-4">
              <Card className="h-100">
                <Card.Body>
                  <Card.Title>Invoice Processing</Card.Title>
                  <Card.Text>
                    Generate and manage invoices, track payment status, and export as PDF.
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
            <Col md={4} className="mb-4">
              <Card className="h-100">
                <Card.Body>
                  <Card.Title>Quotation System</Card.Title>
                  <Card.Text>
                    Create professional quotations for customers with flexible terms.
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
            <Col md={4} className="mb-4">
              <Card className="h-100">
                <Card.Body>
                  <Card.Title>Supplier Management</Card.Title>
                  <Card.Text>
                    Keep track of suppliers, their products, and pricing information.
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Container>
      </section>

      {/* CTA Section */}
      <section className="py-5 bg-primary text-white text-center">
        <Container>
          <h2>Ready to streamline your plant pricing?</h2>
          <p className="lead mb-4">
            Get started today and experience the benefits of an integrated pricing system.
          </p>
          <Link to="/login">
            <Button variant="light" size="lg">Sign In Now</Button>
          </Link>
        </Container>
      </section>
    </div>
  );
};

export default Home;