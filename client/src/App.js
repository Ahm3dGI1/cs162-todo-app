import React, { useState, useEffect } from 'react';
import './App.css';
import Login from './components/Login';
import Register from './components/Register';
import ListSelector from './components/ListSelector';
import { API_ENDPOINTS } from './config/api';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showRegister, setShowRegister] = useState(false);

  const [lists, setLists] = useState([]);
  const [selectedList, setSelectedList] = useState(null);
  const [listsLoading, setListsLoading] = useState(false);

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
      setLists([]);
      setSelectedList(null);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  /**
   * Fetch all lists for the current user
   */
  const fetchLists = async () => {
    setListsLoading(true);
    try {
      const response = await fetch(API_ENDPOINTS.LISTS, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setLists(data.lists);

        // Auto-select first list if none selected
        if (data.lists.length > 0 && !selectedList) {
          setSelectedList(data.lists[0]);
        }
      } else {
        console.error('Failed to fetch lists');
      }
    } catch (error) {
      console.error('Error fetching lists:', error);
    } finally {
      setListsLoading(false);
    }
  };

  /**
   * Create a new list
   */
  const handleCreateList = async (name) => {
    const response = await fetch(API_ENDPOINTS.LISTS, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({ name })
    });

    if (response.ok) {
      const data = await response.json();
      const newList = data.list;
      setLists([...lists, newList]);

      // Auto-select the new list
      setSelectedList(newList);
    } else {
      const error = await response.json();
      throw new Error(error.error || 'Failed to create list');
    }
  };

  /**
   * Select a list
   */
  const handleSelectList = (list) => {
    setSelectedList(list);
  };

  /**
   * Delete a list
   */
  const handleDeleteList = async (listId) => {
    const response = await fetch(`${API_ENDPOINTS.LISTS}/${listId}`, {
      method: 'DELETE',
      credentials: 'include'
    });

    if (response.ok) {
      const updatedLists = lists.filter(list => list.id !== listId);
      setLists(updatedLists);

      // If deleted list was selected, select first remaining list
      if (selectedList?.id === listId) {
        setSelectedList(updatedLists.length > 0 ? updatedLists[0] : null);
      }
    } else {
      const error = await response.json();
      throw new Error(error.error || 'Failed to delete list');
    }
  };

  /**
   * Load lists when user logs in
   */
  useEffect(() => {
    if (user) {
      fetchLists();
    }
  }, [user]);

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

      <div className="app-content">
        {/* List Selector Sidebar (PR-5) */}
        <ListSelector
          lists={lists}
          selectedList={selectedList}
          onSelectList={handleSelectList}
          onCreateList={handleCreateList}
          onDeleteList={handleDeleteList}
        />

        {/* Main Content Area */}
        <div className="main-content">
          {listsLoading ? (
            <div className="loading">Loading lists...</div>
          ) : selectedList ? (
            <div className="todo-list">
              <div className="todo-list-header">
                <h2>{selectedList.name}</h2>
              </div>
              <p className="no-todos">
                Todos will be added in PR-6 and PR-7.
                For now, you can create and manage lists!
              </p>
            </div>
          ) : (
            <div className="no-list-selected">
              {lists.length === 0 ? (
                <>
                  <p>No lists yet.</p>
                  <p>Create your first list to get started!</p>
                </>
              ) : (
                <p>Select a list from the sidebar</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
