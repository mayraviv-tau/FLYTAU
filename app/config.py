"""
Configuration file for FLYTAU Flask application
"""
import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or '1234'
    DB_NAME = os.environ.get('DB_NAME') or 'flytau'
    DB_PORT = int(os.environ.get('DB_PORT') or 3306)
    
    # Session configuration
    SESSION_TYPE = os.environ.get('SESSION_TYPE') or 'filesystem'
    SESSION_PERMANENT = False
    
    # Application settings
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

