"""
Password hashing and verification utilities using bcrypt.
"""

import bcrypt


def hash_password(password):
    """
    Hash a password using bcrypt.

    Args:
        password (str): Plain text password

    Returns:
        str: Hashed password
    """
    # Generate salt and hash password
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password, hashed):
    """
    Verify a password against a hash.

    Args:
        password (str): Plain text password
        hashed (str): Hashed password

    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False
