"""
Authentication utility functions
"""
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from database import execute_query

def hash_password(password):
    """Hash a password using werkzeug"""
    return generate_password_hash(password)

def verify_password_hash(password_hash, password):
    """Check if password matches hash"""
    return check_password_hash(password_hash, password)

def is_logged_in():
    """Check if user is logged in"""
    return 'user_email' in session or 'manager_id' in session

def is_manager():
    """Check if logged in user is a manager"""
    return 'manager_id' in session

def get_current_user_email():
    """Get current logged in user email"""
    return session.get('user_email')

def get_current_manager_id():
    """Get current logged in manager ID"""
    return session.get('manager_id')

def login_customer(email):
    """Set session for customer login"""
    session['user_email'] = email
    session['user_type'] = 'customer'

def login_manager(manager_id):
    """Set session for manager login"""
    session['manager_id'] = manager_id
    session['user_type'] = 'manager'

def logout():
    """Clear session"""
    session.clear()

def verify_customer(email, password):
    """Verify customer credentials"""
    query = """
        SELECT email, account_password
        FROM RegisteredCustomer
        WHERE email = %s
    """
    user = execute_query(query, (email,), fetch_one=True)

    if user and verify_password_hash(user['account_password'], password):
        return True
    return False

def verify_manager(manager_id, password):
    """Verify manager credentials"""
    query = """
        SELECT id_number, account_password
        FROM Manager
        WHERE id_number = %s
    """
    manager = execute_query(query, (manager_id,), fetch_one=True)

    if manager and verify_password_hash(manager['account_password'], password):
        return True
    return False

