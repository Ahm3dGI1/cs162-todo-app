import React, { useState } from 'react';
import TodoItem from './TodoItem';

function TodoList({ list, todos, onCreateTodo, onUpdateTodo, onDeleteTodo }) {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newTodoTitle, setNewTodoTitle] = useState('');
  const [newTodoDescription, setNewTodoDescription] = useState('');
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
        description: newTodoDescription.trim()
      });

      // Reset form
      setNewTodoTitle('');
      setNewTodoDescription('');
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
    setError('');
  };

  return (
    <div className="todo-list">
      <div className="todo-list-header">
        <h2>{list.name}</h2>
        {!showCreateForm && (
          <button
            className="add-todo-button"
            onClick={() => setShowCreateForm(true)}
            disabled={loading}
          >
            + Add Task
          </button>
        )}
      </div>

      {/* Create Todo Form */}
      {showCreateForm && (
        <div className="create-todo-form">
          {error && <div className="error-message">{error}</div>}
          <form onSubmit={handleCreateTodo}>
            <input
              type="text"
              className="todo-input"
              placeholder="Todo title"
              value={newTodoTitle}
              onChange={(e) => setNewTodoTitle(e.target.value)}
              autoFocus
              disabled={loading}
              maxLength="500"
            />
            <textarea
              className="todo-input"
              placeholder="Description (optional)"
              value={newTodoDescription}
              onChange={(e) => setNewTodoDescription(e.target.value)}
              disabled={loading}
              rows="3"
            />
            <div className="create-todo-buttons">
              <button
                type="submit"
                className="save-button"
                disabled={loading || !newTodoTitle.trim()}
              >
                {loading ? 'Creating...' : 'Create'}
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
      <div className="todos-container">
        {todos.length === 0 ? (
          <div className="no-todos">
            No tasks yet. Click "+ Add Task" to create one!
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
            />
          ))
        )}
      </div>
    </div>
  );
}

export default TodoList;
