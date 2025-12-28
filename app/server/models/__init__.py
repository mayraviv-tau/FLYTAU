"""Data models for FLYTAU application."""

from .user import User, RegisteredCustomer, Manager
from .flight import Flight, FlightDetails
from .order import Order, Ticket

__all__ = [
    'User',
    'RegisteredCustomer',
    'Manager',
    'Flight',
    'FlightDetails',
    'Order',
    'Ticket'
]
