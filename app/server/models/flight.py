"""
Flight data models for FLYTAU application.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Flight:
    """Basic flight information."""
    flight_id: int
    origin_airport: str
    destination_airport: str
    departure_datetime: str
    status: str
    plane_id: int
    manufacturer: str
    size_category: str
    flight_duration: float

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'flight_id': self.flight_id,
            'origin_airport': self.origin_airport,
            'destination_airport': self.destination_airport,
            'departure_datetime': str(self.departure_datetime),
            'status': self.status,
            'plane_id': self.plane_id,
            'manufacturer': self.manufacturer,
            'size_category': self.size_category,
            'flight_duration': float(self.flight_duration)
        }


@dataclass
class FlightDetails(Flight):
    """Detailed flight information with seat availability."""
    available_seats: Optional[Dict[str, int]] = None
    seat_map: Optional[Dict[str, Dict]] = None

    def to_dict(self):
        """Convert to dictionary."""
        data = super().to_dict()
        if self.available_seats:
            data['available_seats'] = self.available_seats
        if self.seat_map:
            data['seat_map'] = self.seat_map
        return data
