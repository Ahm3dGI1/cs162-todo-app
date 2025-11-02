"""
Tests for todo item CRUD operations, hierarchy, and move functionality.
"""
import pytest


class TestGetTodos:
    """Test getting todos for a project."""

    def test_get_todos_success(self, auth_client):
        """Test getting todos for a project."""
        # Create project
        project_response = auth_client.post('/api/projects', json={'name': 'Test Project'})
        project_id = project_response.get_json()['project']['id']

        # Create todo
        auth_client.post('/api/todos', json={
            'project_id': project_id,
            'title': 'Test Todo'
        })

        # Get todos
        response = auth_client.get(f'/api/todos/{project_id}')

        assert response.status_code == 200
        data = response.get_json()
        assert 'todos' in data
        assert len(data['todos']) == 1
        assert data['todos'][0]['title'] == 'Test Todo'

    def test_get_todos_empty(self, auth_client):
        """Test getting todos for project with no todos."""
        # Create project
        project_response = auth_client.post('/api/projects', json={'name': 'Empty Project'})
        project_id = project_response.get_json()['project']['id']

        # Get todos
        response = auth_client.get(f'/api/todos/{project_id}')

        assert response.status_code == 200
        data = response.get_json()
        assert 'todos' in data
        assert len(data['todos']) == 0

    def test_get_todos_unauthenticated(self, client):
        """Test getting todos when not authenticated."""
        response = client.get('/api/todos/1')
        assert response.status_code == 401


