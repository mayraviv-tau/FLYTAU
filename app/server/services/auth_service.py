"""
Authentication service for FLYTAU application.
Handles user registration and login.
"""

from datetime import date
from ..db import execute_query, execute_transaction
from ..db.queries import *
from ..utils.password import hash_password, verify_password
from ..utils.validators import validate_email, validate_password
from ..middleware.error_handlers import ValidationError, AuthenticationError
from ..models.user import User, RegisteredCustomer, Manager


def register_customer(email, password, first_name, last_name, birth_date, passport_number, phone_numbers=None):
    """
    Register a new customer.

    Args:
        email (str): Customer email
        password (str): Plain text password
        first_name (str): First name
        last_name (str): Last name
        birth_date (str): Birth date (YYYY-MM-DD)
        passport_number (str): Passport number
        phone_numbers (list): Optional list of phone numbers

    Returns:
        RegisteredCustomer: Created customer object

    Raises:
        ValidationError: If validation fails
    """
    # Validate email
    if not validate_email(email):
        raise ValidationError("Invalid email format")

    # Validate password
    is_valid, error_msg = validate_password(password)
    if not is_valid:
        raise ValidationError(error_msg)

    # Check if customer already exists
    existing = execute_query(CHECK_CUSTOMER_EXISTS, (email,), fetch_one=True)
    if existing:
        raise ValidationError("Email already registered")

    # Hash password
    hashed_password = hash_password(password)

    # Prepare transaction operations
    operations = [
        # Insert into Customer table
        (INSERT_CUSTOMER, (email, first_name, last_name)),
        # Insert into RegisteredCustomer table
        (INSERT_REGISTERED_CUSTOMER, (email, str(date.today()), birth_date, passport_number, hashed_password))
    ]

    # Add phone numbers if provided
    if phone_numbers:
        for phone in phone_numbers:
            operations.append((INSERT_CUSTOMER_PHONE, (email, phone)))

    # Execute transaction
    execute_transaction(operations)

    # Return customer object
    return RegisteredCustomer(
        email=email,
        first_name=first_name,
        last_name=last_name,
        balance=0.0,
        birth_date=birth_date,
        passport_number=passport_number
    )


def login_user(email_or_id, password, user_type='customer'):
    """
    Authenticate a user (customer or manager).

    Args:
        email_or_id (str): Email (customer) or ID number (manager)
        password (str): Plain text password
        user_type (str): 'customer' or 'manager'

    Returns:
        dict: User information for session

    Raises:
        AuthenticationError: If authentication fails
    """
    if user_type == 'customer':
        # Query registered customer
        user_data = execute_query(GET_REGISTERED_CUSTOMER, (email_or_id,), fetch_one=True)

        if not user_data:
            raise AuthenticationError("Invalid email or password")

        # Verify password
        if not verify_password(password, user_data['account_password']):
            raise AuthenticationError("Invalid email or password")

        return {
            'user_id': user_data['email'],
            'user_type': 'customer',
            'first_name': user_data['first_name_english'],
            'last_name': user_data['last_name_english'],
            'is_registered': True,
            'balance': float(user_data['balance'])
        }

    elif user_type == 'manager':
        # Query manager
        manager_data = execute_query(GET_MANAGER, (email_or_id,), fetch_one=True)

        if not manager_data:
            raise AuthenticationError("Invalid ID or password")

        # Verify password
        stored_password = manager_data['password']

        # Check if password is already hashed (starts with $2b$)
        if stored_password.startswith('$2b$'):
            # Already hashed, verify with bcrypt
            if not verify_password(password, stored_password):
                raise AuthenticationError("Invalid ID or password")
        else:
            # Plain text password (from seed data), check directly
            if password != stored_password:
                raise AuthenticationError("Invalid ID or password")

            # TODO: Hash the password and update in database for future logins
            # This is a one-time migration for seed data

        return {
            'user_id': manager_data['id_number'],
            'user_type': 'manager',
            'first_name': manager_data['first_name_hebrew'],
            'last_name': manager_data['last_name_hebrew'],
            'is_registered': True
        }

    else:
        raise ValidationError("Invalid user type")


def get_user_info(user_id, user_type):
    """
    Get user information.

    Args:
        user_id (str): User ID (email or ID number)
        user_type (str): 'customer' or 'manager'

    Returns:
        dict: User information

    Raises:
        AuthenticationError: If user not found
    """
    if user_type == 'customer':
        user_data = execute_query(GET_CUSTOMER_INFO, (user_id,), fetch_one=True)

        if not user_data:
            raise AuthenticationError("User not found")

        result = {
            'email': user_data['email'],
            'first_name': user_data['first_name_english'],
            'last_name': user_data['last_name_english'],
            'user_type': 'customer'
        }

        # Add registered customer fields if available
        if user_data['balance'] is not None:
            result['is_registered'] = True
            result['balance'] = float(user_data['balance'])
            if user_data['birth_date']:
                result['birth_date'] = str(user_data['birth_date'])
            if user_data['passport_number']:
                result['passport_number'] = user_data['passport_number']
        else:
            result['is_registered'] = False

        return result

    elif user_type == 'manager':
        manager_data = execute_query(GET_MANAGER, (user_id,), fetch_one=True)

        if not manager_data:
            raise AuthenticationError("Manager not found")

        return {
            'id_number': manager_data['id_number'],
            'first_name': manager_data['first_name_hebrew'],
            'last_name': manager_data['last_name_hebrew'],
            'user_type': 'manager'
        }

    else:
        raise ValidationError("Invalid user type")
