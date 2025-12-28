"""
Order routes for FLYTAU application.
Handles booking creation and order management.
"""

from flask import Blueprint, request, session, jsonify
from ..services.booking_service import create_booking
from ..services.order_service import get_user_orders, get_order_details, cancel_order
from ..middleware.auth import login_required, get_current_user
from ..middleware.error_handlers import APIError

bp = Blueprint('orders', __name__)


@bp.route('/bookings', methods=['POST'])
@login_required
def create_booking_route():
    """
    Create a new booking.

    Request Body:
        {
            "flight_id": 1,
            "tickets": [
                {
                    "class_type": "Business",
                    "seat_number": "1A",
                    "price": 1500.00
                }
            ]
        }

    Returns:
        201: Booking created successfully
        400: Validation error
        401: Authentication required
    """
    current_user = get_current_user()

    if current_user['user_type'] != 'customer':
        raise APIError("Only customers can create bookings", 403)

    data = request.get_json()

    if not data:
        raise APIError("Request body is required", 400)

    flight_id = data.get('flight_id')
    tickets = data.get('tickets', [])

    if not flight_id:
        raise APIError("flight_id is required", 400)

    if not tickets:
        raise APIError("At least one ticket is required", 400)

    # Validate ticket structure
    for ticket in tickets:
        if not all(k in ticket for k in ['class_type', 'seat_number', 'price']):
            raise APIError("Each ticket must have class_type, seat_number, and price", 400)

    # Create booking
    order = create_booking(
        customer_email=current_user['user_id'],
        flight_id=flight_id,
        tickets=tickets,
        user_type=current_user['user_type']
    )

    return jsonify({
        'success': True,
        'data': order,
        'message': "Booking created successfully"
    }), 201


@bp.route('/orders', methods=['GET'])
@login_required
def get_orders():
    """
    Get user's orders.

    Query Parameters:
        filter: 'future' or 'history' (optional)

    Returns:
        200: List of orders
        401: Authentication required
    """
    current_user = get_current_user()

    if current_user['user_type'] != 'customer':
        raise APIError("Only customers can view orders", 403)

    filter_type = request.args.get('filter')

    # Get orders
    orders = get_user_orders(current_user['user_id'], filter_type)

    # Convert to dict
    orders_data = [order.to_dict() for order in orders]

    return jsonify({
        'success': True,
        'data': {'orders': orders_data},
        'message': f"Found {len(orders_data)} order(s)"
    }), 200


@bp.route('/orders/<int:order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    """
    Get specific order details.

    Path Parameters:
        order_id: Order ID

    Returns:
        200: Order details
        401: Authentication required
        403: Not authorized to view this order
        404: Order not found
    """
    current_user = get_current_user()

    # Managers can view any order, customers can only view their own
    customer_email = None if current_user['user_type'] == 'manager' else current_user['user_id']

    # Get order details
    order = get_order_details(order_id, customer_email)

    return jsonify({
        'success': True,
        'data': order.to_dict()
    }), 200


@bp.route('/orders/<int:order_id>', methods=['DELETE'])
@login_required
def cancel_order_route(order_id):
    """
    Cancel an order.

    Path Parameters:
        order_id: Order ID

    Returns:
        200: Order canceled successfully
        401: Authentication required
        403: Not authorized to cancel this order
        404: Order not found
        400: Cannot cancel order
    """
    current_user = get_current_user()

    if current_user['user_type'] != 'customer':
        raise APIError("Only customers can cancel orders", 403)

    # Cancel order
    result = cancel_order(order_id, current_user['user_id'])

    return jsonify({
        'success': True,
        'data': result,
        'message': "Order canceled successfully"
    }), 200
