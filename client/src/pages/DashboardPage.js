import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Dashboard from '../components/Dashboard';
import { API_ENDPOINTS } from '../config/api';

function DashboardPage({ user, onLogout }) {
  const [projects, setProjects] = useState([]);
  const [projectsLoading, setProjectsLoading] = useState(false);
  const navigate = useNavigate();

  /**
   * Fetch all projects for the current user
   */
  const fetchProjects = async () => {
    setProjectsLoading(true);
    try {
      const response = await fetch(API_ENDPOINTS.PROJECTS, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setProjects(data.projects);
      } else {
        console.error('Failed to fetch projects');
      }
    } catch (error) {
      console.error('Error fetching projects:', error);
    } finally {
      setProjectsLoading(false);
    }
  };

  /**
   * Create a new project
   */
  const handleCreateProject = async (name) => {
    const response = await fetch(API_ENDPOINTS.PROJECTS, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({ name })
    });

    if (response.ok) {
      const data = await response.json();
      const newProject = data.project;
      setProjects([...projects, newProject]);
    } else {
      const error = await response.json();
      throw new Error(error.error || 'Failed to create project');
    }
  };

  /**
   * Select a project and navigate to it
   */
  const handleSelectProject = (project) => {
    // Navigate to the project page with the project ID
    navigate(`/project/${project.id}`, { state: { project } });
  };

  /**
   * Delete a project
   */
  const handleDeleteProject = async (projectId) => {
    const response = await fetch(`${API_ENDPOINTS.PROJECTS}/${projectId}`, {
      method: 'DELETE',
      credentials: 'include'
    });

    if (response.ok) {
      const updatedProjects = projects.filter(project => project.id !== projectId);
      setProjects(updatedProjects);
    } else {
      const error = await response.json();
      throw new Error(error.error || 'Failed to delete project');
    }
  };

  /**
   * Load projects when component mounts
   */
  useEffect(() => {
    if (user) {
      fetchProjects();
    }
  }, [user]);

  if (projectsLoading) {
    return (
      <div className="loading">Loading projects...</div>
    );
  }

  return (
    <Dashboard
      projects={projects}
      onSelectProject={handleSelectProject}
      onCreateProject={handleCreateProject}
      onDeleteProject={handleDeleteProject}
      user={user}
      onLogout={onLogout}
    />
  );
}

export default DashboardPage;
