import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Navbar as BootstrapNavbar, Nav, Container, Form, FormControl, Button, Dropdown } from 'react-bootstrap';
import { FaLeaf, FaSearch, FaUser, FaSignOutAlt, FaBox, FaClipboardList, FaFileInvoice, FaUserFriends, FaChartLine, FaQuestionCircle } from 'react-icons/fa';

/**
 * Main navigation component
 * Displays differently based on authentication status
 */
const Navbar: React.FC<{
  isAuthenticated: boolean;
  logout: () => void;
}> = ({ isAuthenticated, logout }) => {
  const location = useLocation();
  const [searchQuery, setSearchQuery] = useState('');

  // Handle search submit
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      window.location.href = `/search?q=${encodeURIComponent(searchQuery.trim())}`;
    }
  };

  return (
    <BootstrapNavbar bg="white" expand="lg" className="shadow-sm py-2 mb-4" sticky="top">
      <Container>
        {/* Brand */}
        <BootstrapNavbar.Brand as={Link} to="/" className="d-flex align-items-center">
          <FaLeaf className="text-primary me-2" size={24} />
          <span className="fw-bold">Plant Pricing Manager</span>
        </BootstrapNavbar.Brand>

        <BootstrapNavbar.Toggle aria-controls="responsive-navbar-nav" />
        
        <BootstrapNavbar.Collapse id="responsive-navbar-nav">
          {isAuthenticated ? (
            <>
              {/* Main Navigation Links */}
              <Nav className="me-auto">
                <Nav.Link 
                  as={Link} 
                  to="/dashboard" 
                  active={location.pathname === '/dashboard'}
                  className="d-flex align-items-center"
                >
                  <FaChartLine className="me-1" /> Dashboard
                </Nav.Link>
                
                <Nav.Link 
                  as={Link} 
                  to="/products" 
                  active={location.pathname === '/products'}
                  className="d-flex align-items-center"
                >
                  <FaBox className="me-1" /> Products
                </Nav.Link>
                
                <Nav.Link 
                  as={Link} 
                  to="/customers" 
                  active={location.pathname === '/customers'}
                  className="d-flex align-items-center"
                >
                  <FaUserFriends className="me-1" /> Customers
                </Nav.Link>
                
                <Nav.Link 
                  as={Link} 
                  to="/price-lists" 
                  active={location.pathname === '/price-lists'}
                  className="d-flex align-items-center"
                >
                  <FaClipboardList className="me-1" /> Price Lists
                </Nav.Link>
                
                <Nav.Link 
                  as={Link} 
                  to="/quotations" 
                  active={location.pathname === '/quotations'}
                  className="d-flex align-items-center"
                >
                  <FaFileInvoice className="me-1" /> Quotations
                </Nav.Link>
                
                <Nav.Link 
                  as={Link} 
                  to="/invoices" 
                  active={location.pathname === '/invoices'}
                  className="d-flex align-items-center"
                >
                  <FaFileInvoice className="me-1" /> Invoices
                </Nav.Link>
              </Nav>
              
              {/* Search Form */}
              <Form className="d-flex mx-auto" onSubmit={handleSearchSubmit}>
                <FormControl
                  type="search"
                  placeholder="Search products, customers..."
                  className="me-2"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                <Button variant="outline-primary" type="submit">
                  <FaSearch />
                </Button>
              </Form>
              
              {/* User Menu */}
              <Nav>
                <Dropdown align="end">
                  <Dropdown.Toggle variant="light" id="user-dropdown" className="d-flex align-items-center">
                    <FaUser className="me-1" /> Account
                  </Dropdown.Toggle>
                  
                  <Dropdown.Menu>
                    <Dropdown.Item as={Link} to="/settings">
                      <FaUser className="me-2" /> Account Settings
                    </Dropdown.Item>
                    <Dropdown.Item as={Link} to="/company-settings">
                      <FaChartLine className="me-2" /> Company Settings
                    </Dropdown.Item>
                    <Dropdown.Divider />
                    <Dropdown.Item as={Link} to="/help">
                      <FaQuestionCircle className="me-2" /> Help & Documentation
                    </Dropdown.Item>
                    <Dropdown.Divider />
                    <Dropdown.Item onClick={logout}>
                      <FaSignOutAlt className="me-2" /> Logout
                    </Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>
              </Nav>
            </>
          ) : (
            <Nav className="ms-auto">
              <Nav.Link as={Link} to="/login" className="d-flex align-items-center">
                <FaUser className="me-1" /> Login
              </Nav.Link>
            </Nav>
          )}
        </BootstrapNavbar.Collapse>
      </Container>
    </BootstrapNavbar>
  );
};

export default Navbar;