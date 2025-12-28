"""
Order data models for FLYTAU application.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Ticket:
    """Ticket information."""
    class_type: str
    seat_number: str
    price: float

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'class_type': self.class_type,
            'seat_number': self.seat_number,
            'price': float(self.price)
        }


@dataclass
class Order:
    """Order information."""
    order_id: int
    customer_email: str
    flight_id: int
    order_date: str
    order_status: str
    total_payment: float
    origin_airport: str
    destination_airport: str
    departure_datetime: str
    flight_status: str
    tickets: Optional[List[Ticket]] = None

    def to_dict(self):
        """Convert to dictionary."""
        data = {
            'order_id': self.order_id,
            'customer_email': self.customer_email,
            'flight_id': self.flight_id,
            'order_date': str(self.order_date),
            'order_status': self.order_status,
            'total_payment': float(self.total_payment),
            'flight': {
                'origin_airport': self.origin_airport,
                'destination_airport': self.destination_airport,
                'departure_datetime': str(self.departure_datetime),
                'status': self.flight_status
            }
        }

        if self.tickets:
            data['tickets'] = [ticket.to_dict() for ticket in self.tickets]

        return data
