"""
Flight routes for FLYTAU application.
Handles flight search and details.
"""

from flask import Blueprint, request, jsonify
from ..services.flight_service import search_flights, get_flight_details

bp = Blueprint('flights', __name__)


@bp.route('/flights', methods=['GET'])
def get_flights():
    """
    Search for available flights.

    Query Parameters:
        date: YYYY-MM-DD (optional) - Filter by departure date
        origin: Airport code (optional) - Filter by origin
        destination: Airport code (optional) - Filter by destination

    Returns:
        200: List of flights
    """
    # Get query parameters
    date_filter = request.args.get('date')
    origin = request.args.get('origin')
    destination = request.args.get('destination')

    # Search flights
    flights = search_flights(date_filter, origin, destination)

    # Convert to dict
    flights_data = [flight.to_dict() for flight in flights]

    return jsonify({
        'success': True,
        'data': {'flights': flights_data},
        'message': f"Found {len(flights_data)} flight(s)"
    }), 200


@bp.route('/flights/<int:flight_id>', methods=['GET'])
def get_flight(flight_id):
    """
    Get detailed flight information including seat map.

    Path Parameters:
        flight_id: Flight ID

    Returns:
        200: Flight details with seat map
        404: Flight not found
    """
    # Get flight details
    flight = get_flight_details(flight_id)

    return jsonify({
        'success': True,
        'data': flight.to_dict()
    }), 200
