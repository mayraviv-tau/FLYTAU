"""
Tests for admin report endpoints.
"""

import pytest
import json


def test_occupancy_report_not_authenticated(client):
    """Test getting occupancy report without authentication."""
    response = client.get('/api/admin/reports/occupancy')

    assert response.status_code == 401


def test_occupancy_report_customer_access(client, authenticated_customer):
    """Test getting occupancy report with customer credentials."""
    response = authenticated_customer.get('/api/admin/reports/occupancy')

    assert response.status_code == 403


def test_occupancy_report_manager_access(client, authenticated_manager):
    """Test getting occupancy report with manager credentials."""
    response = authenticated_manager.get('/api/admin/reports/occupancy')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'report_name' in data['data']


def test_revenue_report_manager_access(client, authenticated_manager):
    """Test getting revenue report with manager credentials."""
    response = authenticated_manager.get('/api/admin/reports/revenue')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True


def test_staff_hours_report_manager_access(client, authenticated_manager):
    """Test getting staff hours report with manager credentials."""
    response = authenticated_manager.get('/api/admin/reports/staff-hours')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True


def test_cancellations_report_manager_access(client, authenticated_manager):
    """Test getting cancellations report with manager credentials."""
    response = authenticated_manager.get('/api/admin/reports/cancellations')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True


def test_plane_activity_report_manager_access(client, authenticated_manager):
    """Test getting plane activity report with manager credentials."""
    response = authenticated_manager.get('/api/admin/reports/plane-activity')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
