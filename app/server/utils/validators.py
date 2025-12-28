"""
Input validation utilities for FLYTAU application.
Simplified for academic exercise.
"""


def validate_email(email):
    """
    Validate email format (simplified).

    Args:
        email (str): Email address

    Returns:
        bool: True if valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False

    # Simple check: must contain @ and . after @
    if '@' not in email:
        return False

    parts = email.split('@')
    if len(parts) != 2:
        return False

    return '.' in parts[1]


def validate_password(password):
    """
    Validate password (simplified).
    Minimum 4 characters for academic demo.

    Args:
        password (str): Password

    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if not password or not isinstance(password, str):
        return False, "Password is required"

    if len(password) < 4:
        return False, "Password must be at least 4 characters long"

    return True, ""


def validate_airport_code(code):
    """
    Validate airport code (simplified).
    Just check length is 3.

    Args:
        code (str): Airport code

    Returns:
        bool: True if valid, False otherwise
    """
    if not code or not isinstance(code, str):
        return False

    return len(code.strip()) == 3


def validate_seat_number(seat):
    """
    Validate seat number format (simplified).
    Just check it has letters and numbers.

    Args:
        seat (str): Seat number

    Returns:
        bool: True if valid, False otherwise
    """
    if not seat or not isinstance(seat, str):
        return False

    # Simple check: has both letters and digits
    seat = seat.strip().upper()
    has_digit = any(c.isdigit() for c in seat)
    has_letter = any(c.isalpha() for c in seat)

    return has_digit and has_letter and 2 <= len(seat) <= 4
