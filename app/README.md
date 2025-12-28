# FLYTAU Flask Server

REST API server for the FLYTAU flight booking system. This is an academic exercise implementing a flight booking management system.

## Overview

This server implements a complete REST API for managing flights, bookings, orders, and administrative reports. It has been simplified for academic purposes with plain text password storage and straightforward error handling.

## Quick Start

### 1. Install Dependencies

```bash
cd /path/to/Project
pip install -r requirements.txt
```

### 2. Configure Database

Create a `.env` file in the project root (use `.env.example` as template):

```bash
DB_HOST=localhost
DB_PORT=3306
DB_NAME=flytau
DB_USER=root
DB_PASSWORD=your_password

SECRET_KEY=your_secret_key_here
FLASK_ENV=development
FLASK_DEBUG=True
SESSION_TYPE=filesystem
```

### 3. Set Up Database

```bash
mysql -u root -p < db/schema.sql
mysql -u root -p flytau < db/seed.sql
```

### 4. Run Server

```bash
cd app/server
python main.py
```

Server will start at `http://localhost:5001` (Note: Port 5000 may conflict with AirPlay on macOS)

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register customer
- `POST /api/auth/login` - Login (customer/manager)
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

### Flights
- `GET /api/flights` - Search flights
- `GET /api/flights/{id}` - Get flight details

### Bookings & Orders
- `POST /api/bookings` - Create booking
- `GET /api/orders` - Get user orders
- `GET /api/orders/{id}` - Get order details
- `DELETE /api/orders/{id}` - Cancel order

### Admin - Flight Management
- `POST /api/admin/flights` - Create flight
- `DELETE /api/admin/flights/{id}` - Cancel flight

### Admin - Reports
- `GET /api/admin/reports/occupancy` - Occupancy report
- `GET /api/admin/reports/revenue` - Revenue report
- `GET /api/admin/reports/staff-hours` - Staff hours report
- `GET /api/admin/reports/cancellations` - Cancellations report
- `GET /api/admin/reports/plane-activity` - Plane activity report

## Testing

```bash
# From project root
pytest

# With coverage
pytest --cov=app/server
```

## Documentation

- [API Documentation](../docs/API_DOCUMENTATION.md)
- [Setup Guide](../docs/SETUP.md)
- [Architecture](../docs/ARCHITECTURE.md)
- [Implementation Plan](../docs/IMPLEMENTATION_PLAN.md)

## Project Structure

```
server/
├── __init__.py              # Flask app factory
├── config.py                # Configuration
├── main.py                  # Entry point
├── db/                      # Database layer
├── models/                  # Data models
├── routes/                  # API endpoints
├── middleware/              # Auth & error handling
├── services/                # Business logic
├── utils/                   # Utilities
└── tests/                   # Test suite
```

## Features

- Session-based authentication with Flask-Session
- Customer registration and login
- Manager authentication with role-based access control
- Flight search with date, origin, and destination filters
- Real-time seat availability checking
- Booking creation with automatic balance deduction
- Order management and cancellation with refund processing
- Administrative flight creation and cancellation
- Five comprehensive administrative reports
- Database transaction safety for critical operations
- Input validation and error handling
- Test suite for all endpoints

## Technology Stack

- Flask 3.1.0
- MySQL 8.0+
- mysql-connector-python 9.4.0
- pytest and pytest-flask for testing
- Flask-Session 0.8.0 for session management
- Python 3.10+

## Academic Simplifications

This implementation has been simplified for academic purposes:

- **Plain text passwords**: Passwords are stored in plain text for easier testing and grading. NOT suitable for production use.
- **Simplified validation**: Basic email and password validation instead of complex regex patterns.
- **Unified error handling**: Single APIError exception class with status codes instead of multiple error types.
- **Direct JSON responses**: Uses Flask's jsonify() directly without wrapper functions.

These simplifications maintain all required functionality while making the code easier to understand and grade.

## Sample Credentials

**Managers (from seed data):**
- ID: 100000001, Password: pass123
- ID: 100000002, Password: pass456

**Test Customer:**
- Email: testuser@example.com, Password: test123 (created during testing)
