import React, { useState } from 'react';

function Dashboard({ projects, onSelectProject, onCreateProject, onDeleteProject }) {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [projectName, setProjectName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  /**
   * Handle create project form submission
   */
  const handleCreateProject = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const trimmedName = projectName.trim();

    if (!trimmedName) {
      setError('Project name cannot be empty');
      setLoading(false);
      return;
    }

    try {
      await onCreateProject(trimmedName);
      setProjectName('');
      setShowCreateForm(false);
    } catch (err) {
      setError(err.message || 'Failed to create project');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle cancel create
   */
  const handleCancelCreate = () => {
    setShowCreateForm(false);
    setProjectName('');
    setError('');
  };

  /**
   * Handle delete project with confirmation
   */
  const handleDeleteProject = async (projectId, projectName) => {
    const confirmDelete = window.confirm(
      `Are you sure you want to delete "${projectName}" and all its tasks?`
    );

    if (confirmDelete) {
      try {
        await onDeleteProject(projectId);
      } catch (err) {
        alert('Failed to delete project: ' + (err.message || 'Unknown error'));
      }
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>My Projects</h1>
        {!showCreateForm && (
          <button
            className="create-project-btn"
            onClick={() => setShowCreateForm(true)}
            disabled={loading}
          >
            + New Project
          </button>
        )}
      </div>

      {/* Create Project Form */}
      {showCreateForm && (
        <div className="create-project-form">
          {error && <div className="error-message">{error}</div>}
          <form onSubmit={handleCreateProject}>
            <input
              type="text"
              className="project-name-input"
              placeholder="Project name"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              autoFocus
              disabled={loading}
              maxLength="200"
            />
            <div className="create-project-buttons">
              <button
                type="submit"
                className="save-button"
                disabled={loading || !projectName.trim()}
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

      {/* Projects Grid */}
      <div className="projects-grid">
        {projects.length === 0 ? (
          <div className="no-projects">
            <p>No projects yet.</p>
            <p>Create your first project to get started!</p>
          </div>
        ) : (
          projects.map((project) => (
            <div
              key={project.id}
              className="project-card"
              onClick={() => onSelectProject(project)}
            >
              <div className="project-card-header">
                <h3>{project.name}</h3>
                <button
                  className="delete-project-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteProject(project.id, project.name);
                  }}
                  title="Delete project"
                >
                  🗑️
                </button>
              </div>
              <div className="project-card-footer">
                <span className="project-date">
                  Created {new Date(project.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default Dashboard;
