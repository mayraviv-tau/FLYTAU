"""
Authentication routes for FLYTAU application.
Handles registration, login, logout, and user info.
"""

from flask import Blueprint, request, session
from ..services.auth_service import register_customer, login_user, get_user_info
from ..middleware.auth import login_required, get_current_user
from ..middleware.error_handlers import ValidationError
from ..utils.responses import success_response, error_response

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new customer.

    Request Body:
        {
            "email": "user@example.com",
            "password": "password123",
            "first_name": "John",
            "last_name": "Doe",
            "birth_date": "1990-01-15",
            "passport_number": "A12345678",
            "phone_numbers": ["050-1234567"]  // optional
        }

    Returns:
        201: Customer registered successfully
        400: Validation error
    """
    data = request.get_json()

    if not data:
        raise ValidationError("Request body is required")

    # Extract required fields
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    birth_date = data.get('birth_date')
    passport_number = data.get('passport_number')
    phone_numbers = data.get('phone_numbers', [])

    # Validate required fields
    if not all([email, password, first_name, last_name, birth_date, passport_number]):
        raise ValidationError("Missing required fields: email, password, first_name, last_name, birth_date, passport_number")

    # Register customer
    customer = register_customer(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        birth_date=birth_date,
        passport_number=passport_number,
        phone_numbers=phone_numbers
    )

    # Create session
    session['user_id'] = customer.email
    session['user_type'] = 'customer'
    session['first_name'] = customer.first_name
    session['last_name'] = customer.last_name
    session['is_registered'] = True

    return success_response(
        data=customer.to_dict(),
        message="Customer registered successfully",
        status_code=201
    )


@bp.route('/login', methods=['POST'])
def login():
    """
    Login a user (customer or manager).

    Request Body:
        {
            "email": "user@example.com",  // or id_number for manager
            "password": "password123",
            "user_type": "customer"  // or "manager"
        }

    Returns:
        200: Login successful
        401: Authentication failed
    """
    data = request.get_json()

    if not data:
        raise ValidationError("Request body is required")

    email_or_id = data.get('email') or data.get('id_number')
    password = data.get('password')
    user_type = data.get('user_type', 'customer')

    if not all([email_or_id, password]):
        raise ValidationError("Email/ID and password are required")

    # Authenticate user
    user_data = login_user(email_or_id, password, user_type)

    # Create session
    session['user_id'] = user_data['user_id']
    session['user_type'] = user_data['user_type']
    session['first_name'] = user_data['first_name']
    session['last_name'] = user_data['last_name']
    session['is_registered'] = user_data.get('is_registered', True)

    return success_response(
        data=user_data,
        message="Login successful"
    )


@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    Logout current user.

    Returns:
        200: Logout successful
    """
    session.clear()

    return success_response(message="Logout successful")


@bp.route('/me', methods=['GET'])
@login_required
def get_current_user_info():
    """
    Get current user information.

    Returns:
        200: User information
        401: Not authenticated
    """
    current_user = get_current_user()

    if not current_user:
        return error_response("Not authenticated", "AuthenticationError", 401)

    # Get full user info from database
    user_info = get_user_info(current_user['user_id'], current_user['user_type'])

    return success_response(data=user_info)
