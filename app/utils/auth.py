"""
Authentication utility functions
"""
from flask import session
from database import execute_query

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

    # Get customer's first name to display in header
    query = "SELECT first_name_english FROM Customer WHERE LOWER(email) = %s"
    customer = execute_query(query, (email.lower(),), fetch_one=True)
    if customer:
        session['user_name'] = customer['first_name_english']

def login_manager(manager_id):
    """Set session for manager login"""
    session['manager_id'] = manager_id
    session['user_type'] = 'manager'

    # Get manager's first name to display in header
    query = "SELECT first_name_hebrew FROM Manager WHERE id_number = %s"
    manager = execute_query(query, (manager_id,), fetch_one=True)
    if manager:
        session['manager_name'] = manager['first_name_hebrew']

def logout():
    """Clear session"""
    session.clear()

def verify_customer(email, password):
    """Verify customer credentials - plain text comparison"""
    email = email.strip().lower() if email else ''
    
    query = """
        SELECT email, account_password
        FROM RegisteredCustomer
        WHERE LOWER(email) = %s
    """
    user = execute_query(query, (email,), fetch_one=True)

    if not user:
        return False
    
    stored_password = user['account_password']
    
    if not stored_password:
        return False
    
    # Simple plain text comparison
    return stored_password == password

def verify_manager(manager_id, password):
    """Verify manager credentials - plain text comparison"""
    query = """
        SELECT id_number, account_password
        FROM Manager
        WHERE id_number = %s
    """
    manager = execute_query(query, (manager_id,), fetch_one=True)

    if not manager:
        return False
    
    stored_password = manager['account_password']
    
    if not stored_password:
        return False
    
    # Simple plain text comparison
    return stored_password == password
