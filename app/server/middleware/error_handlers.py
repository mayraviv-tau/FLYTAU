"""
Global error handlers for FLYTAU application.
"""

from flask import jsonify
from mysql.connector import Error as MySQLError


class APIError(Exception):
    """Base API error class."""
    status_code = 400

    def __init__(self, message, status_code=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code


class AuthenticationError(APIError):
    """Authentication failed error."""
    status_code = 401


class AuthorizationError(APIError):
    """Authorization/permission error."""
    status_code = 403


class NotFoundError(APIError):
    """Resource not found error."""
    status_code = 404


class ValidationError(APIError):
    """Input validation error."""
    status_code = 400


class DatabaseError(APIError):
    """Database operation error."""
    status_code = 500


def register_error_handlers(app):
    """
    Register global error handlers with Flask app.

    Args:
        app: Flask application instance
    """

    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handle custom API errors."""
        response = {
            'success': False,
            'error': error.__class__.__name__,
            'message': error.message
        }
        return jsonify(response), error.status_code

    @app.errorhandler(MySQLError)
    def handle_mysql_error(error):
        """Handle MySQL errors."""
        response = {
            'success': False,
            'error': 'DatabaseError',
            'message': 'Database operation failed'
        }
        # Log the actual error for debugging
        app.logger.error(f"MySQL Error: {error}")
        return jsonify(response), 500

    @app.errorhandler(404)
    def handle_404(error):
        """Handle 404 Not Found."""
        response = {
            'success': False,
            'error': 'NotFound',
            'message': 'Resource not found'
        }
        return jsonify(response), 404

    @app.errorhandler(500)
    def handle_500(error):
        """Handle 500 Internal Server Error."""
        response = {
            'success': False,
            'error': 'InternalServerError',
            'message': 'Internal server error'
        }
        app.logger.error(f"Internal Error: {error}")
        return jsonify(response), 500
