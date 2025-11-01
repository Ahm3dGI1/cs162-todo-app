import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faXmark, faTableCells, faRightFromBracket } from '@fortawesome/free-solid-svg-icons';

function Sidebar({ isOpen, onClose, currentProject, onBackToDashboard, user, onLogout }) {
  return (
    <>
      {/* Overlay */}
      {isOpen && <div className="sidebar-overlay" onClick={onClose}></div>}

      {/* Sidebar */}
      <div className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <button className="close-sidebar-btn" onClick={onClose}>
            <FontAwesomeIcon icon={faXmark} />
          </button>
        </div>

        <div className="sidebar-content">
          {/* User Info */}
          <div className="sidebar-user">
            <div className="user-avatar">
              {user.username.charAt(0).toUpperCase()}
            </div>
            <div className="user-details">
              <div className="user-name">{user.username}</div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="sidebar-nav">
            {currentProject && (
              <div className="current-project-info">
                <div className="current-project-label">Current Project</div>
                <div className="current-project-name">{currentProject.name}</div>
              </div>
            )}

            <button className="sidebar-nav-btn" onClick={onBackToDashboard}>
              <span className="nav-icon"><FontAwesomeIcon icon={faTableCells} /></span>
              <span>All Projects</span>
            </button>

            <div className="sidebar-divider"></div>

            <button className="sidebar-nav-btn logout-btn" onClick={onLogout}>
              <span className="nav-icon"><FontAwesomeIcon icon={faRightFromBracket} /></span>
              <span>Logout</span>
            </button>
          </nav>
        </div>
      </div>
    </>
  );
}

export default Sidebar;
