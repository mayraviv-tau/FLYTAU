"""Service layer for FLYTAU application."""

from .auth_service import register_customer, login_user, get_user_info
from .flight_service import search_flights, get_flight_details, get_available_seats
from .booking_service import create_booking
from .order_service import get_user_orders, get_order_details, cancel_order
from .report_service import execute_sql_report, get_all_reports

__all__ = [
    'register_customer',
    'login_user',
    'get_user_info',
    'search_flights',
    'get_flight_details',
    'get_available_seats',
    'create_booking',
    'get_user_orders',
    'get_order_details',
    'cancel_order',
    'execute_sql_report',
    'get_all_reports'
]
