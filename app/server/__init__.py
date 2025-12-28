"""
Flask application factory for FLYTAU.
"""

import os
from flask import Flask
from flask_session import Session

from .config import get_config
from .db.connection import init_db_pool
from .middleware.error_handlers import register_error_handlers


def create_app(config_name=None):
    """
    Create and configure the Flask application.

    Args:
        config_name (str): Configuration name (development, production, testing)

    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__,
                template_folder='../ui/templates',
                static_folder='../ui/static')

    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Create session directory if it doesn't exist
    if not os.path.exists(app.config['SESSION_FILE_DIR']):
        os.makedirs(app.config['SESSION_FILE_DIR'])

    # Initialize session
    Session(app)

    # Initialize database connection pool
    init_db_pool(app.config)

    # Register error handlers
    register_error_handlers(app)

    # Register blueprints
    register_blueprints(app)

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'FLYTAU API'}, 200

    return app


def register_blueprints(app):
    """
    Register all route blueprints.

    Args:
        app: Flask application
    """
    # API blueprints
    from .routes import auth, flights, orders, admin_flights, admin_reports

    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(flights.bp, url_prefix='/api')
    app.register_blueprint(orders.bp, url_prefix='/api')
    app.register_blueprint(admin_flights.bp, url_prefix='/api/admin')
    app.register_blueprint(admin_reports.bp, url_prefix='/api/admin/reports')

    # UI blueprints
    import sys
    import os
    # Add parent directory to path for UI imports
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    from ui.routes import public, customer, manager

    app.register_blueprint(public.bp, url_prefix='')
    app.register_blueprint(customer.bp, url_prefix='/customer')
    app.register_blueprint(manager.bp, url_prefix='/manager')
