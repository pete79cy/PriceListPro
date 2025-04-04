import React, { useState, useContext } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert } from 'react-bootstrap';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { AuthContext } from '../App';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);

  // Form validation
  const validateForm = (): boolean => {
    setError(null);
    
    if (!username.trim()) {
      setError('Username is required');
      return false;
    }
    
    if (!password.trim()) {
      setError('Password is required');
      return false;
    }
    
    return true;
  };

  // Handle login
  const handleLogin = async () => {
    // Validate form
    if (!validateForm()) {
      return;
    }
    
    try {
      setLoading(true);
      
      // Call login function from AuthContext
      const success = await login(username, password);
      
      if (success) {
        // Redirect to dashboard on successful login
        navigate('/dashboard');
      } else {
        setError('Invalid username or password. Please try again.');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError('An error occurred during login. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleLogin();
  };

  return (
    <Container className="py-5">
      <Row className="justify-content-center">
        <Col md={6} lg={5}>
          <Card>
            <Card.Header className="bg-primary text-white text-center">
              <h3 className="m-0">Login</h3>
            </Card.Header>
            <Card.Body>
              {error && (
                <Alert variant="danger">{error}</Alert>
              )}
              
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>Username</Form.Label>
                  <Form.Control
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Enter your username"
                    disabled={loading}
                  />
                </Form.Group>
                
                <Form.Group className="mb-4">
                  <Form.Label>Password</Form.Label>
                  <Form.Control
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    disabled={loading}
                  />
                </Form.Group>
                
                <div className="d-grid">
                  <Button variant="primary" type="submit" disabled={loading}>
                    {loading ? 'Logging in...' : 'Login'}
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Login;