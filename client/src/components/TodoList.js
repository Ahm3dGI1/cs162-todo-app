import React, { useState } from 'react';
import TodoItem from './TodoItem';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faArrowLeft } from '@fortawesome/free-solid-svg-icons';

function TodoList({ list, todos, onCreateTodo, onUpdateTodo, onDeleteTodo, onMoveTodo, availableProjects, onBack }) {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newTodoTitle, setNewTodoTitle] = useState('');
  const [newTodoDescription, setNewTodoDescription] = useState('');
  const [newTodoPriority, setNewTodoPriority] = useState('medium');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  /**
   * Handle create todo form submission
   */
  const handleCreateTodo = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const trimmedTitle = newTodoTitle.trim();

    if (!trimmedTitle) {
      setError('Title cannot be empty');
      setLoading(false);
      return;
    }

    try {
      await onCreateTodo({
        project_id: list.id,
        title: trimmedTitle,
        description: newTodoDescription.trim(),
        priority: newTodoPriority
      });

      // Reset form
      setNewTodoTitle('');
      setNewTodoDescription('');
      setNewTodoPriority('medium');
      setShowCreateForm(false);
    } catch (err) {
      setError(err.message || 'Failed to create todo');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle cancel create
   */
  const handleCancelCreate = () => {
    setShowCreateForm(false);
    setNewTodoTitle('');
    setNewTodoDescription('');
    setNewTodoPriority('medium');
    setError('');
  };

  return (
    <div className="todo-list-container">
      {/* Page Header */}
      <div className="project-page-header">
        <div className="project-header-content">
          <h1 className="project-title">{list.name}</h1>
          <div className="project-header-actions">
            {!showCreateForm && (
              <button
                className="add-task-button"
                onClick={() => setShowCreateForm(true)}
                disabled={loading}
              >
                <FontAwesomeIcon icon={faPlus} /> Add Task
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="todo-list-content">

        {/* Create Todo Form */}
        {showCreateForm && (
          <div className="create-task-card">
            {error && <div className="error-message">{error}</div>}
            <form onSubmit={handleCreateTodo}>
              <div className="form-group">
                <label>Task Title</label>
                <input
                  type="text"
                  className="task-input"
                  placeholder="Enter task title"
                  value={newTodoTitle}
                  onChange={(e) => setNewTodoTitle(e.target.value)}
                  autoFocus
                  disabled={loading}
                  maxLength="500"
                />
              </div>
              <div className="form-group">
                <label>Description (optional)</label>
                <textarea
                  className="task-input"
                  placeholder="Add more details..."
                  value={newTodoDescription}
                  onChange={(e) => setNewTodoDescription(e.target.value)}
                  disabled={loading}
                  rows="3"
                />
              </div>
              <div className="form-group">
                <label>Priority</label>
                <select
                  className="priority-select"
                  value={newTodoPriority}
                  onChange={(e) => setNewTodoPriority(e.target.value)}
                  disabled={loading}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
              <div className="create-task-buttons">
                <button
                  type="submit"
                  className="save-button"
                  disabled={loading || !newTodoTitle.trim()}
                >
                  {loading ? 'Creating...' : 'Create Task'}
                </button>
                <button
                  type="button"
                  className="cancel-button"
                  onClick={handleCancelCreate}
                  disabled={loading}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Todos Container */}
        <div className="tasks-container">
          {todos.length === 0 ? (
            <div className="no-tasks">
              <p>No tasks yet.</p>
              <p>Create your first task to get started!</p>
            </div>
          ) : (
            todos.map((todo) => (
              <TodoItem
                key={todo.id}
                todo={todo}
                listId={list.id}
                onUpdate={onUpdateTodo}
                onDelete={onDeleteTodo}
                onCreateSubtask={onCreateTodo}
                onMove={onMoveTodo}
                availableProjects={availableProjects}
                currentProjectId={list.id}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default TodoList;
