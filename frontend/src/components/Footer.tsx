import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import { FaLeaf, FaGithub, FaEnvelope, FaPhone } from 'react-icons/fa';

/**
 * Footer component for the application
 */
const Footer: React.FC = () => {
  return (
    <footer className="bg-light py-4 mt-5">
      <Container>
        <Row className="align-items-center">
          <Col md={4} className="mb-3 mb-md-0">
            <div className="d-flex align-items-center">
              <FaLeaf className="text-primary me-2" size={20} />
              <span className="fw-bold text-primary">Plant Pricing Manager</span>
            </div>
            <p className="text-muted small mt-2 mb-0">
              Streamlining plant inventory and pricing management.
            </p>
          </Col>
          
          <Col md={4} className="mb-3 mb-md-0">
            <h6 className="text-uppercase fw-bold mb-3">Quick Links</h6>
            <ul className="list-unstyled mb-0">
              <li className="mb-2"><a href="/" className="text-decoration-none text-muted">Home</a></li>
              <li className="mb-2"><a href="/products" className="text-decoration-none text-muted">Products</a></li>
              <li className="mb-2"><a href="/customers" className="text-decoration-none text-muted">Customers</a></li>
              <li className="mb-2"><a href="/price-lists" className="text-decoration-none text-muted">Price Lists</a></li>
              <li className="mb-2"><a href="/quotations" className="text-decoration-none text-muted">Quotations</a></li>
              <li><a href="/invoices" className="text-decoration-none text-muted">Invoices</a></li>
            </ul>
          </Col>
          
          <Col md={4}>
            <h6 className="text-uppercase fw-bold mb-3">Contact</h6>
            <ul className="list-unstyled mb-0">
              <li className="mb-2">
                <FaEnvelope className="text-muted me-2" /> 
                <a href="mailto:support@plantpricing.com" className="text-decoration-none text-muted">
                  support@plantpricing.com
                </a>
              </li>
              <li className="mb-2">
                <FaPhone className="text-muted me-2" />
                <span className="text-muted">+1 (234) 567-8900</span>
              </li>
              <li>
                <FaGithub className="text-muted me-2" />
                <a href="https://github.com/plant-pricing" className="text-decoration-none text-muted">
                  GitHub
                </a>
              </li>
            </ul>
          </Col>
        </Row>
        
        <hr className="my-4" />
        
        <Row>
          <Col className="text-center text-muted small">
            <p className="mb-0">&copy; {new Date().getFullYear()} Plant Pricing Manager. All rights reserved.</p>
          </Col>
        </Row>
      </Container>
    </footer>
  );
};

export default Footer;