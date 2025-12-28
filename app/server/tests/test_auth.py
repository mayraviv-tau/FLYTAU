"""
Tests for authentication endpoints.
"""

import pytest
import json


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'


def test_register_customer_success(client, sample_customer_data):
    """Test successful customer registration."""
    response = client.post('/api/auth/register', json=sample_customer_data)

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['data']['email'] == sample_customer_data['email']
    assert data['data']['is_registered'] is True


def test_register_duplicate_email(client, sample_customer_data):
    """Test registration with duplicate email."""
    # Register once
    client.post('/api/auth/register', json=sample_customer_data)

    # Try to register again
    response = client.post('/api/auth/register', json=sample_customer_data)

    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False
    assert 'already registered' in data['message'].lower()


def test_register_invalid_password(client, sample_customer_data):
    """Test registration with invalid password."""
    sample_customer_data['password'] = 'short'

    response = client.post('/api/auth/register', json=sample_customer_data)

    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False


def test_login_customer_success(client, sample_customer_data):
    """Test successful customer login."""
    # Register first
    client.post('/api/auth/register', json=sample_customer_data)

    # Logout
    client.post('/api/auth/logout')

    # Login
    response = client.post('/api/auth/login', json={
        'email': sample_customer_data['email'],
        'password': sample_customer_data['password'],
        'user_type': 'customer'
    })

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['data']['user_type'] == 'customer'


def test_login_wrong_password(client, sample_customer_data):
    """Test login with wrong password."""
    # Register first
    client.post('/api/auth/register', json=sample_customer_data)

    # Logout
    client.post('/api/auth/logout')

    # Try to login with wrong password
    response = client.post('/api/auth/login', json={
        'email': sample_customer_data['email'],
        'password': 'WrongPassword123',
        'user_type': 'customer'
    })

    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['success'] is False


def test_logout(client, authenticated_customer):
    """Test logout."""
    response = authenticated_customer.post('/api/auth/logout')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True


def test_get_current_user(client, authenticated_customer):
    """Test getting current user info."""
    response = authenticated_customer.get('/api/auth/me')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'email' in data['data']


def test_get_current_user_not_authenticated(client):
    """Test getting current user without authentication."""
    response = client.get('/api/auth/me')

    assert response.status_code == 401
