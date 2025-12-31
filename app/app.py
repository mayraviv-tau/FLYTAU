"""
FLYTAU - Flight Management System
Main Flask Application
"""
from flask import Flask
from flask_session import Session
from config import Config
import os

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize session
    Session(app)
    
    # Register blueprints
    from routes import auth, flights, orders, reports, managers
    app.register_blueprint(auth.bp)
    app.register_blueprint(flights.bp)
    app.register_blueprint(orders.bp)
    app.register_blueprint(reports.bp)
    app.register_blueprint(managers.bp)
    
    @app.route('/')
    def index():
        """Home page"""
        from flask import redirect, url_for, session
        try:
            if session.get('manager_id'):
                return redirect(url_for('flights.list'))
            return redirect(url_for('flights.search'))
        except:
            return redirect(url_for('flights.search'))
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        from flask import render_template
        return '<h1>404 - Page Not Found</h1><p>הדף שביקשת לא נמצא</p>', 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        return '<h1>500 - Internal Server Error</h1><p>שגיאה בשרת</p>', 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)

