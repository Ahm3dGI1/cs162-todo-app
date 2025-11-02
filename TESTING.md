---
noteId: "810a8690b83a11f0aec70f1c7b620dce"
tags: []

---

# Testing Documentation

This document describes the test suites for the Hierarchical Todo Application.

## Overview

The project includes comprehensive test coverage for both backend (Flask/Python) and frontend (React/JavaScript) components.

## Backend Tests (Python/pytest)

### Setup

1. **Install test dependencies:**
   ```bash
   cd server
   pip install -r requirements-dev.txt
   ```

2. **The test dependencies include:**
   - `pytest` - Testing framework
   - `pytest-flask` - Flask-specific test utilities
   - `pytest-cov` - Code coverage reports

### Test Structure

```
server/
├── tests/
│   ├── __init__.py
│   ├── test_auth.py          # Authentication tests
│   ├── test_projects.py      # Project CRUD tests
│   └── test_todos.py         # Todo CRUD, hierarchy, and move tests
└── conftest.py               # Pytest fixtures and configuration
```

### Running Backend Tests

```bash
cd server

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth.py

# Run specific test class
pytest tests/test_auth.py::TestLogin

# Run specific test
pytest tests/test_auth.py::TestLogin::test_successful_login

# Run with coverage report
pytest --cov=. --cov-report=html

# Run with coverage and show missing lines
pytest --cov=. --cov-report=term-missing
```

### Test Categories

#### 1. Authentication Tests (`test_auth.py`)
- **TestRegistration**
  - Successful registration
  - Missing fields validation
  - Password length validation
  - Username length validation
  - Duplicate username/email prevention

- **TestLogin**
  - Successful login
  - Wrong password handling
  - Non-existent user handling
  - Missing fields validation

- **TestLogout**
  - Successful logout
  - Unauthenticated logout attempt

- **TestCurrentUser**
  - Get authenticated user info
  - Get unauthenticated user (should fail)

- **TestChangePassword**
  - Successful password change
  - Wrong current password
  - New password too short
  - Unauthenticated attempt

#### 2. Project Tests (`test_projects.py`)
- **TestGetProjects**
  - Get projects when authenticated
  - Get projects when unauthenticated
  - Get empty project list

- **TestCreateProject**
  - Successful project creation
  - Missing/empty name validation
  - Name length validation
  - Unauthenticated creation

- **TestGetSingleProject**
  - Get existing project
  - Get non-existent project
  - Unauthorized access

- **TestUpdateProject**
  - Successful update
  - Missing fields
  - Non-existent project
  - Unauthenticated update

- **TestDeleteProject**
  - Successful deletion
  - Non-existent project
  - Cascade deletion with todos
  - Unauthenticated deletion

#### 3. Todo Tests (`test_todos.py`)
- **TestGetTodos**
  - Get todos for project
  - Get empty todo list
  - Unauthenticated access

- **TestCreateTodo**
  - Successful creation
  - Missing required fields
  - Empty title validation

- **TestTodoHierarchy**
  - Create subtask (1 level deep)
  - Create 3-level hierarchy (max depth)
  - Prevent exceeding max depth (4 levels)

- **TestUpdateTodo**
  - Update title/description/priority
  - Mark as complete
  - Collapse/expand todo

- **TestDeleteTodo**
  - Successful deletion
  - Cascade delete with children

- **TestMoveTodo**
  - Move subtask to top level
  - Move to different parent
  - Prevent depth limit violations
  - Prevent circular dependencies
  - Move to different project

### Fixtures

The `conftest.py` file provides reusable fixtures:

- `app` - Test Flask application with test database
- `client` - Test client for making requests
- `auth_client` - Pre-authenticated test client
- `sample_user` - Sample user in database
- `sample_project` - Sample project for testing
- `sample_todo` - Sample todo item for testing

### Example Test Usage

```python
def test_create_project_success(auth_client):
    """Test with authenticated client."""
    response = auth_client.post('/api/projects', json={
        'name': 'Test Project'
    })
    assert response.status_code == 201

def test_get_projects_unauthenticated(client):
    """Test with unauthenticated client."""
    response = client.get('/api/projects')
    assert response.status_code == 401
```