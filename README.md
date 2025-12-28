# FLYTAU Flight Booking System

Academic project implementing a complete flight booking management system with REST API backend.

## Project Overview

FLYTAU is a flight booking system that manages flights, customer bookings, and administrative operations. The system includes:

- Customer registration and authentication
- Flight search and booking
- Order management with cancellation and refunds
- Administrative flight creation and management
- Comprehensive reporting for business analytics

## Project Structure

```
Project/
├── db/                          # Database layer
│   ├── schema.sql              # Database schema (15 tables)
│   ├── seed.sql                # Sample data
│   └── reports_sql/            # SQL queries for 5 reports
├── app/
│   └── server/                 # Flask REST API
│       ├── routes/             # API endpoints
│       ├── services/           # Business logic
│       ├── models/             # Data models
│       ├── middleware/         # Authentication & error handling
│       ├── db/                 # Database connection & queries
│       ├── utils/              # Validation utilities
│       └── tests/              # Test suite
├── docs/                       # Documentation
│   ├── exercise2.txt          # Project requirements
│   ├── API_DOCUMENTATION.md   # API reference
│   ├── SETUP.md               # Setup instructions
│   └── ARCHITECTURE.md        # System architecture
└── README.md                  # This file
```

## Quick Start

### Prerequisites

- Python 3.10 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   cd /path/to/Project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**

   Create a `.env` file in the project root:
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

4. **Initialize database**
   ```bash
   mysql -u root -p < db/schema.sql
   mysql -u root -p flytau < db/seed.sql
   ```

5. **Run the server**
   ```bash
   cd app/server
   python main.py
   ```

   Server will be available at: http://localhost:5001

## Testing

Run the automated test script:
```bash
./test_api.sh
```

Or use pytest for unit tests:
```bash
pytest app/server/tests/
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new customer
- `POST /api/auth/login` - Login (customer or manager)
- `POST /api/auth/logout` - Logout current user
- `GET /api/auth/me` - Get current user information

### Flights
- `GET /api/flights` - Search available flights
- `GET /api/flights/{id}` - Get flight details with seat map

### Bookings & Orders
- `POST /api/bookings` - Create new booking
- `GET /api/orders` - Get user's orders
- `GET /api/orders/{id}` - Get specific order details
- `DELETE /api/orders/{id}` - Cancel order

### Admin (Manager Only)
- `POST /api/admin/flights` - Create new flight
- `DELETE /api/admin/flights/{id}` - Cancel flight
- `GET /api/admin/reports/occupancy` - Flight occupancy report
- `GET /api/admin/reports/revenue` - Revenue analysis
- `GET /api/admin/reports/staff-hours` - Staff working hours
- `GET /api/admin/reports/cancellations` - Cancellation statistics
- `GET /api/admin/reports/plane-activity` - Plane utilization

## Sample Credentials

**Manager Accounts:**
- ID: 100000001, Password: pass123
- ID: 100000002, Password: pass456

**Customer Account (for testing):**
- Email: testuser@example.com, Password: test123

## Database Schema

The system uses 15 tables:
- Customer, RegisteredCustomer, CustomerPhone
- Manager, Pilot, FlightAttendant
- Plane, PlaneClass, PlaneSeat, FlightLine
- Flight, FlightPilotAssignment, FlightAttendantAssignment
- FlightOrder, Ticket

See `db/schema.sql` for complete schema definition.

## Documentation

- [API Documentation](docs/API_DOCUMENTATION.md) - Detailed API reference
- [Setup Guide](docs/SETUP.md) - Complete setup instructions
- [Architecture](docs/ARCHITECTURE.md) - System design and architecture
- [Server README](app/README.md) - Server-specific documentation

## Academic Notes

This project has been simplified for academic purposes:
- Plain text password storage (NOT suitable for production)
- Simplified input validation
- Unified error handling with single exception class
- Direct JSON responses without wrapper abstractions

All simplifications maintain complete functionality while improving code clarity for educational purposes.

## Technology Stack

- **Backend**: Flask 3.1.0 (Python web framework)
- **Database**: MySQL 8.0+ with mysql-connector-python 9.4.0
- **Session Management**: Flask-Session 0.8.0
- **Testing**: pytest with pytest-flask
- **Language**: Python 3.10+

## License

Academic project - for educational purposes only.
