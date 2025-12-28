"""
Admin flight management routes for FLYTAU application.
Handles flight creation and cancellation (managers only).
"""

from flask import Blueprint, request, session, jsonify
from datetime import datetime, timedelta
from ..db import execute_query, execute_transaction
from ..db.queries import *
from ..middleware.auth import manager_required, get_current_user
from ..middleware.error_handlers import APIError

bp = Blueprint('admin_flights', __name__)


@bp.route('/flights', methods=['POST'])
@manager_required
def create_flight():
    """
    Create a new flight (managers only).

    Request Body:
        {
            "origin_airport": "TLV",
            "destination_airport": "JFK",
            "plane_id": 1,
            "departure_datetime": "2026-05-01T10:00:00",
            "pilot_ids": ["300000001", "300000002", "300000003"],
            "attendant_ids": ["400000001", "400000002", ...]
        }

    Returns:
        201: Flight created successfully
        400: Validation error
        401: Authentication required
        403: Manager access required
    """
    current_user = get_current_user()
    data = request.get_json()

    if not data:
        raise APIError("Request body is required", 400)

    # Extract fields
    origin_airport = data.get('origin_airport')
    destination_airport = data.get('destination_airport')
    plane_id = data.get('plane_id')
    departure_datetime = data.get('departure_datetime')
    pilot_ids = data.get('pilot_ids', [])
    attendant_ids = data.get('attendant_ids', [])

    # Validate required fields
    if not all([origin_airport, destination_airport, plane_id, departure_datetime]):
        raise APIError("Missing required fields: origin_airport, destination_airport, plane_id, departure_datetime", 400)

    # Validate flight line exists
    flight_line = execute_query(
        CHECK_FLIGHT_LINE,
        (origin_airport.upper(), destination_airport.upper()),
        fetch_one=True
    )

    if not flight_line:
        raise APIError(f"Flight route {origin_airport}-{destination_airport} does not exist", 400)

    flight_duration = float(flight_line['flight_duration'])

    # Validate plane exists
    plane = execute_query(CHECK_PLANE_EXISTS, (plane_id,), fetch_one=True)

    if not plane:
        raise APIError(f"Plane {plane_id} not found", 404)

    size_category = plane['size_category']

    # Determine crew requirements
    is_long_haul = flight_duration > 6.0

    if is_long_haul:
        required_pilots = 3
        required_attendants = 6
    else:
        if size_category == 'Large':
            required_pilots = 3
            required_attendants = 6
        else:  # Small
            required_pilots = 2
            required_attendants = 3

    # Validate crew count
    if len(pilot_ids) != required_pilots:
        raise APIError(f"Flight requires {required_pilots} pilots, got {len(pilot_ids)}", 400)

    if len(attendant_ids) != required_attendants:
        raise APIError(f"Flight requires {required_attendants} flight attendants, got {len(attendant_ids)}", 400)

    # Validate pilot qualifications
    for pilot_id in pilot_ids:
        pilot = execute_query(CHECK_PILOT_QUALIFICATION, (pilot_id,), fetch_one=True)

        if not pilot:
            raise APIError(f"Pilot {pilot_id} not found", 404)

        if is_long_haul and not pilot['is_long_haul_qualified']:
            raise APIError(f"Pilot {pilot_id} is not qualified for long-haul flights", 400)

    # Validate attendant qualifications
    for attendant_id in attendant_ids:
        attendant = execute_query(CHECK_ATTENDANT_QUALIFICATION, (attendant_id,), fetch_one=True)

        if not attendant:
            raise APIError(f"Flight attendant {attendant_id} not found", 404)

        if is_long_haul and not attendant['is_long_haul_qualified']:
            raise APIError(f"Flight attendant {attendant_id} is not qualified for long-haul flights", 400)

    # Check crew availability (no schedule conflicts)
    # Assume conflict window is departure_time ± flight_duration hours
    departure_dt = datetime.fromisoformat(departure_datetime.replace('T', ' '))
    window_start = departure_dt - timedelta(hours=flight_duration)
    window_end = departure_dt + timedelta(hours=flight_duration)

    for pilot_id in pilot_ids:
        conflicts = execute_query(
            CHECK_PILOT_AVAILABILITY,
            (pilot_id, window_start, window_end),
            fetch_all=True
        )

        if conflicts:
            raise APIError(f"Pilot {pilot_id} has schedule conflict with flight {conflicts[0]['flight_id']}", 400)

    for attendant_id in attendant_ids:
        conflicts = execute_query(
            CHECK_ATTENDANT_AVAILABILITY,
            (attendant_id, window_start, window_end),
            fetch_all=True
        )

        if conflicts:
            raise APIError(f"Flight attendant {attendant_id} has schedule conflict with flight {conflicts[0]['flight_id']}", 400)

    # Create flight with crew assignments (transaction)
    operations = []

    # 1. Insert flight
    operations.append((
        INSERT_FLIGHT,
        (origin_airport.upper(), destination_airport.upper(), plane_id, departure_datetime, current_user['user_id'])
    ))

    # Execute flight insertion to get flight_id
    flight_ids = execute_transaction([operations[0]])
    flight_id = flight_ids[0]

    # 2. Insert pilot assignments
    crew_ops = []
    for pilot_id in pilot_ids:
        crew_ops.append((INSERT_PILOT_ASSIGNMENT, (pilot_id, flight_id)))

    # 3. Insert attendant assignments
    for attendant_id in attendant_ids:
        crew_ops.append((INSERT_ATTENDANT_ASSIGNMENT, (attendant_id, flight_id)))

    # Execute crew assignments
    execute_transaction(crew_ops)

    # Get created flight details
    flight = execute_query(GET_FLIGHT, (flight_id,), fetch_one=True)

    return jsonify({
        'success': True,
        'data': {
            'flight_id': flight['flight_id'],
            'origin_airport': flight['origin_airport'],
            'destination_airport': flight['destination_airport'],
            'departure_datetime': str(flight['departure_datetime']),
            'plane_id': flight['plane_id'],
            'status': flight['status'],
            'pilots_assigned': len(pilot_ids),
            'attendants_assigned': len(attendant_ids)
        },
        'message': "Flight created successfully"
    }), 201


