"""
Authentication middleware for FLYTAU application.
Provides decorators for route protection.
Simplified to use APIError.
"""

from functools import wraps
from flask import session
from .error_handlers import APIError


def login_required(f):
    """
    Decorator to require authentication for a route.
    User must be logged in (customer or manager).

    Usage:
        @app.route('/protected')
        @login_required
        def protected_route():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            raise APIError("Authentication required. Please log in.", 401)
        return f(*args, **kwargs)
    return decorated_function


def manager_required(f):
    """
    Decorator to require manager authentication for a route.
    User must be logged in as a manager.

    Usage:
        @app.route('/admin')
        @manager_required
        def admin_route():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            raise APIError("Authentication required. Please log in.", 401)

        if session.get('user_type') != 'manager':
            raise APIError("Manager access required.", 403)

        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """
    Get current user information from session.

    Returns:
        dict: User information or None if not logged in
    """
    if 'user_id' not in session:
        return None

    return {
        'user_id': session.get('user_id'),
        'user_type': session.get('user_type'),
        'first_name': session.get('first_name'),
        'last_name': session.get('last_name'),
        'is_registered': session.get('is_registered', False)
    }
