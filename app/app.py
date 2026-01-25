"""
FLYTAU - Flight Management System
Main Flask Application
"""
from flask import Flask
from config import Config
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = 'GROUP_14'

    from routes import auth, flights, orders, reports, managers
    app.register_blueprint(auth.bp)
    app.register_blueprint(flights.bp)
    app.register_blueprint(orders.bp, url_prefix='/orders')
    app.register_blueprint(reports.bp, url_prefix='/reports')
    app.register_blueprint(managers.bp)

    @app.route('/')
    def index():
        from flask import redirect, url_for, session
        if session.get('manager_id'):
            return redirect(url_for('flights.list'))
        return redirect(url_for('flights.search'))

    @app.errorhandler(404)
    def not_found(error):
        return '<h1>404 - Page Not Found</h1>', 404

    @app.errorhandler(500)
    def internal_error(error):
        return '<h1>500 - Internal Server Error</h1>', 500

    return app

if __name__ == '__main__':
    app = create_app()
    print("Starting FLYTAU server...")
    print("Local URL: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)