@bp.route('/flights/<int:flight_id>', methods=['DELETE'])
@manager_required
def cancel_flight(flight_id):
    """
    Cancel a flight (managers only).

    Path Parameters:
        flight_id: Flight ID

    Returns:
        200: Flight canceled successfully
        400: Cannot cancel flight
        401: Authentication required
        403: Manager access required
        404: Flight not found
    """
    # Get flight
    flight = execute_query(GET_FLIGHT, (flight_id,), fetch_one=True)

    if not flight:
        raise APIError(f"Flight {flight_id} not found", 404)

    # Check if flight can be canceled
    if flight['status'] == 'Landed':
        raise APIError("Cannot cancel a flight that has already landed", 400)

    if flight['status'] == 'Canceled':
        raise APIError("Flight is already canceled", 400)

    # Get all active orders for this flight
    active_orders = execute_query(GET_FLIGHT_ACTIVE_ORDERS, (flight_id,), fetch_all=True)

    # Prepare transaction operations
    operations = []

    # 1. Update flight status to Canceled
    operations.append((
        UPDATE_FLIGHT_STATUS,
        ('Canceled', flight_id)
    ))

    # 2. Cancel all active orders and process refunds
    for order in active_orders:
        # Update order to Canceled_By_Company with 0 payment (full refund)
        operations.append((
            UPDATE_ORDER_CANCELLATION,
            ('Canceled_By_Company', 0, order['order_id'])
        ))

        # Refund 100% to customer balance if registered
        customer_data = execute_query(GET_CUSTOMER_INFO, (order['customer_email'],), fetch_one=True)

        if customer_data and customer_data['balance'] is not None:
            # Registered customer - full refund
            refund_amount = float(order['total_payment'])
            operations.append((
                UPDATE_CUSTOMER_BALANCE,
                (refund_amount, order['customer_email'])
            ))

    # Execute transaction
    execute_transaction(operations)

    return jsonify({
        'success': True,
        'data': {
            'flight_id': flight_id,
            'status': 'Canceled',
            'orders_canceled': len(active_orders),
            'total_refunded': sum(float(order['total_payment']) for order in active_orders)
        },
        'message': "Flight canceled successfully"
    }), 200
