import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import TodoList from '../components/TodoList';
import Sidebar from '../components/Sidebar';
import { API_ENDPOINTS } from '../config/api';

function ProjectPage({ user, onLogout }) {
  const { projectId } = useParams();
  const navigate = useNavigate();

  const [project, setProject] = useState(null);
  const [projects, setProjects] = useState([]);
  const [todos, setTodos] = useState([]);
  const [todosLoading, setTodosLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  /**
   * Fetch project details
   */
  const fetchProject = async () => {
    try {
      const response = await fetch(`${API_ENDPOINTS.PROJECTS}/${projectId}`, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setProject(data.project);
      } else {
        console.error('Failed to fetch project');
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Error fetching project:', error);
      navigate('/dashboard');
    }
  };

  /**
   * Fetch all projects (for move functionality)
   */
  const fetchProjects = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.PROJECTS, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setProjects(data.projects);
      }
    } catch (error) {
      console.error('Error fetching projects:', error);
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
      await fetchTodos(projectId);
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
          const optimisticTodo = { ...todo, ...updates };

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

    setTodos(applyOptimisticUpdate(todos));

    try {
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
        await fetchTodos(projectId);
        const error = await response.json();
        throw new Error(error.error || 'Failed to update todo');
      }
    } catch (err) {
      await fetchTodos(projectId);
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
      await fetchTodos(projectId);
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
      await fetchTodos(projectId);
    } else {
      const error = await response.json();
      throw new Error(error.error || 'Failed to move todo');
    }
  };

  /**
   * Navigate back to dashboard
   */
  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  /**
   * Load project and todos when component mounts or projectId changes
   */
  useEffect(() => {
    if (projectId) {
      fetchProject();
      fetchProjects();
      fetchTodos(projectId);
    }
  }, [projectId]);

  if (!project) {
    return <div className="loading">Loading project...</div>;
  }

  return (
    <div className="project-view">
      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        currentProject={project}
        onBackToDashboard={handleBackToDashboard}
        user={user}
        onLogout={onLogout}
      />

      {/* Todo List */}
      {todosLoading ? (
        <div className="loading">Loading tasks...</div>
      ) : (
        <TodoList
          list={project}
          todos={todos}
          onCreateTodo={handleCreateTodo}
          onUpdateTodo={handleUpdateTodo}
          onDeleteTodo={handleDeleteTodo}
          onMoveTodo={handleMoveTodo}
          availableProjects={projects}
          onOpenSidebar={() => setSidebarOpen(true)}
        />
      )}
    </div>
  );
}

export default ProjectPage;
