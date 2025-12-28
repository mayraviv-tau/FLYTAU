"""
Booking service for FLYTAU application.
Handles ticket booking and flight status updates.
"""

from datetime import datetime, timedelta
from ..db import execute_query, execute_transaction
from ..db.queries import *
from ..middleware.error_handlers import APIError
from ..services.flight_service import check_seat_availability, get_available_seats


def update_completed_flights():
    """
    Update flights to 'Landed' status if they have passed their landing time.
    Landing time = departure_datetime + flight_duration.

    This function should be called periodically (e.g., via a cron job or scheduler).
    """
    # Get all Active or Full flights with their duration
    query = """
        SELECT f.flight_id, f.departure_datetime, fl.flight_duration, f.status
        FROM Flight f
        JOIN FlightLine fl ON f.origin_airport = fl.origin_airport
                           AND f.destination_airport = fl.destination_airport
        WHERE f.status IN ('Active', 'Full')
    """

    flights = execute_query(query, fetch_all=True)
    updated_count = 0

    for flight in flights:
        departure = flight['departure_datetime']
        if isinstance(departure, str):
            departure = datetime.strptime(departure, '%Y-%m-%d %H:%M:%S')

        duration_hours = float(flight['flight_duration'])
        landing_time = departure + timedelta(hours=duration_hours)

        # If current time is past landing time, mark as Landed
        if datetime.now() >= landing_time:
            execute_query(UPDATE_FLIGHT_STATUS, ('Landed', flight['flight_id']), commit=True)
            updated_count += 1

    return updated_count


def create_booking(customer_email, flight_id, tickets, user_type='customer'):
    """
    Create a new booking with tickets.

    Args:
        customer_email (str): Customer email
        flight_id (int): Flight ID
        tickets (list): List of ticket dicts with class_type, seat_number, price
        user_type (str): Type of user ('customer', 'manager') - managers cannot purchase

    Returns:
        dict: Created order information

    Raises:
        APIError: If validation fails or flight not found
    """
    # Managers cannot purchase tickets
    if user_type == 'manager':
        raise APIError("Managers are not authorized to purchase tickets", 403)

    # Get flight details
    flight = execute_query(GET_FLIGHT, (flight_id,), fetch_one=True)

    if not flight:
        raise APIError(f"Flight {flight_id} not found", 404)

    # Check flight status
    if flight['status'] not in ('Active', 'Full'):
        raise APIError(f"Flight is {flight['status']}. Booking not allowed.", 400)

    # Check if flight has departed
    departure_time = flight['departure_datetime']
    if isinstance(departure_time, str):
        departure_time = datetime.strptime(departure_time, '%Y-%m-%d %H:%M:%S')

    if departure_time <= datetime.now():
        raise APIError("Flight has already departed", 400)

    # Validate tickets
    if not tickets or len(tickets) == 0:
        raise APIError("At least one ticket is required", 400)

    # Check seat availability
    seats_to_check = [
        {'class_type': ticket['class_type'], 'seat_number': ticket['seat_number']}
        for ticket in tickets
    ]

    all_available, unavailable_seats = check_seat_availability(
        flight_id,
        flight['plane_id'],
        seats_to_check
    )

    if not all_available:
        raise APIError(f"Seats not available: {', '.join(unavailable_seats)}", 400)

    # Calculate total payment
    total_payment = sum(ticket['price'] for ticket in tickets)

    # Check if customer is registered and has sufficient balance
    customer_data = execute_query(GET_CUSTOMER_INFO, (customer_email,), fetch_one=True)

    if customer_data and customer_data['balance'] is not None:
        # Registered customer - check balance
        balance = float(customer_data['balance'])
        if balance < total_payment:
            raise APIError(f"Insufficient balance. Required: ${total_payment:.2f}, Available: ${balance:.2f}", 400)

    # Prepare transaction operations
    operations = []

    # 1. Insert flight order
    order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    operations.append((
        INSERT_FLIGHT_ORDER,
        (customer_email, flight_id, order_date, total_payment)
    ))

    # Execute order insertion first to get order_id
    order_id_list = execute_transaction([operations[0]])
    order_id = order_id_list[0]

    # 2. Insert tickets
    ticket_ops = []
    for ticket in tickets:
        ticket_ops.append((
            INSERT_TICKET,
            (order_id, flight['plane_id'], ticket['class_type'], ticket['seat_number'], ticket['price'])
        ))

    # 3. Deduct from customer balance if registered
    if customer_data and customer_data['balance'] is not None:
        ticket_ops.append((
            DEDUCT_CUSTOMER_BALANCE,
            (total_payment, customer_email, total_payment)
        ))

    # Execute ticket insertions and balance deduction
    if ticket_ops:
        execute_transaction(ticket_ops)

    # 4. Check if flight should be marked as Full
    available_seats = get_available_seats(flight_id, flight['plane_id'])
    total_available = sum(available_seats.values())

    if total_available == 0 and flight['status'] == 'Active':
        execute_query(UPDATE_FLIGHT_STATUS, ('Full', flight_id), commit=True)

    # Get created order details
    order = execute_query(GET_ORDER_DETAILS, (order_id,), fetch_one=True)
    order_tickets = execute_query(GET_ORDER_TICKETS, (order_id,), fetch_all=True)

    return {
        'order_id': order['order_id'],
        'customer_email': order['customer_email'],
        'flight_id': order['flight_id'],
        'order_date': str(order['order_date']),
        'order_status': order['order_status'],
        'total_payment': float(order['total_payment']),
        'flight': {
            'origin_airport': order['origin_airport'],
            'destination_airport': order['destination_airport'],
            'departure_datetime': str(order['departure_datetime'])
        },
        'tickets': [
            {
                'class_type': ticket['class_type'],
                'seat_number': ticket['seat_number'],
                'price': float(ticket['price'])
            }
            for ticket in order_tickets
        ]
    }
