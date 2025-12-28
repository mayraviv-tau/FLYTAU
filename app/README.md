# FLYTAU Flask Server

REST API server for the FLYTAU flight booking system.

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

Server will start at `http://localhost:5000`

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

✅ Session-based authentication
✅ Customer registration and login
✅ Manager authentication
✅ Flight search with filters
✅ Seat availability checking
✅ Booking creation with balance deduction
✅ Order management and cancellation
✅ Flight creation and cancellation (admin)
✅ Administrative reports (5 reports)
✅ Comprehensive test coverage
✅ Transaction safety for critical operations
✅ Input validation and error handling

## Technology Stack

- Flask 3.0.0
- MySQL 8.0+
- mysql-connector-python 8.2.0
- bcrypt 4.1.2
- pytest 7.4.3
- Flask-Session 0.5.0

## Security

- Bcrypt password hashing
- Session-based authentication
- Role-based access control
- SQL injection prevention
- Input validation

## Sample Credentials

**Managers (from seed data):**
- ID: 200000001, Password: manager123
- ID: 200000002, Password: manager456

**Customers (from seed data):**
- alice.thompson@gmail.com (balance: $1500)
- michael.chen@yahoo.com (balance: $200)
