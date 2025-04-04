import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';

const Footer: React.FC = () => {
  return (
    <footer className="bg-dark text-light py-4 mt-auto">
      <Container>
        <Row>
          <Col md={4}>
            <h5>Plant Pricing System</h5>
            <p className="small">A modern system for managing plant inventory and pricing.</p>
          </Col>
          <Col md={4}>
            <h5>Quick Links</h5>
            <ul className="list-unstyled small">
              <li><a href="/" className="text-light">Home</a></li>
              <li><a href="/dashboard" className="text-light">Dashboard</a></li>
              <li><a href="/customers" className="text-light">Customers</a></li>
              <li><a href="/products" className="text-light">Products</a></li>
            </ul>
          </Col>
          <Col md={4}>
            <h5>Contact</h5>
            <p className="small">
              Email: info@plantpricing.com<br />
              Phone: +1 234 567 8901<br />
              Address: 123 Plant Street, Greenhouse City
            </p>
          </Col>
        </Row>
        <hr className="my-3" />
        <Row>
          <Col className="text-center">
            <p className="small mb-0">&copy; {new Date().getFullYear()} Plant Pricing System. All rights reserved.</p>
          </Col>
        </Row>
      </Container>
    </footer>
  );
};

export default Footer;