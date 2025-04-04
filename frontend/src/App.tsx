import React, { createContext, useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import axios from 'axios';

// Components
import AppNavbar from './components/Navbar';
import Footer from './components/Footer';

// Pages
import Home from './pages/Home';
import Login from './pages/Login';

// API client
import { authAPI } from './api/client';

// Create authentication context
interface AuthContextType {
  isAuthenticated: boolean;
  user: any | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  user: null,
  loading: true,
  login: async () => false,
  logout: async () => {},
});

// Auth provider component
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check authentication status when the app loads
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const data = await authAPI.checkAuth();
        if (data.authenticated) {
          setUser(data.user);
          setIsAuthenticated(true);
        } else {
          setUser(null);
          setIsAuthenticated(false);
        }
      } catch (error) {
        console.error('Failed to check authentication status:', error);
        setUser(null);
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  // Login function
  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      const data = await authAPI.login(username, password);
      if (data.success) {
        setUser(data.user);
        setIsAuthenticated(true);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  // Logout function
  const logout = async (): Promise<void> => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  // Context value
  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Route guard for protected routes
interface ProtectedRouteProps {
  element: React.ReactNode;
  isAuthenticated: boolean;
  loading: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ element, isAuthenticated, loading }) => {
  const location = useLocation();

  if (loading) {
    return <div className="loading-spinner">Loading...</div>;
  }

  return isAuthenticated ? (
    <>{element}</>
  ) : (
    <Navigate to="/login" state={{ from: location }} replace />
  );
};

// Layout wrapper with navigation and footer
interface LayoutProps {
  isAuthenticated: boolean;
  logout: () => void;
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ isAuthenticated, logout, children }) => {
  return (
    <div className="d-flex flex-column min-vh-100">
      <AppNavbar isAuthenticated={isAuthenticated} logout={logout} />
      
      <main className="flex-grow-1">
        {children}
      </main>
      
      <Footer />
    </div>
  );
};

// Main App component
const App: React.FC = () => {
  return (
    <Router>
      <AuthProvider>
        <AuthContext.Consumer>
          {({ isAuthenticated, loading, logout }) => (
            <Layout isAuthenticated={isAuthenticated} logout={logout}>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/login" element={<Login />} />
                
                {/* Protected routes - will be expanded as more pages are added */}
                <Route 
                  path="/dashboard" 
                  element={
                    <ProtectedRoute 
                      element={<div>Dashboard Content (To be implemented)</div>} 
                      isAuthenticated={isAuthenticated}
                      loading={loading}
                    />
                  } 
                />
                
                {/* Catch-all route */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Layout>
          )}
        </AuthContext.Consumer>
      </AuthProvider>
    </Router>
  );
};

export default App;