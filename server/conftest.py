"""
Pytest configuration and fixtures for testing.
"""
import pytest
import os
import sys
import tempfile

# Add the server directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User, TodoList, TodoItem


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    db_fd, db_path = tempfile.mkstemp()

    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SECRET_KEY': 'test-secret-key',
        'SESSION_TYPE': 'filesystem',
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def auth_client(client):
    """Create an authenticated test client."""
    # Register and login a test user
    client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    })

    yield client

    # Logout after test
    client.post('/api/auth/logout')


@pytest.fixture
def sample_user(app):
    """Create a sample user in the database."""
    with app.app_context():
        user = User(username='sampleuser', email='sample@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def sample_project(app, sample_user):
    """Create a sample project for testing."""
    with app.app_context():
        project = TodoList(name='Test Project', user_id=sample_user)
        db.session.add(project)
        db.session.commit()
        return project.id


@pytest.fixture
def sample_todo(app, sample_project, sample_user):
    """Create a sample todo item for testing."""
    with app.app_context():
        todo = TodoItem(
            title='Test Todo',
            description='Test description',
            list_id=sample_project,
            user_id=sample_user,
            priority='medium',
            depth=0
        )
        db.session.add(todo)
        db.session.commit()
        return todo.id
