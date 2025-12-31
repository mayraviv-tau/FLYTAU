"""
WSGI entry point for PythonAnywhere
This file is used by PythonAnywhere to serve the Flask application

In PythonAnywhere, set the WSGI configuration file to point to this file.
Path in PythonAnywhere Web tab: /home/USERNAME/flytau/app/wsgi.py
"""
import sys
import os

# Add the app directory to the path so we can import app modules
# The path should point to the directory containing this wsgi.py file
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.insert(0, path)

# Import create_app from app.py
# Since wsgi.py is in the same directory as app.py, we can import directly
from app import create_app

# Create application instance
# PythonAnywhere expects a variable called 'application'
application = create_app()

