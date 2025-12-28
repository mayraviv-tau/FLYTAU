"""Routes package for FLYTAU application."""

# Import blueprints to make them available
from . import auth, flights, orders, admin_flights, admin_reports

__all__ = ['auth', 'flights', 'orders', 'admin_flights', 'admin_reports']
