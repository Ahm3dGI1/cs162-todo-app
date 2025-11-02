import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Login from '../components/Login';
import Register from '../components/Register';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faClipboardCheck } from '@fortawesome/free-solid-svg-icons';

function LoginPage({ onLogin }) {
  const [showRegister, setShowRegister] = useState(false);
  const navigate = useNavigate();

  const handleLogin = (userData) => {
    onLogin(userData);
    navigate('/dashboard');
  };

  const handleRegister = (userData) => {
    onLogin(userData);
    navigate('/dashboard');
  };

  return (
    <div className="App">
      <div className="auth-container">
        <h1>
          <FontAwesomeIcon icon={faClipboardCheck} /> Hierarchical Todo List
        </h1>

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

export default LoginPage;
