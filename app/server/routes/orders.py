"""
Order routes for FLYTAU application.
Handles booking creation and order management.
"""

from flask import Blueprint, request, session
from ..services.booking_service import create_booking
from ..services.order_service import get_user_orders, get_order_details, cancel_order
from ..middleware.auth import login_required, get_current_user
from ..middleware.error_handlers import ValidationError, AuthorizationError
from ..utils.responses import success_response

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
        raise AuthorizationError("Only customers can create bookings")

    data = request.get_json()

    if not data:
        raise ValidationError("Request body is required")

    flight_id = data.get('flight_id')
    tickets = data.get('tickets', [])

    if not flight_id:
        raise ValidationError("flight_id is required")

    if not tickets:
        raise ValidationError("At least one ticket is required")

    # Validate ticket structure
    for ticket in tickets:
        if not all(k in ticket for k in ['class_type', 'seat_number', 'price']):
            raise ValidationError("Each ticket must have class_type, seat_number, and price")

    # Create booking
    order = create_booking(
        customer_email=current_user['user_id'],
        flight_id=flight_id,
        tickets=tickets
    )

    return success_response(
        data=order,
        message="Booking created successfully",
        status_code=201
    )


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
        raise AuthorizationError("Only customers can view orders")

    filter_type = request.args.get('filter')

    # Get orders
    orders = get_user_orders(current_user['user_id'], filter_type)

    # Convert to dict
    orders_data = [order.to_dict() for order in orders]

    return success_response(
        data={'orders': orders_data},
        message=f"Found {len(orders_data)} order(s)"
    )


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

    return success_response(data=order.to_dict())


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
        raise AuthorizationError("Only customers can cancel orders")

    # Cancel order
    result = cancel_order(order_id, current_user['user_id'])

    return success_response(
        data=result,
        message="Order canceled successfully"
    )
