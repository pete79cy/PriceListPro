import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';

// Import components
import Navbar from './components/Navbar';
import Footer from './components/Footer';

// Import pages
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';

// Import Bootstrap CSS
import 'bootstrap/dist/css/bootstrap.min.css';

// Define types
interface User {
  id: number;
  username: string;
  is_admin: boolean;
}

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  loading: boolean;
}

// Create AuthContext
export const AuthContext = React.createContext<{
  authState: AuthState;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
}>({
  authState: {
    isAuthenticated: false,
    user: null,
    loading: true
  },
  login: async () => false,
  logout: () => {}
});

const App: React.FC = () => {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    loading: true
  });

  // Check if user is already authenticated
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const res = await axios.get('/api/auth/user', { withCredentials: true });
        if (res.data.authenticated) {
          setAuthState({
            isAuthenticated: true,
            user: res.data.user,
            loading: false
          });
        } else {
          setAuthState({
            isAuthenticated: false,
            user: null,
            loading: false
          });
        }
      } catch (err) {
        console.error('Error checking auth status:', err);
        setAuthState({
          isAuthenticated: false,
          user: null,
          loading: false
        });
      }
    };

    checkAuthStatus();
  }, []);

  // Login function
  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      const res = await axios.post('/login', { username, password }, {
        headers: { 'Content-Type': 'application/json' },
        withCredentials: true
      });
      
      if (res.status === 200) {
        const userRes = await axios.get('/api/auth/user', { withCredentials: true });
        setAuthState({
          isAuthenticated: true,
          user: userRes.data.user,
          loading: false
        });
        return true;
      }
      return false;
    } catch (err) {
      console.error('Login error:', err);
      return false;
    }
  };

  // Logout function
  const logout = async () => {
    try {
      await axios.get('/logout', { withCredentials: true });
      setAuthState({
        isAuthenticated: false,
        user: null,
        loading: false
      });
    } catch (err) {
      console.error('Logout error:', err);
    }
  };

  // Protected route component
  const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
    if (authState.loading) {
      return <div>Loading...</div>;
    }
    
    if (!authState.isAuthenticated) {
      return <Navigate to="/login" />;
    }
    
    return <>{children}</>;
  };

  return (
    <AuthContext.Provider value={{ authState, login, logout }}>
      <Router>
        <div className="d-flex flex-column min-vh-100">
          <Navbar />
          <main className="flex-grow-1">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/dashboard" element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } />
              {/* Add more routes as needed */}
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </AuthContext.Provider>
  );
};

export default App;