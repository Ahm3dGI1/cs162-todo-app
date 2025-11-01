import React, { useState, useEffect } from 'react';
import './App.css';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import Sidebar from './components/Sidebar';
import TodoList from './components/TodoList';
import { API_ENDPOINTS } from './config/api';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faClipboardCheck } from '@fortawesome/free-solid-svg-icons';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showRegister, setShowRegister] = useState(false);

  // Project state
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectsLoading, setProjectsLoading] = useState(false);
  const [viewMode, setViewMode] = useState('dashboard'); // 'dashboard' or 'project'

  // Sidebar state
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Todo state
  const [todos, setTodos] = useState([]);
  const [todosLoading, setTodosLoading] = useState(false);

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
      setProjects([]);
      setSelectedProject(null);
      setViewMode('dashboard');
      setSidebarOpen(false);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  /**
   * Fetch all projects for the current user
   */
  const fetchProjects = async () => {
    setProjectsLoading(true);
    try {
      const response = await fetch(API_ENDPOINTS.PROJECTS, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setProjects(data.projects);
      } else {
        console.error('Failed to fetch projects');
      }
    } catch (error) {
      console.error('Error fetching projects:', error);
    } finally {
      setProjectsLoading(false);
    }
  };

  /**
   * Create a new project
   */
  const handleCreateProject = async (name) => {
    const response = await fetch(API_ENDPOINTS.PROJECTS, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({ name })
    });

    if (response.ok) {
      const data = await response.json();
      const newProject = data.project;
      setProjects([...projects, newProject]);
    } else {
      const error = await response.json();
      throw new Error(error.error || 'Failed to create project');
    }
  };

  /**
   * Select a project and switch to project view
   */
  const handleSelectProject = (project) => {
    setSelectedProject(project);
    setViewMode('project');
  };

  /**
   * Navigate back to dashboard
   */
  const handleBackToDashboard = () => {
    setViewMode('dashboard');
    setSelectedProject(null);
    setTodos([]);
    setSidebarOpen(false);
  };

  /**
   * Delete a project
   */
  const handleDeleteProject = async (projectId) => {
    const response = await fetch(`${API_ENDPOINTS.PROJECTS}/${projectId}`, {
      method: 'DELETE',
      credentials: 'include'
    });

    if (response.ok) {
      const updatedProjects = projects.filter(project => project.id !== projectId);
      setProjects(updatedProjects);

      // If deleted project was selected, go back to dashboard
      if (selectedProject?.id === projectId) {
        handleBackToDashboard();
      }
    } else {
      const error = await response.json();
      throw new Error(error.error || 'Failed to delete project');
    }
  };

  /**
   * Fetch todos for the selected project
   */
  const fetchTodos = async (projectId) => {
    setTodosLoading(true);
    try {
      const response = await fetch(`${API_ENDPOINTS.TODOS}/${projectId}`, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setTodos(data.todos);
      } else {
        console.error('Failed to fetch todos');
        setTodos([]);
      }
    } catch (error) {
      console.error('Error fetching todos:', error);
      setTodos([]);
    } finally {
      setTodosLoading(false);
    }
  };

  /**
   * Create a new todo
   */
  const handleCreateTodo = async (todoData) => {
    const response = await fetch(API_ENDPOINTS.TODOS, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify(todoData)
    });

    if (response.ok) {
      // Refetch todos to get updated hierarchical structure
      if (selectedProject) {
        await fetchTodos(selectedProject.id);
      }
    } else {
      const error = await response.json();
      throw new Error(error.error || 'Failed to create todo');
    }
  };

  /**
   * Update a todo with optimistic UI updates
   */
  const handleUpdateTodo = async (todoId, updates) => {
    // Optimistic update - update UI immediately
    const applyOptimisticUpdate = (todosList) => {
      return todosList.map(todo => {
        if (todo.id === todoId) {
          // Apply updates optimistically
          const optimisticTodo = { ...todo, ...updates };

          // If completing, cascade to children optimistically
          if (updates.completed === true && todo.children) {
            const markChildrenComplete = (children) => {
              return children.map(child => ({
                ...child,
                completed: true,
                children: child.children ? markChildrenComplete(child.children) : []
              }));
            };
            optimisticTodo.children = markChildrenComplete(todo.children);
          }

          return optimisticTodo;
        } else if (todo.children && todo.children.length > 0) {
          return {
            ...todo,
            children: applyOptimisticUpdate(todo.children)
          };
        }
        return todo;
      });
    };

    // Update UI immediately
    setTodos(applyOptimisticUpdate(todos));

    try {
      // Then sync with backend
      const response = await fetch(`${API_ENDPOINTS.TODOS}/${todoId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(updates)
      });

      if (response.ok) {
        const data = await response.json();
        const updatedTodo = data.todo;

        // Update with authoritative server response
        const updateTodoInTree = (todosList) => {
          return todosList.map(todo => {
            if (todo.id === updatedTodo.id) {
              return updatedTodo;
            } else if (todo.children && todo.children.length > 0) {
              return {
                ...todo,
                children: updateTodoInTree(todo.children)
              };
            }
            return todo;
          });
        };

        setTodos(updateTodoInTree(todos));
      } else {
        // Revert optimistic update on error
        await fetchTodos(selectedProject.id);
        const error = await response.json();
        throw new Error(error.error || 'Failed to update todo');
      }
    } catch (err) {
      // Revert on network error
      await fetchTodos(selectedProject.id);
      throw err;
    }
  };

  /**
   * Delete a todo
   */
  const handleDeleteTodo = async (todoId) => {
    const response = await fetch(`${API_ENDPOINTS.TODOS}/${todoId}`, {
      method: 'DELETE',
      credentials: 'include'
    });

    if (response.ok) {
      // Refetch to maintain hierarchical structure
      if (selectedProject) {
        await fetchTodos(selectedProject.id);
      }
    } else {
      const error = await response.json();
      throw new Error(error.error || 'Failed to delete todo');
    }
  };

  /**
   * Move a todo to another project
   */
  const handleMoveTodo = async (todoId, targetProjectId) => {
    const response = await fetch(`${API_ENDPOINTS.TODOS}/${todoId}/move`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({ target_project_id: targetProjectId })
    });

    if (response.ok) {
      // Refetch current project's todos after move
      if (selectedProject) {
        await fetchTodos(selectedProject.id);
      }
    } else {
      const error = await response.json();
      throw new Error(error.error || 'Failed to move todo');
    }
  };

  /**
   * Load projects when user logs in
   */
  useEffect(() => {
    if (user) {
      fetchProjects();
    }
  }, [user]);

  /**
   * Load todos when selected project changes
   */
  useEffect(() => {
    if (selectedProject) {
      fetchTodos(selectedProject.id);
    } else {
      setTodos([]);
    }
  }, [selectedProject]);

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
          <h1><FontAwesomeIcon icon={faClipboardCheck} /> Hierarchical Todo List</h1>
          
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
      {/* Hamburger Menu Button (only in project view) */}
      {viewMode === 'project' && (
        <button
          className="hamburger-btn"
          onClick={() => setSidebarOpen(true)}
          aria-label="Open menu"
        >
          ☰
        </button>
      )}

      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        currentProject={selectedProject}
        onBackToDashboard={handleBackToDashboard}
        user={user}
        onLogout={handleLogout}
      />

      {/* Main Content */}
      <div className="app-content">
        {viewMode === 'dashboard' ? (
          /* Dashboard View */
          projectsLoading ? (
            <div className="loading">Loading projects...</div>
          ) : (
            <Dashboard
              projects={projects}
              onSelectProject={handleSelectProject}
              onCreateProject={handleCreateProject}
              onDeleteProject={handleDeleteProject}
              user={user}
              onLogout={handleLogout}
            />
          )
        ) : (
          /* Project View */
          <div className="project-view">
            {todosLoading ? (
              <div className="loading">Loading tasks...</div>
            ) : selectedProject ? (
              <TodoList
                list={selectedProject}
                todos={todos}
                onCreateTodo={handleCreateTodo}
                onUpdateTodo={handleUpdateTodo}
                onDeleteTodo={handleDeleteTodo}
                onMoveTodo={handleMoveTodo}
                availableProjects={projects}
              />
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
