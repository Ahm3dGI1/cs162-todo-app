import React, { useState } from 'react';

function TodoItem({ todo, listId, onUpdate, onDelete, onCreateSubtask }) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(todo.title);
  const [editDescription, setEditDescription] = useState(todo.description || '');

  //  Add subtask form state
  const [showSubtaskForm, setShowSubtaskForm] = useState(false);
  const [subtaskTitle, setSubtaskTitle] = useState('');
  const [subtaskDescription, setSubtaskDescription] = useState('');
  const [subtaskLoading, setSubtaskLoading] = useState(false);

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
   * Handle checkbox toggle
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

  /**
   *  Handle create subtask
   */
  const handleCreateSubtask = async (e) => {
    e.preventDefault();

    if (!subtaskTitle.trim()) {
      alert('Subtask title cannot be empty');
      return;
    }

    setSubtaskLoading(true);
    try {
      await onCreateSubtask({
        project_id: listId,
        parent_id: todo.id,
        title: subtaskTitle.trim(),
        description: subtaskDescription.trim()
      });

      // Reset form
      setSubtaskTitle('');
      setSubtaskDescription('');
      setShowSubtaskForm(false);
    } catch (err) {
      alert('Failed to create subtask: ' + (err.message || 'Unknown error'));
    } finally {
      setSubtaskLoading(false);
    }
  };

  /**
   *  Cancel subtask form
   */
  const handleCancelSubtask = () => {
    setShowSubtaskForm(false);
    setSubtaskTitle('');
    setSubtaskDescription('');
  };

  //  Check if max depth reached
  const canAddSubtask = todo.depth < 2;

  /**
   * Handle toggle collapse
   */
  const handleToggleCollapse = async () => {
    try {
      await onUpdate(todo.id, {
        collapsed: !todo.collapsed
      });
    } catch (err) {
      alert('Failed to toggle collapse: ' + (err.message || 'Unknown error'));
    }
  };

  if (isEditing) {
    return (
      <div className={`todo-item depth-${todo.depth}`}>
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
    <div className={`todo-item depth-${todo.depth}`}>
      <div className={`todo-content ${todo.completed ? 'completed' : ''}`}>
        {/* Collapse/Expand button (only if has children) */}
        {todo.children && todo.children.length > 0 ? (
          <button
            className="collapse-button"
            onClick={handleToggleCollapse}
            title={todo.collapsed ? 'Expand' : 'Collapse'}
          >
            {todo.collapsed ? '▶' : '▼'}
          </button>
        ) : (
          <div className="collapse-spacer"></div>
        )}

        {/* Checkbox (not functional yet) */}
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
          {/*  Add Subtask button */}
          {canAddSubtask ? (
            <button
              className="action-button"
              onClick={() => setShowSubtaskForm(!showSubtaskForm)}
              title="Add subtask"
            >
              ➕
            </button>
          ) : (
            <button
              className="action-button"
              disabled
              title="Maximum depth reached (3 levels)"
            >
              🚫
            </button>
          )}
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

      {/*  Subtask creation form */}
      {showSubtaskForm && (
        <div className="add-child-form">
          <form onSubmit={handleCreateSubtask}>
            <input
              type="text"
              className="child-input"
              placeholder="Subtask title"
              value={subtaskTitle}
              onChange={(e) => setSubtaskTitle(e.target.value)}
              autoFocus
              disabled={subtaskLoading}
              maxLength="500"
            />
            <textarea
              className="child-input"
              placeholder="Description (optional)"
              value={subtaskDescription}
              onChange={(e) => setSubtaskDescription(e.target.value)}
              disabled={subtaskLoading}
              rows="2"
            />
            <div className="add-child-buttons">
              <button
                type="submit"
                className="save-button"
                disabled={subtaskLoading || !subtaskTitle.trim()}
              >
                {subtaskLoading ? 'Adding...' : 'Add Subtask'}
              </button>
              <button
                type="button"
                className="cancel-button"
                onClick={handleCancelSubtask}
                disabled={subtaskLoading}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/*  Recursive rendering of children (only if not collapsed) */}
      {todo.children && todo.children.length > 0 && !todo.collapsed && (
        <div className="todo-children">
          {todo.children.map((child) => (
            <TodoItem
              key={child.id}
              todo={child}
              listId={listId}
              onUpdate={onUpdate}
              onDelete={onDelete}
              onCreateSubtask={onCreateSubtask}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default TodoItem;
