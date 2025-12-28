"""
Global error handlers for FLYTAU application.
Simplified for academic exercise.
"""

from flask import jsonify, render_template, request
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

    def wants_json():
        """Check if request wants JSON response."""
        return request.path.startswith('/api/') or \
               request.accept_mimetypes.best_match(['application/json', 'text/html']) == 'application/json'

    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handle custom API errors."""
        if wants_json():
            response = {
                'success': False,
                'error': 'APIError',
                'message': error.message
            }
            return jsonify(response), error.status_code
        else:
            # HTML response for UI
            from flask import flash, redirect, url_for, session
            flash(error.message, 'error')
            # For auth errors, redirect to login
            if error.status_code == 401:
                session.clear()
                return redirect(url_for('public.login'))
            # For other errors, try to render error page
            try:
                return render_template('errors/error.html',
                                     error=error.message,
                                     status_code=error.status_code), error.status_code
            except:
                # Fallback if template doesn't exist
                return f"<h1>Error {error.status_code}</h1><p>{error.message}</p>", error.status_code

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
        if wants_json():
            response = {
                'success': False,
                'error': 'NotFound',
                'message': 'Resource not found'
            }
            return jsonify(response), 404
        else:
            try:
                return render_template('errors/404.html'), 404
            except:
                return "<h1>404 - Page Not Found</h1>", 404

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