class TestCreateTodo:
    """Test creating todo items."""

    def test_create_todo_success(self, auth_client):
        """Test successful todo creation."""
        # Create project
        project_response = auth_client.post('/api/projects', json={'name': 'Test Project'})
        project_id = project_response.get_json()['project']['id']

        # Create todo
        response = auth_client.post('/api/todos', json={
            'project_id': project_id,
            'title': 'New Todo',
            'description': 'Test description',
            'priority': 'high'
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Todo created successfully'
        assert data['todo']['title'] == 'New Todo'
        assert data['todo']['description'] == 'Test description'
        assert data['todo']['priority'] == 'high'
        assert data['todo']['depth'] == 0

    def test_create_todo_missing_fields(self, auth_client):
        """Test creating todo with missing required fields."""
        response = auth_client.post('/api/todos', json={
            'title': 'No Project ID'
        })

        assert response.status_code == 400

    def test_create_todo_empty_title(self, auth_client):
        """Test creating todo with empty title."""
        # Create project
        project_response = auth_client.post('/api/projects', json={'name': 'Test Project'})
        project_id = project_response.get_json()['project']['id']

        response = auth_client.post('/api/todos', json={
            'project_id': project_id,
            'title': '   '
        })

        assert response.status_code == 400


class TestTodoHierarchy:
    """Test todo hierarchy (parent-child relationships)."""

    def test_create_subtask(self, auth_client):
        """Test creating a subtask under a parent todo."""
        # Create project
        project_response = auth_client.post('/api/projects', json={'name': 'Test Project'})
        project_id = project_response.get_json()['project']['id']

        # Create parent todo
        parent_response = auth_client.post('/api/todos', json={
            'project_id': project_id,
            'title': 'Parent Todo'
        })
        parent_id = parent_response.get_json()['todo']['id']

        # Create subtask
        response = auth_client.post('/api/todos', json={
            'project_id': project_id,
            'title': 'Subtask',
            'parent_id': parent_id
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['todo']['parent_id'] == parent_id
        assert data['todo']['depth'] == 1

    def test_create_three_level_hierarchy(self, auth_client):
        """Test creating maximum depth hierarchy (3 levels)."""
        # Create project
        project_response = auth_client.post('/api/projects', json={'name': 'Test Project'})
        project_id = project_response.get_json()['project']['id']

        # Create level 0 (parent)
        level0_response = auth_client.post('/api/todos', json={
            'project_id': project_id,
            'title': 'Level 0'
        })
        level0_id = level0_response.get_json()['todo']['id']

        # Create level 1 (child)
        level1_response = auth_client.post('/api/todos', json={
            'project_id': project_id,
            'title': 'Level 1',
            'parent_id': level0_id
        })
        level1_id = level1_response.get_json()['todo']['id']

        # Create level 2 (grandchild)
        level2_response = auth_client.post('/api/todos', json={
            'project_id': project_id,
            'title': 'Level 2',
            'parent_id': level1_id
        })

        assert level2_response.status_code == 201
        assert level2_response.get_json()['todo']['depth'] == 2

    def test_exceed_max_depth(self, auth_client):
        """Test that creating beyond max depth (level 3) is prevented."""
        # Create project
        project_response = auth_client.post('/api/projects', json={'name': 'Test Project'})
        project_id = project_response.get_json()['project']['id']

        # Create 3 levels
        level0 = auth_client.post('/api/todos', json={'project_id': project_id, 'title': 'L0'}).get_json()['todo']['id']
        level1 = auth_client.post('/api/todos', json={'project_id': project_id, 'title': 'L1', 'parent_id': level0}).get_json()['todo']['id']
        level2 = auth_client.post('/api/todos', json={'project_id': project_id, 'title': 'L2', 'parent_id': level1}).get_json()['todo']['id']

        # Try to create level 3 (should fail)
        response = auth_client.post('/api/todos', json={
            'project_id': project_id,
            'title': 'Level 3',
            'parent_id': level2
        })

        assert response.status_code == 400
        data = response.get_json()
        assert 'depth' in data['error'].lower() or 'maximum' in data['error'].lower()


class TestUpdateTodo:
    """Test updating todo items."""

    def test_update_todo_success(self, auth_client):
        """Test successful todo update."""
        # Create project and todo
        project_response = auth_client.post('/api/projects', json={'name': 'Test Project'})
        project_id = project_response.get_json()['project']['id']

        todo_response = auth_client.post('/api/todos', json={
            'project_id': project_id,
            'title': 'Original Title'
        })
        todo_id = todo_response.get_json()['todo']['id']

        # Update todo
        response = auth_client.put(f'/api/todos/{todo_id}', json={
            'title': 'Updated Title',
            'description': 'New description',
            'priority': 'low'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['todo']['title'] == 'Updated Title'
        assert data['todo']['description'] == 'New description'
        assert data['todo']['priority'] == 'low'

    def test_update_todo_completion(self, auth_client):
        """Test marking todo as complete."""
        # Create project and todo
        project_response = auth_client.post('/api/projects', json={'name': 'Test Project'})
        project_id = project_response.get_json()['project']['id']

        todo_response = auth_client.post('/api/todos', json={
            'project_id': project_id,
            'title': 'Todo to Complete'
        })
        todo_id = todo_response.get_json()['todo']['id']

        # Mark as complete
        response = auth_client.put(f'/api/todos/{todo_id}', json={
            'completed': True
        })

        assert response.status_code == 200
        assert response.get_json()['todo']['completed'] is True

    def test_update_todo_collapse(self, auth_client):
        """Test collapsing a todo."""
        # Create project and todo
        project_response = auth_client.post('/api/projects', json={'name': 'Test Project'})
        project_id = project_response.get_json()['project']['id']

        todo_response = auth_client.post('/api/todos', json={
            'project_id': project_id,
            'title': 'Collapsible Todo'
        })
        todo_id = todo_response.get_json()['todo']['id']

        # Collapse
        response = auth_client.put(f'/api/todos/{todo_id}', json={
            'collapsed': True
        })

        assert response.status_code == 200
        assert response.get_json()['todo']['collapsed'] is True


class TestDeleteTodo:
    """Test deleting todo items."""

    def test_delete_todo_success(self, auth_client):
        """Test successful todo deletion."""
        # Create project and todo
        project_response = auth_client.post('/api/projects', json={'name': 'Test Project'})
        project_id = project_response.get_json()['project']['id']

        todo_response = auth_client.post('/api/todos', json={
            'project_id': project_id,
            'title': 'To Be Deleted'
        })
        todo_id = todo_response.get_json()['todo']['id']

        # Delete todo
        response = auth_client.delete(f'/api/todos/{todo_id}')

        assert response.status_code == 200
        assert 'deleted successfully' in response.get_json()['message']

    def test_delete_todo_with_children(self, auth_client):
        """Test that deleting parent todo also deletes children (cascade)."""
        # Create project
        project_response = auth_client.post('/api/projects', json={'name': 'Test Project'})
        project_id = project_response.get_json()['project']['id']

        # Create parent and child
        parent_response = auth_client.post('/api/todos', json={
            'project_id': project_id,
            'title': 'Parent'
        })
        parent_id = parent_response.get_json()['todo']['id']

        child_response = auth_client.post('/api/todos', json={
            'project_id': project_id,
            'title': 'Child',
            'parent_id': parent_id
        })
        child_id = child_response.get_json()['todo']['id']

        # Delete parent
        delete_response = auth_client.delete(f'/api/todos/{parent_id}')
        assert delete_response.status_code == 200

        # Verify child is also deleted (get should fail)
        todos_response = auth_client.get(f'/api/todos/{project_id}')
        todos = todos_response.get_json()['todos']
        assert len(todos) == 0


class TestMoveTodo:
    """Test moving todos (reparenting)."""

    def test_move_todo_to_top_level(self, auth_client):
        """Test moving a subtask to top level."""
        # Create project
        project_response = auth_client.post('/api/projects', json={'name': 'Test Project'})
        project_id = project_response.get_json()['project']['id']

        # Create parent and child
        parent = auth_client.post('/api/todos', json={'project_id': project_id, 'title': 'Parent'}).get_json()['todo']
        child = auth_client.post('/api/todos', json={'project_id': project_id, 'title': 'Child', 'parent_id': parent['id']}).get_json()['todo']

        # Move child to top level
        response = auth_client.post(f'/api/todos/{child["id"]}/reparent', json={
            'new_parent_id': None,
            'new_project_id': project_id,
            'new_order': 0
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['todo']['parent_id'] is None
        assert data['todo']['depth'] == 0

    def test_move_todo_to_new_parent(self, auth_client):
        """Test moving a todo to a different parent."""
        # Create project
        project_response = auth_client.post('/api/projects', json={'name': 'Test Project'})
        project_id = project_response.get_json()['project']['id']

        # Create todos
        todo1 = auth_client.post('/api/todos', json={'project_id': project_id, 'title': 'Todo 1'}).get_json()['todo']
        todo2 = auth_client.post('/api/todos', json={'project_id': project_id, 'title': 'Todo 2'}).get_json()['todo']

        # Move todo2 under todo1
        response = auth_client.post(f'/api/todos/{todo2["id"]}/reparent', json={
            'new_parent_id': todo1['id'],
            'new_project_id': project_id,
            'new_order': 0
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['todo']['parent_id'] == todo1['id']
        assert data['todo']['depth'] == 1

    def test_move_todo_exceed_depth(self, auth_client):
        """Test that moving a task with subtasks validates depth limit."""
        # Create project
        project_response = auth_client.post('/api/projects', json={'name': 'Test Project'})
        project_id = project_response.get_json()['project']['id']

        # Create hierarchy: Task A -> Task B -> Task C
        taskA = auth_client.post('/api/todos', json={'project_id': project_id, 'title': 'Task A'}).get_json()['todo']
        taskB = auth_client.post('/api/todos', json={'project_id': project_id, 'title': 'Task B', 'parent_id': taskA['id']}).get_json()['todo']
        taskC = auth_client.post('/api/todos', json={'project_id': project_id, 'title': 'Task C', 'parent_id': taskB['id']}).get_json()['todo']

        # Create Task D at depth 1
        taskD = auth_client.post('/api/todos', json={'project_id': project_id, 'title': 'Task D'}).get_json()['todo']
        taskE = auth_client.post('/api/todos', json={'project_id': project_id, 'title': 'Task E', 'parent_id': taskD['id']}).get_json()['todo']

        # Try to move Task B (with child C) under Task E (this would make C depth 3)
        response = auth_client.post(f'/api/todos/{taskB["id"]}/reparent', json={
            'new_parent_id': taskE['id'],
            'new_project_id': project_id,
            'new_order': 0
        })

        assert response.status_code == 400
        assert 'depth' in response.get_json()['error'].lower()

    def test_move_todo_prevent_circular(self, auth_client):
        """Test that moving creates no circular dependencies."""
        # Create project
        project_response = auth_client.post('/api/projects', json={'name': 'Test Project'})
        project_id = project_response.get_json()['project']['id']

        # Create parent and child
        parent = auth_client.post('/api/todos', json={'project_id': project_id, 'title': 'Parent'}).get_json()['todo']
        child = auth_client.post('/api/todos', json={'project_id': project_id, 'title': 'Child', 'parent_id': parent['id']}).get_json()['todo']

        # Try to move parent under child (circular)
        response = auth_client.post(f'/api/todos/{parent["id"]}/reparent', json={
            'new_parent_id': child['id'],
            'new_project_id': project_id,
            'new_order': 0
        })

        assert response.status_code == 400
        assert 'circular' in response.get_json()['error'].lower() or 'descendant' in response.get_json()['error'].lower()

    def test_move_todo_to_different_project(self, auth_client):
        """Test moving a todo to a different project."""
        # Create two projects
        project1 = auth_client.post('/api/projects', json={'name': 'Project 1'}).get_json()['project']
        project2 = auth_client.post('/api/projects', json={'name': 'Project 2'}).get_json()['project']

        # Create todo in project 1
        todo = auth_client.post('/api/todos', json={'project_id': project1['id'], 'title': 'Todo'}).get_json()['todo']

        # Move to project 2
        response = auth_client.post(f'/api/todos/{todo["id"]}/reparent', json={
            'new_parent_id': None,
            'new_project_id': project2['id'],
            'new_order': 0
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['todo']['list_id'] == project2['id']

        # Verify it's in project 2
        todos_p2 = auth_client.get(f'/api/todos/{project2["id"]}').get_json()['todos']
        assert len(todos_p2) == 1
        assert todos_p2[0]['id'] == todo['id']
