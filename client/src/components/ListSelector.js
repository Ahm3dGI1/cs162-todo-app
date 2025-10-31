import React, { useState } from 'react';

function ListSelector({ lists, selectedList, onSelectList, onCreateList, onDeleteList }) {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newListName, setNewListName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  /**
   * Handle create list form submission
   */
  const handleCreateList = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const trimmedName = newListName.trim();

    if (!trimmedName) {
      setError('List name cannot be empty');
      setLoading(false);
      return;
    }

    try {
      await onCreateList(trimmedName);
      setNewListName('');
      setShowCreateForm(false);
    } catch (err) {
      setError(err.message || 'Failed to create list');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle delete list with confirmation
   */
  const handleDeleteList = async (list) => {
    const confirmDelete = window.confirm(
      `Are you sure you want to delete "${list.name}"? All todos in this list will be deleted.`
    );

    if (confirmDelete) {
      try {
        await onDeleteList(list.id);
      } catch (err) {
        alert('Failed to delete list: ' + (err.message || 'Unknown error'));
      }
    }
  };

  /**
   * Cancel create form
   */
  const handleCancelCreate = () => {
    setShowCreateForm(false);
    setNewListName('');
    setError('');
  };

  return (
    <div className="list-selector">
      <div className="list-selector-header">
        <h2>My Lists</h2>
        {!showCreateForm && (
          <button
            className="create-list-button"
            onClick={() => setShowCreateForm(true)}
            disabled={loading}
          >
            + New List
          </button>
        )}
      </div>

      {/* Create List Form */}
      {showCreateForm && (
        <div className="create-list-form">
          {error && <div className="error-message">{error}</div>}
          <form onSubmit={handleCreateList}>
            <input
              type="text"
              className="list-name-input"
              placeholder="List name"
              value={newListName}
              onChange={(e) => setNewListName(e.target.value)}
              autoFocus
              disabled={loading}
              maxLength="200"
            />
            <div className="create-list-buttons">
              <button
                type="submit"
                className="save-button"
                disabled={loading || !newListName.trim()}
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

      {/* Lists Container */}
      <div className="lists-container">
        {lists.length === 0 ? (
          <div className="no-lists">
            No lists yet. Create your first list to get started!
          </div>
        ) : (
          lists.map((list) => (
            <div
              key={list.id}
              className={`list-item ${selectedList?.id === list.id ? 'selected' : ''}`}
              onClick={() => onSelectList(list)}
            >
              <div className="list-item-content">
                <span className="list-name">{list.name}</span>
              </div>
              <button
                className="delete-list-button"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeleteList(list);
                }}
                title="Delete list"
              >
                🗑️
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default ListSelector;
