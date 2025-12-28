"""
Pytest configuration and fixtures for FLYTAU tests.
"""

import pytest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from server import create_app


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
    })
    yield app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def sample_customer_data():
    """Sample customer registration data."""
    return {
        'email': 'test@example.com',
        'password': 'TestPassword123',
        'first_name': 'Test',
        'last_name': 'User',
        'birth_date': '1990-01-15',
        'passport_number': 'T12345678',
        'phone_numbers': ['050-1234567']
    }


@pytest.fixture
def sample_manager_data():
    """Sample manager login data."""
    return {
        'id_number': '200000001',  # From seed data
        'password': 'manager123'   # Plain text password from seed
    }


@pytest.fixture
def authenticated_customer(client, sample_customer_data):
    """Create authenticated customer session."""
    # Register customer
    client.post('/api/auth/register', json=sample_customer_data)

    # Login
    response = client.post('/api/auth/login', json={
        'email': sample_customer_data['email'],
        'password': sample_customer_data['password'],
        'user_type': 'customer'
    })

    return client


@pytest.fixture
def authenticated_manager(client, sample_manager_data):
    """Create authenticated manager session."""
    response = client.post('/api/auth/login', json={
        'email': sample_manager_data['id_number'],
        'password': sample_manager_data['password'],
        'user_type': 'manager'
    })

    return client
