"""
WSGI entry point for PythonAnywhere
This file is used by PythonAnywhere to serve the Flask application
"""
import sys
import os

path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.insert(0, path)

from app import create_app

application = create_app()

