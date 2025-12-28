"""
Tests for order and booking endpoints.
"""

import pytest
import json


def test_create_booking_not_authenticated(client):
    """Test creating booking without authentication."""
    response = client.post('/api/bookings', json={
        'flight_id': 1,
        'tickets': [
            {'class_type': 'Economy', 'seat_number': '15A', 'price': 800.0}
        ]
    })

    assert response.status_code == 401


def test_create_booking_missing_fields(client, authenticated_customer):
    """Test creating booking with missing fields."""
    response = authenticated_customer.post('/api/bookings', json={
        'flight_id': 1
    })

    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False


def test_get_orders_not_authenticated(client):
    """Test getting orders without authentication."""
    response = client.get('/api/orders')

    assert response.status_code == 401


def test_get_orders_authenticated(client, authenticated_customer):
    """Test getting orders for authenticated customer."""
    response = authenticated_customer.get('/api/orders')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'orders' in data['data']


def test_get_orders_with_filter(client, authenticated_customer):
    """Test getting orders with filter."""
    response = authenticated_customer.get('/api/orders?filter=future')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True


def test_get_order_details_not_found(client, authenticated_customer):
    """Test getting non-existent order."""
    response = authenticated_customer.get('/api/orders/99999')

    assert response.status_code == 404


def test_cancel_order_not_authenticated(client):
    """Test canceling order without authentication."""
    response = client.delete('/api/orders/1')

    assert response.status_code == 401
