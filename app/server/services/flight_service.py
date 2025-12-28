"""
Flight service for FLYTAU application.
Handles flight search and seat availability.
"""

from datetime import datetime
from ..db import execute_query
from ..db.queries import *
from ..middleware.error_handlers import APIError
from ..models.flight import Flight, FlightDetails


def search_flights(date_filter=None, origin=None, destination=None):
    """
    Search for available flights.

    Args:
        date_filter (str): Optional date filter (YYYY-MM-DD)
        origin (str): Optional origin airport code
        destination (str): Optional destination airport code

    Returns:
        list: List of Flight objects
    """
    query = SEARCH_FLIGHTS
    params = []
    conditions = []

    # Add date filter (flights from this date onwards)
    if date_filter:
        conditions.append("DATE(f.departure_datetime) >= %s")
        params.append(date_filter)

    # Add origin filter
    if origin:
        conditions.append("f.origin_airport = %s")
        params.append(origin.upper())

    # Add destination filter
    if destination:
        conditions.append("f.destination_airport = %s")
        params.append(destination.upper())

    # Append conditions to query
    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += " ORDER BY f.departure_datetime ASC"

    # Execute query
    results = execute_query(query, tuple(params), fetch_all=True)

    if not results:
        return []

    # Calculate available seats for each flight
    flights = []
    for row in results:
        flight = Flight(
            flight_id=row['flight_id'],
            origin_airport=row['origin_airport'],
            destination_airport=row['destination_airport'],
            departure_datetime=str(row['departure_datetime']),
            status=row['status'],
            plane_id=row['plane_id'],
            manufacturer=row['manufacturer'],
            size_category=row['size_category'],
            flight_duration=float(row['flight_duration'])
        )

        # Get available seats
        available_seats = get_available_seats(flight.flight_id, flight.plane_id)

        # Create flight details with seat info
        flight_details = FlightDetails(
            flight_id=flight.flight_id,
            origin_airport=flight.origin_airport,
            destination_airport=flight.destination_airport,
            departure_datetime=flight.departure_datetime,
            status=flight.status,
            plane_id=flight.plane_id,
            manufacturer=flight.manufacturer,
            size_category=flight.size_category,
            flight_duration=flight.flight_duration,
            available_seats=available_seats
        )

        flights.append(flight_details)

    return flights


def get_flight_details(flight_id):
    """
    Get detailed flight information including seat map.

    Args:
        flight_id (int): Flight ID

    Returns:
        FlightDetails: Flight details with seat map

    Raises:
        APIError: If flight not found
    """
    # Get flight info
    flight_data = execute_query(GET_FLIGHT, (flight_id,), fetch_one=True)

    if not flight_data:
        raise APIError(f"Flight {flight_id} not found", 404)

    # Create flight object
    flight = Flight(
        flight_id=flight_data['flight_id'],
        origin_airport=flight_data['origin_airport'],
        destination_airport=flight_data['destination_airport'],
        departure_datetime=str(flight_data['departure_datetime']),
        status=flight_data['status'],
        plane_id=flight_data['plane_id'],
        manufacturer=flight_data['manufacturer'],
        size_category=flight_data['size_category'],
        flight_duration=float(flight_data['flight_duration'])
    )

    # Get seat map
    seat_map = get_seat_map(flight.flight_id, flight.plane_id)

    # Create flight details
    flight_details = FlightDetails(
        flight_id=flight.flight_id,
        origin_airport=flight.origin_airport,
        destination_airport=flight.destination_airport,
        departure_datetime=flight.departure_datetime,
        status=flight.status,
        plane_id=flight.plane_id,
        manufacturer=flight.manufacturer,
        size_category=flight.size_category,
        flight_duration=flight.flight_duration,
        seat_map=seat_map
    )

    return flight_details


def get_available_seats(flight_id, plane_id):
    """
    Calculate available seats per class for a flight.

    Args:
        flight_id (int): Flight ID
        plane_id (int): Plane ID

    Returns:
        dict: Available seats per class
    """
    # Get plane classes and capacity
    classes = execute_query(GET_PLANE_CLASSES, (plane_id,), fetch_all=True)

    if not classes:
        return {}

    # Get occupied seats
    occupied = execute_query(GET_OCCUPIED_SEATS, (flight_id,), fetch_all=True)

    # Count occupied seats per class
    occupied_count = {}
    for seat in occupied:
        class_type = seat['class_type']
        occupied_count[class_type] = occupied_count.get(class_type, 0) + 1

    # Calculate available seats
    available = {}
    for cls in classes:
        class_type = cls['class_type']
        total = cls['total_seats']
        occupied = occupied_count.get(class_type, 0)
        available[class_type] = total - occupied

    return available


def get_seat_map(flight_id, plane_id):
    """
    Get detailed seat map showing available and occupied seats.

    Args:
        flight_id (int): Flight ID
        plane_id (int): Plane ID

    Returns:
        dict: Seat map per class with available and occupied seats
    """
    # Get all seats for the plane
    all_seats = execute_query(GET_PLANE_SEATS, (plane_id,), fetch_all=True)

    # Get occupied seats
    occupied_seats = execute_query(GET_OCCUPIED_SEATS, (flight_id,), fetch_all=True)

    # Create set of occupied seat keys
    occupied_set = set()
    for seat in occupied_seats:
        key = f"{seat['class_type']}:{seat['seat_number']}"
        occupied_set.add(key)

    # Build seat map
    seat_map = {}
    for seat in all_seats:
        class_type = seat['class_type']
        seat_number = seat['seat_number']

        if class_type not in seat_map:
            seat_map[class_type] = {
                'available': [],
                'occupied': []
            }

        key = f"{class_type}:{seat_number}"
        if key in occupied_set:
            seat_map[class_type]['occupied'].append(seat_number)
        else:
            seat_map[class_type]['available'].append(seat_number)

    # Add totals
    for class_type in seat_map:
        seat_map[class_type]['total'] = (
            len(seat_map[class_type]['available']) +
            len(seat_map[class_type]['occupied'])
        )

    return seat_map


def check_seat_availability(flight_id, plane_id, seats):
    """
    Check if specific seats are available for booking.

    Args:
        flight_id (int): Flight ID
        plane_id (int): Plane ID
        seats (list): List of dicts with class_type and seat_number

    Returns:
        tuple: (bool, list) - (all_available, unavailable_seats)
    """
    unavailable = []

    for seat in seats:
        class_type = seat['class_type']
        seat_number = seat['seat_number']

        # Check if seat is available
        result = execute_query(
            CHECK_SEAT_AVAILABLE,
            (plane_id, class_type, seat_number, plane_id, class_type, seat_number, flight_id),
            fetch_one=True
        )

        if not result:
            unavailable.append(f"{class_type} {seat_number}")

    return len(unavailable) == 0, unavailable
