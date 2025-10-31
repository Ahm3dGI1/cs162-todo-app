import React, { useState } from 'react';

function TodoItem({ todo, onUpdate, onDelete }) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(todo.title);
  const [editDescription, setEditDescription] = useState(todo.description || '');

  /**
   * Handle save edit
   */
  const handleSaveEdit = async () => {
    if (!editTitle.trim()) {
      alert('Title cannot be empty');
      return;
    }

    try {
      await onUpdate(todo.id, {
        title: editTitle.trim(),
        description: editDescription.trim()
      });
      setIsEditing(false);
    } catch (err) {
      alert('Failed to update todo: ' + (err.message || 'Unknown error'));
    }
  };

  /**
   * Handle cancel edit
   */
  const handleCancelEdit = () => {
    setEditTitle(todo.title);
    setEditDescription(todo.description || '');
    setIsEditing(false);
  };

  /**
   * Handle checkbox toggle (not functional yet in PR-7)
   */
  const handleToggleComplete = () => {
    // Will be implemented in later PR
    console.log('Checkbox toggled (not functional yet)');
  };

  /**
   * Handle delete with confirmation
   */
  const handleDelete = async () => {
    const confirmDelete = window.confirm(
      `Are you sure you want to delete "${todo.title}"?`
    );

    if (confirmDelete) {
      try {
        await onDelete(todo.id);
      } catch (err) {
        alert('Failed to delete todo: ' + (err.message || 'Unknown error'));
      }
    }
  };

  if (isEditing) {
    return (
      <div className="todo-item">
        <div className="todo-content">
          <div className="todo-edit-form">
            <input
              type="text"
              className="edit-title-input"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              placeholder="Todo title"
              autoFocus
              maxLength="500"
            />
            <textarea
              className="edit-description-input"
              value={editDescription}
              onChange={(e) => setEditDescription(e.target.value)}
              placeholder="Description (optional)"
              rows="3"
            />
            <div className="edit-buttons">
              <button
                type="button"
                className="save-button"
                onClick={handleSaveEdit}
                disabled={!editTitle.trim()}
              >
                Save
              </button>
              <button
                type="button"
                className="cancel-button"
                onClick={handleCancelEdit}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="todo-item">
      <div className={`todo-content ${todo.completed ? 'completed' : ''}`}>
        {/* Checkbox (not functional in PR-7) */}
        <input
          type="checkbox"
          className="todo-checkbox"
          checked={false}
          onChange={handleToggleComplete}
          title="Checkbox (not functional yet)"
        />

        {/* Todo text */}
        <div className="todo-text" onClick={() => setIsEditing(true)}>
          <div className="todo-title">{todo.title}</div>
          {todo.description && (
            <div className="todo-description">{todo.description}</div>
          )}
        </div>

        {/* Action buttons */}
        <div className="todo-actions">
          <button
            className="action-button"
            onClick={() => setIsEditing(true)}
            title="Edit todo"
          >
            ✏️
          </button>
          <button
            className="action-button delete"
            onClick={handleDelete}
            title="Delete todo"
          >
            🗑️
          </button>
        </div>
      </div>
    </div>
  );
}

export default TodoItem;
