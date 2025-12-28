"""
Input validation utilities for FLYTAU application.
"""

import re
from datetime import datetime


def validate_email(email):
    """
    Validate email format.

    Args:
        email (str): Email address

    Returns:
        bool: True if valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False

    # Basic email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password):
    """
    Validate password strength.
    Minimum 8 characters.

    Args:
        password (str): Password

    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if not password or not isinstance(password, str):
        return False, "Password is required"

    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    return True, ""


def validate_date(date_string):
    """
    Validate date format (YYYY-MM-DD).

    Args:
        date_string (str): Date string

    Returns:
        tuple: (bool, datetime/None) - (is_valid, parsed_date)
    """
    if not date_string:
        return False, None

    try:
        parsed_date = datetime.strptime(date_string, '%Y-%m-%d')
        return True, parsed_date
    except ValueError:
        return False, None


def validate_datetime(datetime_string):
    """
    Validate datetime format (YYYY-MM-DD HH:MM:SS or ISO format).

    Args:
        datetime_string (str): Datetime string

    Returns:
        tuple: (bool, datetime/None) - (is_valid, parsed_datetime)
    """
    if not datetime_string:
        return False, None

    # Try multiple formats
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%dT%H:%M'
    ]

    for fmt in formats:
        try:
            parsed_dt = datetime.strptime(datetime_string, fmt)
            return True, parsed_dt
        except ValueError:
            continue

    return False, None


def validate_airport_code(code):
    """
    Validate airport code (3 uppercase letters).

    Args:
        code (str): Airport code

    Returns:
        bool: True if valid, False otherwise
    """
    if not code or not isinstance(code, str):
        return False

    # 3 uppercase letters
    pattern = r'^[A-Z]{3}$'
    return bool(re.match(pattern, code.upper()))


def validate_seat_number(seat):
    """
    Validate seat number format (e.g., 1A, 10B, 32F).

    Args:
        seat (str): Seat number

    Returns:
        bool: True if valid, False otherwise
    """
    if not seat or not isinstance(seat, str):
        return False

    # Row number (1-99) followed by seat letter (A-F typically)
    pattern = r'^[1-9][0-9]?[A-Z]$'
    return bool(re.match(pattern, seat.upper()))
