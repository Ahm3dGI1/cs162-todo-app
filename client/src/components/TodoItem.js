import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faChevronRight,
  faChevronDown,
  faPlus,
  faBan,
  faFolder,
  faPenToSquare,
  faTrash,
  faSpinner
} from '@fortawesome/free-solid-svg-icons';

function TodoItem({ todo, listId, onUpdate, onDelete, onCreateSubtask, onMove, availableProjects, currentProjectId }) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(todo.title);
  const [editDescription, setEditDescription] = useState(todo.description || '');
  const [editPriority, setEditPriority] = useState(todo.priority || 'medium');

  //  Add subtask form state
  const [showSubtaskForm, setShowSubtaskForm] = useState(false);
  const [subtaskTitle, setSubtaskTitle] = useState('');
  const [subtaskDescription, setSubtaskDescription] = useState('');
  const [subtaskPriority, setSubtaskPriority] = useState('medium');
  const [subtaskLoading, setSubtaskLoading] = useState(false);

  //  Loading states for operations
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  //  Move task state
  const [showMoveDialog, setShowMoveDialog] = useState(false);
  const [isMoving, setIsMoving] = useState(false);

  /**
   * Handle save edit
   */
  const handleSaveEdit = async () => {
    if (!editTitle.trim()) {
      alert('Title cannot be empty');
      return;
    }

    setIsUpdating(true);
    try {
      await onUpdate(todo.id, {
        title: editTitle.trim(),
        description: editDescription.trim(),
        priority: editPriority
      });
      setIsEditing(false);
    } catch (err) {
      alert('Failed to update todo: ' + (err.message || 'Unknown error'));
    } finally {
      setIsUpdating(false);
    }
  };

  /**
   * Handle cancel edit
   */
  const handleCancelEdit = () => {
    setEditTitle(todo.title);
    setEditDescription(todo.description || '');
    setEditPriority(todo.priority || 'medium');
    setIsEditing(false);
  };

  /**
   * Handle checkbox toggle
   */
  const handleToggleComplete = async () => {
    try {
      await onUpdate(todo.id, {
        completed: !todo.completed
      });
    } catch (err) {
      alert('Failed to toggle completion: ' + (err.message || 'Unknown error'));
    }
  };

  /**
   * Handle delete with confirmation
   */
  const handleDelete = async () => {
    const confirmDelete = window.confirm(
      `Are you sure you want to delete "${todo.title}"?${todo.children && todo.children.length > 0 ? '\n\nThis will also delete all subtasks.' : ''}`
    );

    if (confirmDelete) {
      setIsDeleting(true);
      try {
        await onDelete(todo.id);
      } catch (err) {
        alert('Failed to delete todo: ' + (err.message || 'Unknown error'));
        setIsDeleting(false);
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
        description: subtaskDescription.trim(),
        priority: subtaskPriority
      });

      // Reset form
      setSubtaskTitle('');
      setSubtaskDescription('');
      setSubtaskPriority('medium');
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
    setSubtaskPriority('medium');
  };

  /**
   * Handle move to another project
   */
  const handleMoveToProject = async (targetProjectId) => {
    setIsMoving(true);
    try {
      await onMove(todo.id, targetProjectId);
      setShowMoveDialog(false);
    } catch (err) {
      alert('Failed to move task: ' + (err.message || 'Unknown error'));
    } finally {
      setIsMoving(false);
    }
  };

  //  Check if max depth reached
  const canAddSubtask = todo.depth < 2;

  //  Only top-level tasks can be moved
  const canMove = todo.depth === 0 && availableProjects && availableProjects.length > 1;

  /**
   * Handle keyboard shortcuts in edit mode
   */
  const handleEditKeyDown = (e) => {
    // Escape to cancel
    if (e.key === 'Escape') {
      handleCancelEdit();
    }
    // Ctrl+Enter or Cmd+Enter to save
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleSaveEdit();
    }
  };

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
      <div className={`todo-item depth-${todo.depth} editing`}>
        <div className="todo-content">
          <div className="todo-edit-form">
            <input
              type="text"
              className="edit-title-input"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              onKeyDown={handleEditKeyDown}
              placeholder="Todo title"
              autoFocus
              maxLength="500"
              disabled={isUpdating}
            />
            <textarea
              className="edit-description-input"
              value={editDescription}
              onChange={(e) => setEditDescription(e.target.value)}
              onKeyDown={handleEditKeyDown}
              placeholder="Description (optional)"
              rows="3"
              disabled={isUpdating}
            />
            <select
              className="edit-priority-select"
              value={editPriority}
              onChange={(e) => setEditPriority(e.target.value)}
              disabled={isUpdating}
            >
              <option value="low">Low Priority</option>
              <option value="medium">Medium Priority</option>
              <option value="high">High Priority</option>
            </select>
            <div className="edit-buttons">
              <button
                type="button"
                className="save-button"
                onClick={handleSaveEdit}
                disabled={!editTitle.trim() || isUpdating}
              >
                {isUpdating ? 'Saving...' : 'Save'}
              </button>
              <button
                type="button"
                className="cancel-button"
                onClick={handleCancelEdit}
                disabled={isUpdating}
              >
                Cancel
              </button>
            </div>
            <div className="keyboard-hints">
              Press <kbd>Esc</kbd> to cancel, <kbd>Ctrl+Enter</kbd> to save
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
            <FontAwesomeIcon icon={todo.collapsed ? faChevronRight : faChevronDown} />
          </button>
        ) : (
          <div className="collapse-spacer"></div>
        )}

        {/* Checkbox */}
        <input
          type="checkbox"
          className="todo-checkbox"
          checked={todo.completed}
          onChange={handleToggleComplete}
          title={todo.completed ? 'Mark as incomplete' : 'Mark as complete'}
        />

        {/* Todo text */}
        <div className="todo-text" onClick={() => setIsEditing(true)}>
          <div className="todo-title-row">
            <span className="todo-title">{todo.title}</span>
            <span className={`priority-badge priority-${todo.priority || 'medium'}`}>
              {(todo.priority || 'medium').toUpperCase()}
            </span>
          </div>
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
              disabled={isDeleting}
            >
              <FontAwesomeIcon icon={faPlus} />
            </button>
          ) : (
            <button
              className="action-button"
              disabled
              title="Maximum depth reached (3 levels)"
            >
              <FontAwesomeIcon icon={faBan} />
            </button>
          )}
          {/*  Move button (only for top-level tasks) */}
          {canMove && (
            <button
              className="action-button"
              onClick={() => setShowMoveDialog(!showMoveDialog)}
              title="Move to another project"
              disabled={isDeleting || isMoving}
            >
              <FontAwesomeIcon icon={faFolder} />
            </button>
          )}
          <button
            className="action-button"
            onClick={() => setIsEditing(true)}
            title="Edit todo"
            disabled={isDeleting}
          >
            <FontAwesomeIcon icon={faPenToSquare} />
          </button>
          <button
            className="action-button delete"
            onClick={handleDelete}
            title="Delete todo"
            disabled={isDeleting}
          >
            {isDeleting ? <FontAwesomeIcon icon={faSpinner} spin /> : <FontAwesomeIcon icon={faTrash} />}
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
            <select
              className="child-priority-select"
              value={subtaskPriority}
              onChange={(e) => setSubtaskPriority(e.target.value)}
              disabled={subtaskLoading}
            >
              <option value="low">Low Priority</option>
              <option value="medium">Medium Priority</option>
              <option value="high">High Priority</option>
            </select>
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

      {/*  Move task dialog */}
      {showMoveDialog && (
        <div className="move-dialog">
          <div className="move-dialog-header">
            Move to Project
          </div>
          <div className="move-dialog-content">
            {availableProjects
              .filter(project => project.id !== currentProjectId)
              .map(project => (
                <button
                  key={project.id}
                  className="move-option"
                  onClick={() => handleMoveToProject(project.id)}
                  disabled={isMoving}
                >
                  📋 {project.name}
                </button>
              ))}
          </div>
          <div className="move-dialog-footer">
            <button
              className="cancel-button"
              onClick={() => setShowMoveDialog(false)}
              disabled={isMoving}
            >
              Cancel
            </button>
          </div>
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
              onMove={onMove}
              availableProjects={availableProjects}
              currentProjectId={currentProjectId}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default TodoItem;
