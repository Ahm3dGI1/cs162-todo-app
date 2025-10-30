import React, { useState, useEffect } from 'react';
import './App.css';
import Login from './components/Login';
import Register from './components/Register';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showRegister, setShowRegister] = useState(false);

  /**
   * Check if user is already logged in on component mount
   * This enables session persistence - if user refreshes page, they stay logged in
   */
  useEffect(() => {
    checkAuth();
  }, []);

  /**
   * Check authentication status by calling the /api/auth/current endpoint
   */
  const checkAuth = async () => {
    try {
      const response = await fetch('/api/auth/current', {
        credentials: 'include'  // Important: send cookies with request
      });
      
      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle successful login
   * Called by Login component after successful API call
   */
  const handleLogin = (userData) => {
    setUser(userData);
  };

  /**
   * Handle successful registration
   * Called by Register component after successful API call
   */
  const handleRegister = (userData) => {
    setUser(userData);
  };

  /**
   * Handle logout
   * Calls backend to clear session, then clears local state
   */
  const handleLogout = async () => {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include'
      });
      
      setUser(null);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  /**
   * Render loading state while checking authentication
   */
  if (loading) {
    return (
      <div className="App">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  /**
   * Render login/register if not authenticated
   */
  if (!user) {
    return (
      <div className="App">
        <div className="auth-container">
          <h1>📝 Hierarchical Todo List</h1>
          
          {showRegister ? (
            <>
              <Register onRegister={handleRegister} />
              <p className="auth-switch">
                Already have an account?{' '}
                <button 
                  className="link-button"
                  onClick={() => setShowRegister(false)}
                >
                  Login
                </button>
              </p>
            </>
          ) : (
            <>
              <Login onLogin={handleLogin} />
              <p className="auth-switch">
                Don't have an account?{' '}
                <button 
                  className="link-button"
                  onClick={() => setShowRegister(true)}
                >
                  Register
                </button>
              </p>
            </>
          )}
        </div>
      </div>
    );
  }

  /**
   * Render main application (authenticated users)
   * For PR-3, we just show a welcome message
   * Lists and todos will be added in PR-4 onwards
   */
  return (
    <div className="App">
      <header className="app-header">
        <h1>📝 Hierarchical Todo List</h1>
        <div className="user-info">
          <span>Welcome, {user.username}!</span>
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </header>

      <div className="main-content">
        <div className="welcome-message">
          <h2>🎉 Authentication Successful!</h2>
          <p>You are logged in as: <strong>{user.username}</strong></p>
          <p>Email: {user.email}</p>
          <p className="info-text">
            Lists and todos will be added in the next PRs (PR-4 and beyond).
            For now, you can test logging out and logging back in.
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
