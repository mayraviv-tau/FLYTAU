"""
Main entry point for FLYTAU Flask application.
Run this file to start the server.
"""

import os
from . import create_app

# Create Flask app
app = create_app()

if __name__ == '__main__':
    # Get configuration from environment
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    print(f"Starting FLYTAU Flask server on {host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")

    app.run(host=host, port=port, debug=debug)
