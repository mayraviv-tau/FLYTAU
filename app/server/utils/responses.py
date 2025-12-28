"""
Standard JSON response formatting utilities.
"""

from flask import jsonify


def success_response(data=None, message="Success", status_code=200):
    """
    Create a success response.

    Args:
        data: Response data (dict, list, etc.)
        message (str): Success message
        status_code (int): HTTP status code

    Returns:
        Flask response with JSON
    """
    response = {
        'success': True,
        'message': message
    }

    if data is not None:
        response['data'] = data

    return jsonify(response), status_code


def error_response(message, error_type="Error", status_code=400):
    """
    Create an error response.

    Args:
        message (str): Error message
        error_type (str): Error type/name
        status_code (int): HTTP status code

    Returns:
        Flask response with JSON
    """
    response = {
        'success': False,
        'error': error_type,
        'message': message
    }

    return jsonify(response), status_code
