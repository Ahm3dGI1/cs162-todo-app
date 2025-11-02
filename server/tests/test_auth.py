"""
Tests for authentication endpoints.
"""
import pytest
from models import User, db


class TestRegistration:
    """Test user registration endpoint."""

    def test_successful_registration(self, client):
        """Test successful user registration."""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123'
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'User registered successfully'
        assert data['user']['username'] == 'newuser'
        assert data['user']['email'] == 'newuser@example.com'
        assert 'password' not in data['user']

    def test_registration_missing_fields(self, client):
        """Test registration with missing required fields."""
        response = client.post('/api/auth/register', json={
            'username': 'newuser'
        })

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_registration_short_password(self, client):
        """Test registration with password too short."""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': '123'
        })

        assert response.status_code == 400
        data = response.get_json()
        assert 'Password must be at least 6 characters' in data['error']

    def test_registration_short_username(self, client):
        """Test registration with username too short."""
        response = client.post('/api/auth/register', json={
            'username': 'ab',
            'email': 'newuser@example.com',
            'password': 'password123'
        })

        assert response.status_code == 400
        data = response.get_json()
        assert 'Username must be at least 3 characters' in data['error']

    def test_registration_duplicate_username(self, client):
        """Test registration with existing username."""
        # Register first user
        client.post('/api/auth/register', json={
            'username': 'existinguser',
            'email': 'existing@example.com',
            'password': 'password123'
        })

        # Try to register with same username
        response = client.post('/api/auth/register', json={
            'username': 'existinguser',
            'email': 'different@example.com',
            'password': 'password123'
        })

        assert response.status_code == 400
        data = response.get_json()
        assert 'Username already exists' in data['error']

    def test_registration_duplicate_email(self, client):
        """Test registration with existing email."""
        # Register first user
        client.post('/api/auth/register', json={
            'username': 'user1',
            'email': 'same@example.com',
            'password': 'password123'
        })

        # Try to register with same email
        response = client.post('/api/auth/register', json={
            'username': 'user2',
            'email': 'same@example.com',
            'password': 'password123'
        })

        assert response.status_code == 400
        data = response.get_json()
        assert 'Email already registered' in data['error']


class TestLogin:
    """Test user login endpoint."""

    def test_successful_login(self, client):
        """Test successful login."""
        # Register user first
        client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })

        # Logout
        client.post('/api/auth/logout')

        # Login
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Login successful'
        assert data['user']['username'] == 'testuser'

    def test_login_missing_fields(self, client):
        """Test login with missing fields."""
        response = client.post('/api/auth/login', json={
            'username': 'testuser'
        })

        assert response.status_code == 400

    def test_login_wrong_password(self, client):
        """Test login with incorrect password."""
        # Register user
        client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'correctpassword'
        })

        client.post('/api/auth/logout')

        # Try to login with wrong password
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'wrongpassword'
        })

        assert response.status_code == 401
        data = response.get_json()
        assert 'Invalid' in data['error']

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'password123'
        })

        assert response.status_code == 401


class TestLogout:
    """Test user logout endpoint."""

    def test_successful_logout(self, auth_client):
        """Test successful logout."""
        response = auth_client.post('/api/auth/logout')

        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Logout successful'

    def test_logout_unauthenticated(self, client):
        """Test logout when not logged in."""
        response = client.post('/api/auth/logout')
        assert response.status_code == 401


class TestCurrentUser:
    """Test getting current user information."""

    def test_get_current_user_authenticated(self, auth_client):
        """Test getting current user when authenticated."""
        response = auth_client.get('/api/auth/current')

        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data
        assert data['user']['username'] == 'testuser'

    def test_get_current_user_unauthenticated(self, client):
        """Test getting current user when not authenticated."""
        response = client.get('/api/auth/current')

        assert response.status_code == 401


class TestChangePassword:
    """Test password change endpoint."""

    def test_successful_password_change(self, auth_client):
        """Test successful password change."""
        response = auth_client.post('/api/auth/change-password', json={
            'current_password': 'testpass123',
            'new_password': 'newpassword123'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Password changed successfully'

        # Verify can login with new password
        auth_client.post('/api/auth/logout')
        login_response = auth_client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'newpassword123'
        })
        assert login_response.status_code == 200

    def test_change_password_wrong_current(self, auth_client):
        """Test password change with incorrect current password."""
        response = auth_client.post('/api/auth/change-password', json={
            'current_password': 'wrongpassword',
            'new_password': 'newpassword123'
        })

        assert response.status_code == 401
        data = response.get_json()
        assert 'incorrect' in data['error'].lower()

    def test_change_password_short_new_password(self, auth_client):
        """Test password change with new password too short."""
        response = auth_client.post('/api/auth/change-password', json={
            'current_password': 'testpass123',
            'new_password': '123'
        })

        assert response.status_code == 400
        data = response.get_json()
        assert 'at least 6 characters' in data['error']

    def test_change_password_unauthenticated(self, client):
        """Test password change when not authenticated."""
        response = client.post('/api/auth/change-password', json={
            'current_password': 'testpass123',
            'new_password': 'newpassword123'
        })

        assert response.status_code == 401
