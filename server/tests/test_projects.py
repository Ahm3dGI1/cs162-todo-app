"""
Tests for project/list CRUD operations.
"""
import pytest


class TestGetProjects:
    """Test getting user projects."""

    def test_get_projects_authenticated(self, auth_client):
        """Test getting projects when authenticated."""
        # Create a project first
        auth_client.post('/api/projects', json={'name': 'Test Project'})

        response = auth_client.get('/api/projects')

        assert response.status_code == 200
        data = response.get_json()
        assert 'projects' in data
        assert len(data['projects']) >= 1
        assert data['projects'][0]['name'] == 'Test Project'

    def test_get_projects_unauthenticated(self, client):
        """Test getting projects when not authenticated."""
        response = client.get('/api/projects')
        assert response.status_code == 401

    def test_get_projects_empty_list(self, auth_client):
        """Test getting projects when user has no projects."""
        response = auth_client.get('/api/projects')

        assert response.status_code == 200
        data = response.get_json()
        assert 'projects' in data
        assert isinstance(data['projects'], list)


class TestCreateProject:
    """Test creating projects."""

    def test_create_project_success(self, auth_client):
        """Test successful project creation."""
        response = auth_client.post('/api/projects', json={
            'name': 'New Project'
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Project created successfully'
        assert data['project']['name'] == 'New Project'
        assert 'id' in data['project']

    def test_create_project_missing_name(self, auth_client):
        """Test creating project without name."""
        response = auth_client.post('/api/projects', json={})

        assert response.status_code == 400
        data = response.get_json()
        assert 'required' in data['error'].lower()

    def test_create_project_empty_name(self, auth_client):
        """Test creating project with empty name."""
        response = auth_client.post('/api/projects', json={
            'name': '   '
        })

        assert response.status_code == 400
        data = response.get_json()
        assert 'empty' in data['error'].lower()

    def test_create_project_name_too_long(self, auth_client):
        """Test creating project with name exceeding max length."""
        long_name = 'a' * 201
        response = auth_client.post('/api/projects', json={
            'name': long_name
        })

        assert response.status_code == 400
        data = response.get_json()
        assert '200 characters' in data['error']

    def test_create_project_unauthenticated(self, client):
        """Test creating project when not authenticated."""
        response = client.post('/api/projects', json={
            'name': 'Test Project'
        })

        assert response.status_code == 401


class TestGetSingleProject:
    """Test getting a single project by ID."""

    def test_get_project_success(self, auth_client):
        """Test getting a project successfully."""
        # Create project
        create_response = auth_client.post('/api/projects', json={
            'name': 'Test Project'
        })
        project_id = create_response.get_json()['project']['id']

        # Get project
        response = auth_client.get(f'/api/projects/{project_id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['project']['id'] == project_id
        assert data['project']['name'] == 'Test Project'

    def test_get_project_not_found(self, auth_client):
        """Test getting non-existent project."""
        response = auth_client.get('/api/projects/99999')

        assert response.status_code == 404

    def test_get_project_unauthorized(self, client):
        """Test getting project when not authenticated."""
        response = client.get('/api/projects/1')

        assert response.status_code == 401


class TestUpdateProject:
    """Test updating projects."""

    def test_update_project_success(self, auth_client):
        """Test successful project update."""
        # Create project
        create_response = auth_client.post('/api/projects', json={
            'name': 'Original Name'
        })
        project_id = create_response.get_json()['project']['id']

        # Update project
        response = auth_client.put(f'/api/projects/{project_id}', json={
            'name': 'Updated Name'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Project updated successfully'
        assert data['project']['name'] == 'Updated Name'

    def test_update_project_missing_name(self, auth_client):
        """Test updating project without providing name."""
        # Create project
        create_response = auth_client.post('/api/projects', json={
            'name': 'Test Project'
        })
        project_id = create_response.get_json()['project']['id']

        # Try to update without name
        response = auth_client.put(f'/api/projects/{project_id}', json={})

        assert response.status_code == 400

    def test_update_project_not_found(self, auth_client):
        """Test updating non-existent project."""
        response = auth_client.put('/api/projects/99999', json={
            'name': 'New Name'
        })

        assert response.status_code == 404

    def test_update_project_unauthenticated(self, client):
        """Test updating project when not authenticated."""
        response = client.put('/api/projects/1', json={
            'name': 'New Name'
        })

        assert response.status_code == 401


class TestDeleteProject:
    """Test deleting projects."""

    def test_delete_project_success(self, auth_client):
        """Test successful project deletion."""
        # Create project
        create_response = auth_client.post('/api/projects', json={
            'name': 'To Be Deleted'
        })
        project_id = create_response.get_json()['project']['id']

        # Delete project
        response = auth_client.delete(f'/api/projects/{project_id}')

        assert response.status_code == 200
        data = response.get_json()
        assert 'deleted successfully' in data['message']

        # Verify project is deleted
        get_response = auth_client.get(f'/api/projects/{project_id}')
        assert get_response.status_code == 404

    def test_delete_project_not_found(self, auth_client):
        """Test deleting non-existent project."""
        response = auth_client.delete('/api/projects/99999')

        assert response.status_code == 404

    def test_delete_project_unauthenticated(self, client):
        """Test deleting project when not authenticated."""
        response = client.delete('/api/projects/1')

        assert response.status_code == 401

    def test_delete_project_with_todos(self, auth_client):
        """Test that deleting project also deletes its todos (cascade)."""
        # Create project
        create_response = auth_client.post('/api/projects', json={
            'name': 'Project with Todos'
        })
        project_id = create_response.get_json()['project']['id']

        # Create todo in project
        auth_client.post('/api/todos', json={
            'project_id': project_id,
            'title': 'Test Todo'
        })

        # Delete project
        delete_response = auth_client.delete(f'/api/projects/{project_id}')
        assert delete_response.status_code == 200

        # Verify todos are also deleted
        todos_response = auth_client.get(f'/api/todos/{project_id}')
        assert todos_response.status_code == 404
