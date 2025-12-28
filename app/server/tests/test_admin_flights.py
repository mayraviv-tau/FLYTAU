"""
Tests for admin flight management endpoints.
"""

import pytest
import json


def test_create_flight_not_authenticated(client):
    """Test creating flight without authentication."""
    response = client.post('/api/admin/flights', json={
        'origin_airport': 'TLV',
        'destination_airport': 'JFK',
        'plane_id': 1,
        'departure_datetime': '2026-06-01T10:00:00',
        'pilot_ids': ['300000001', '300000002', '300000003'],
        'attendant_ids': ['400000001', '400000002', '400000003', '400000004', '400000005', '400000006']
    })

    assert response.status_code == 401


def test_create_flight_customer_access(client, authenticated_customer):
    """Test creating flight with customer credentials."""
    response = authenticated_customer.post('/api/admin/flights', json={
        'origin_airport': 'TLV',
        'destination_airport': 'JFK',
        'plane_id': 1,
        'departure_datetime': '2026-06-01T10:00:00',
        'pilot_ids': ['300000001', '300000002', '300000003'],
        'attendant_ids': ['400000001', '400000002', '400000003', '400000004', '400000005', '400000006']
    })

    assert response.status_code == 403
    data = json.loads(response.data)
    assert data['success'] is False


def test_create_flight_missing_fields(client, authenticated_manager):
    """Test creating flight with missing fields."""
    response = authenticated_manager.post('/api/admin/flights', json={
        'origin_airport': 'TLV'
    })

    assert response.status_code == 400


def test_cancel_flight_not_authenticated(client):
    """Test canceling flight without authentication."""
    response = client.delete('/api/admin/flights/1')

    assert response.status_code == 401


def test_cancel_flight_not_found(client, authenticated_manager):
    """Test canceling non-existent flight."""
    response = authenticated_manager.delete('/api/admin/flights/99999')

    assert response.status_code == 404
