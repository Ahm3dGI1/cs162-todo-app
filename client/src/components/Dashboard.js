import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faUser,
  faRightFromBracket,
  faClipboardList,
  faGear,
  faLock,
  faTrash
} from '@fortawesome/free-solid-svg-icons';

function Dashboard({
  projects,
  onSelectProject,
  onCreateProject,
  onDeleteProject,
  user,
  onLogout,
  currentSection = 'projects'
}) {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [projectName, setProjectName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeSection, setActiveSection] = useState(currentSection);

  // Password change state
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState('');
  const [passwordLoading, setPasswordLoading] = useState(false);

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

  /**
   * Handle password change
   */
  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setPasswordError('');
    setPasswordSuccess('');

    // Validation
    if (!currentPassword || !newPassword || !confirmPassword) {
      setPasswordError('All fields are required');
      return;
    }

    if (newPassword.length < 6) {
      setPasswordError('New password must be at least 6 characters long');
      return;
    }

    if (newPassword !== confirmPassword) {
      setPasswordError('New passwords do not match');
      return;
    }

    setPasswordLoading(true);

    try {
      const response = await fetch('/api/auth/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        })
      });

      const data = await response.json();

      if (response.ok) {
        setPasswordSuccess('Password changed successfully!');
        setCurrentPassword('');
        setNewPassword('');
        setConfirmPassword('');
        setShowPasswordForm(false);

        // Clear success message after 3 seconds
        setTimeout(() => setPasswordSuccess(''), 3000);
      } else {
        setPasswordError(data.error || 'Failed to change password');
      }
    } catch (err) {
      setPasswordError('An error occurred. Please try again.');
    } finally {
      setPasswordLoading(false);
    }
  };

  /**
   * Cancel password change
   */
  const handleCancelPasswordChange = () => {
    setShowPasswordForm(false);
    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');
    setPasswordError('');
    setPasswordSuccess('');
  };

  // Get section title
  const getSectionTitle = () => {
    switch(activeSection) {
      case 'projects':
        return 'My Projects';
      case 'settings':
        return 'Account Settings';
      default:
        return 'Dashboard';
    }
  };

  return (
    <div className="dashboard-layout">
      {/* Header */}
      <div className="dashboard-top-header">
        <div className="header-title">
          <h1>{getSectionTitle()}</h1>
        </div>
        <div className="header-user">
          <span className="user-name">
            <FontAwesomeIcon icon={faUser} /> {user?.username}
          </span>
          <button className="header-logout-btn" onClick={onLogout} title="Logout">
            <FontAwesomeIcon icon={faRightFromBracket} />
          </button>
        </div>
      </div>

      {/* Layout with Sidebar and Content */}
      <div className="dashboard-main">
        {/* Sidebar */}
        <div className="dashboard-sidebar">
          <div className="sidebar-section">
            <h3 className="sidebar-section-title">Navigation</h3>
            <button
              className={`sidebar-menu-item ${activeSection === 'projects' ? 'active' : ''}`}
              onClick={() => setActiveSection('projects')}
            >
              <FontAwesomeIcon icon={faClipboardList} /> Projects
            </button>
            <button
              className={`sidebar-menu-item ${activeSection === 'settings' ? 'active' : ''}`}
              onClick={() => setActiveSection('settings')}
            >
              <FontAwesomeIcon icon={faGear} /> Account Settings
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="dashboard-content">
          {activeSection === 'projects' ? (
            <>
              {/* Create Project Button */}
              {!showCreateForm && (
                <div className="content-toolbar">
                  <button
                    className="create-project-btn"
                    onClick={() => setShowCreateForm(true)}
                    disabled={loading}
                  >
                    + New Project
                  </button>
                </div>
              )}

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
              <div className="projects-grid-container">
                {projects.length === 0 ? (
                  <div className="no-projects">
                    <p>No projects yet.</p>
                    <p>Create your first project to get started!</p>
                  </div>
                ) : (
                  projects.map((project) => (
                    <div
                      key={project.id}
                      className="project-rectangle"
                      onClick={() => onSelectProject(project)}
                    >
                      <div className="project-rectangle-header">
                        <h3>{project.name}</h3>
                        <button
                          className="delete-project-btn"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteProject(project.id, project.name);
                          }}
                          title="Delete project"
                        >
                          <FontAwesomeIcon icon={faTrash} />
                        </button>
                      </div>
                      <div className="project-rectangle-footer">
                        <span className="project-date">
                          Created {new Date(project.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </>
          ) : (
            /* Settings Section */
            <div className="settings-section">
              <div className="settings-card">
                <h2>Account Information</h2>
                <div className="settings-info">
                  <div className="info-row">
                    <span className="info-label">Username:</span>
                    <span className="info-value">{user?.username}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Email:</span>
                    <span className="info-value">{user?.email}</span>
                  </div>
                </div>
              </div>

              <div className="settings-card">
                <h2>Security</h2>

                {passwordSuccess && (
                  <div className="success-message">{passwordSuccess}</div>
                )}

                {!showPasswordForm ? (
                  <button
                    className="change-password-btn"
                    onClick={() => setShowPasswordForm(true)}
                  >
                    <FontAwesomeIcon icon={faLock} /> Change Password
                  </button>
                ) : (
                  <form onSubmit={handlePasswordChange} className="password-change-form">
                    {passwordError && (
                      <div className="error-message">{passwordError}</div>
                    )}

                    <div className="form-group">
                      <label>Current Password</label>
                      <input
                        type="password"
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        disabled={passwordLoading}
                        autoFocus
                      />
                    </div>

                    <div className="form-group">
                      <label>New Password</label>
                      <input
                        type="password"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        disabled={passwordLoading}
                        minLength="6"
                      />
                    </div>

                    <div className="form-group">
                      <label>Confirm New Password</label>
                      <input
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        disabled={passwordLoading}
                        minLength="6"
                      />
                    </div>

                    <div className="password-form-buttons">
                      <button
                        type="submit"
                        className="save-button"
                        disabled={passwordLoading}
                      >
                        {passwordLoading ? 'Changing...' : 'Change Password'}
                      </button>
                      <button
                        type="button"
                        className="cancel-button"
                        onClick={handleCancelPasswordChange}
                        disabled={passwordLoading}
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                )}
              </div>

              <div className="settings-card">
                <h2>Actions</h2>
                <button className="logout-btn" onClick={onLogout}>
                  <FontAwesomeIcon icon={faRightFromBracket} /> Logout
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
