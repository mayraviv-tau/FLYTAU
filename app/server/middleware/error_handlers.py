"""
Global error handlers for FLYTAU application.
Simplified for academic exercise.
"""

from flask import jsonify
from mysql.connector import Error as MySQLError


class APIError(Exception):
    """
    Base API error class.
    Use with different status codes instead of subclassing.

    Usage:
        raise APIError("Invalid email", 400)
        raise APIError("Not authenticated", 401)
        raise APIError("Not authorized", 403)
        raise APIError("Not found", 404)
        raise APIError("Server error", 500)
    """

    def __init__(self, message, status_code=400):
        super().__init__()
        self.message = message
        self.status_code = status_code


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
            'error': 'APIError',
            'message': error.message
        }
        return jsonify(response), error.status_code

    @app.errorhandler(MySQLError)
    def handle_mysql_error(error):
        """Handle MySQL errors - show actual error for easier debugging."""
        response = {
            'success': False,
            'error': 'DatabaseError',
            'message': f'Database error: {str(error)}'  # Show actual error for academic demo
        }
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
            'message': f'Internal server error: {str(error)}'  # Show error for debugging
        }
        app.logger.error(f"Internal Error: {error}")
        return jsonify(response), 500
