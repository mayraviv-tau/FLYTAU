"""
Order service for FLYTAU application.
Handles order retrieval and cancellation.
"""

from datetime import datetime
from ..db import execute_query, execute_transaction
from ..db.queries import *
from ..middleware.error_handlers import APIError
from ..models.order import Order, Ticket
from ..services.flight_service import get_available_seats


def get_user_orders(customer_email, filter_type=None):
    """
    Get orders for a customer.

    Args:
        customer_email (str): Customer email
        filter_type (str): Optional filter ('future' or 'history')

    Returns:
        list: List of Order objects
    """
    query = GET_USER_ORDERS
    params = [customer_email]

    # Add filter for future flights - insert before ORDER BY
    if filter_type == 'future':
        # Remove the ORDER BY clause temporarily
        query = query.replace("ORDER BY fo.order_date DESC", "")
        query += " AND f.departure_datetime > NOW()"
        query += " ORDER BY fo.order_date DESC"
    elif filter_type == 'history':
        # Remove the ORDER BY clause temporarily
        query = query.replace("ORDER BY fo.order_date DESC", "")
        query += " AND f.departure_datetime <= NOW()"
        query += " ORDER BY fo.order_date DESC"

    # Execute query
    results = execute_query(query, tuple(params), fetch_all=True)

    if not results:
        return []

    # Convert to Order objects
    orders = []
    for row in results:
        # Get tickets for this order
        tickets_data = execute_query(GET_ORDER_TICKETS, (row['order_id'],), fetch_all=True)

        tickets = [
            Ticket(
                class_type=t['class_type'],
                seat_number=t['seat_number'],
                price=float(t['price'])
            )
            for t in tickets_data
        ]

        order = Order(
            order_id=row['order_id'],
            customer_email=row['customer_email'],
            flight_id=row['flight_id'],
            order_date=str(row['order_date']),
            order_status=row['order_status'],
            total_payment=float(row['total_payment']),
            origin_airport=row['origin_airport'],
            destination_airport=row['destination_airport'],
            departure_datetime=str(row['departure_datetime']),
            flight_status=row['flight_status'],
            tickets=tickets
        )

        orders.append(order)

    return orders


def get_order_details(order_id, customer_email=None):
    """
    Get detailed information for a specific order.

    Args:
        order_id (int): Order ID
        customer_email (str): Optional customer email for ownership check

    Returns:
        Order: Order object

    Raises:
        APIError: If order not found or customer doesn't own the order
    """
    # Get order
    order_data = execute_query(GET_ORDER_DETAILS, (order_id,), fetch_one=True)

    if not order_data:
        raise APIError(f"Order {order_id} not found", 404)

    # Check ownership if customer_email provided
    if customer_email and order_data['customer_email'] != customer_email:
        raise APIError("You don't have permission to view this order", 403)

    # Get tickets
    tickets_data = execute_query(GET_ORDER_TICKETS, (order_id,), fetch_all=True)

    tickets = [
        Ticket(
            class_type=t['class_type'],
            seat_number=t['seat_number'],
            price=float(t['price'])
        )
        for t in tickets_data
    ]

    order = Order(
        order_id=order_data['order_id'],
        customer_email=order_data['customer_email'],
        flight_id=order_data['flight_id'],
        order_date=str(order_data['order_date']),
        order_status=order_data['order_status'],
        total_payment=float(order_data['total_payment']),
        origin_airport=order_data['origin_airport'],
        destination_airport=order_data['destination_airport'],
        departure_datetime=str(order_data['departure_datetime']),
        flight_status=order_data['flight_status'],
        tickets=tickets
    )

    return order


def cancel_order(order_id, customer_email):
    """
    Cancel an order and process refund.

    Args:
        order_id (int): Order ID
        customer_email (str): Customer email

    Returns:
        dict: Cancellation result with refund information

    Raises:
        APIError: If order not found, customer doesn't own the order, or order cannot be canceled
    """
    # Get order
    order_data = execute_query(GET_ORDER_DETAILS, (order_id,), fetch_one=True)

    if not order_data:
        raise APIError(f"Order {order_id} not found", 404)

    # Check ownership
    if order_data['customer_email'] != customer_email:
        raise APIError("You don't have permission to cancel this order", 403)

    # Check if order is Active
    if order_data['order_status'] != 'Active':
        raise APIError(f"Order is {order_data['order_status']}. Cannot cancel.", 400)

    # Check if flight has departed
    departure_time = order_data['departure_datetime']
    if isinstance(departure_time, str):
        departure_time = datetime.strptime(departure_time, '%Y-%m-%d %H:%M:%S')

    if departure_time <= datetime.now():
        raise APIError("Cannot cancel order. Flight has already departed.", 400)

    # Calculate refund (95% refund, 5% cancellation fee)
    original_payment = float(order_data['total_payment'])
    cancellation_fee = original_payment * 0.05
    refund_amount = original_payment * 0.95

    # Prepare transaction operations
    operations = []

    # 1. Update order status and payment (keep 5% as cancellation fee)
    operations.append((
        UPDATE_ORDER_CANCELLATION,
        ('Canceled_By_Client', cancellation_fee, order_id)
    ))

    # 2. Refund 95% to customer balance if registered
    customer_data = execute_query(GET_CUSTOMER_INFO, (customer_email,), fetch_one=True)

    if customer_data and customer_data['balance'] is not None:
        # Registered customer - process refund
        operations.append((
            UPDATE_CUSTOMER_BALANCE,
            (refund_amount, customer_email)
        ))

    # Execute transaction
    execute_transaction(operations)

    # 3. Update flight status from Full to Active if needed
    if order_data['flight_status'] == 'Full':
        # Check if there are now available seats
        available_seats = get_available_seats(
            order_data['flight_id'],
            order_data['plane_id']
        )
        total_available = sum(available_seats.values())

        if total_available > 0:
            execute_query(
                UPDATE_FLIGHT_STATUS,
                ('Active', order_data['flight_id']),
                commit=True
            )

    return {
        'order_id': order_id,
        'status': 'Canceled_By_Client',
        'original_payment': original_payment,
        'cancellation_fee': cancellation_fee,
        'refund_amount': refund_amount,
        'refunded_to_balance': customer_data and customer_data['balance'] is not None
    }
