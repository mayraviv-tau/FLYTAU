"""
Tests for flight endpoints.
"""

import pytest
import json


def test_search_flights_all(client):
    """Test searching all flights."""
    response = client.get('/api/flights')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'flights' in data['data']
    assert isinstance(data['data']['flights'], list)


def test_search_flights_by_origin(client):
    """Test searching flights by origin."""
    response = client.get('/api/flights?origin=TLV')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'flights' in data['data']


def test_search_flights_by_destination(client):
    """Test searching flights by destination."""
    response = client.get('/api/flights?destination=JFK')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True


def test_search_flights_by_date(client):
    """Test searching flights by date."""
    response = client.get('/api/flights?date=2026-04-01')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True


def test_get_flight_details(client):
    """Test getting flight details."""
    # First get list of flights
    flights_response = client.get('/api/flights')
    flights_data = json.loads(flights_response.data)

    if flights_data['data']['flights']:
        flight_id = flights_data['data']['flights'][0]['flight_id']

        # Get flight details
        response = client.get(f'/api/flights/{flight_id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'seat_map' in data['data']


def test_get_flight_not_found(client):
    """Test getting non-existent flight."""
    response = client.get('/api/flights/99999')

    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['success'] is False
