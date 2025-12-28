# FLYTAU System Architecture

System architecture documentation for the FLYTAU flight booking system.

## System Overview

FLYTAU is a Flask-based REST API server for managing flight bookings, implementing a complete airline reservation system with user management, flight search, booking, and administrative features.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│                  (Future UI / API Consumers)                 │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP/REST
┌────────────────────────────┴────────────────────────────────┐
│                      Flask Application                       │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    Routes Layer                        │  │
│  │  - Auth Routes      - Order Routes                     │  │
│  │  - Flight Routes    - Admin Routes                     │  │
│  └──────────────────────┬────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────┴────────────────────────────────┐  │
│  │                 Middleware Layer                       │  │
│  │  - Authentication (@login_required, @manager_required) │  │
│  │  - Error Handlers (APIError, ValidationError)          │  │
│  └──────────────────────┬────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────┴────────────────────────────────┐  │
│  │                  Service Layer                         │  │
│  │  - auth_service     - order_service                    │  │
│  │  - flight_service   - report_service                   │  │
│  │  - booking_service                                     │  │
│  └──────────────────────┬────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────┴────────────────────────────────┐  │
│  │               Database Layer                           │  │
│  │  - Connection Pool  - Query Execution                  │  │
│  │  - Transaction Management                              │  │
│  └──────────────────────┬────────────────────────────────┘  │
└─────────────────────────┴────────────────────────────────────┘
                          │
┌─────────────────────────┴────────────────────────────────────┐
│                      MySQL Database                          │
│  - 15 Tables (Customers, Flights, Orders, Staff, etc.)      │
└──────────────────────────────────────────────────────────────┘
```

## Technology Stack

- **Backend Framework:** Flask 3.0.0
- **Database:** MySQL 8.0+
- **Database Driver:** mysql-connector-python 8.2.0
- **Authentication:** Flask-Session (session-based)
- **Password Hashing:** bcrypt 4.1.2
- **Testing:** pytest 7.4.3, pytest-flask 1.3.0
- **Configuration:** python-dotenv 1.0.0

## Directory Structure

```
app/server/
├── __init__.py              # Flask app factory
├── config.py                # Configuration management
├── main.py                  # Application entry point
│
├── db/                      # Database layer
│   ├── connection.py        # Connection pooling
│   └── queries.py           # SQL query constants
│
├── models/                  # Data models
│   ├── user.py             # User, RegisteredCustomer, Manager
│   ├── flight.py           # Flight, FlightDetails
│   └── order.py            # Order, Ticket
│
├── routes/                  # API endpoints
│   ├── auth.py             # Authentication routes
│   ├── flights.py          # Flight search routes
│   ├── orders.py           # Booking & order routes
│   ├── admin_flights.py    # Flight management
│   └── admin_reports.py    # Administrative reports
│
├── middleware/              # Middleware components
│   ├── auth.py             # Authentication decorators
│   └── error_handlers.py   # Global error handling
│
├── services/                # Business logic layer
│   ├── auth_service.py     # User registration/login
│   ├── flight_service.py   # Flight search/seat availability
│   ├── booking_service.py  # Booking creation
│   ├── order_service.py    # Order management
│   └── report_service.py   # Report generation
│
├── utils/                   # Utility functions
│   ├── password.py         # Password hashing
│   ├── validators.py       # Input validation
│   └── responses.py        # Response formatting
│
└── tests/                   # Test suite
    ├── conftest.py         # Test fixtures
    ├── test_auth.py        # Auth tests
    ├── test_flights.py     # Flight tests
    ├── test_orders.py      # Order tests
    ├── test_admin_flights.py
    └── test_admin_reports.py
```

## Database Schema

### Core Entities

**Employees:**
- Manager (id_number, names_hebrew, password)
- Pilot (id_number, is_long_haul_qualified)
- FlightAttendant (id_number, is_long_haul_qualified)

**Infrastructure:**
- Plane (plane_id, manufacturer, size_category)
- PlaneClass (plane_id, class_type, rows_count, cols_count)
- Seat (plane_id, class_type, seat_number)
- FlightLine (origin_airport, destination_airport, flight_duration)

**Operations:**
- Flight (flight_id, origin, destination, plane_id, departure_datetime, manager_id, status)
- FlightPilotAssignment (pilot_id, flight_id)
- FlightAttendantAssignment (attendant_id, flight_id)

**Customers:**
- Customer (email, first_name_english, last_name_english)
- RegisteredCustomer (email, birth_date, passport, password, balance)
- CustomerPhone (email, phone_number)

**Orders:**
- FlightOrder (order_id, customer_email, flight_id, order_date, order_status, total_payment)
- Ticket (order_id, plane_id, class_type, seat_number, price)

### Key Relationships

```
Flight ──┬── belongs to → Plane
         ├── uses → FlightLine
         ├── managed by → Manager
         └── assigned to → Pilots, FlightAttendants

FlightOrder ──┬── placed by → Customer
              ├── for → Flight
              └── contains → Tickets

Ticket ──┬── part of → FlightOrder
         └── reserves → Seat
```

## Business Logic Flows

### User Registration

1. Validate email format and password strength
2. Check for duplicate email
3. Hash password with bcrypt
4. Transaction:
   - Insert into Customer table
   - Insert into RegisteredCustomer table
   - Insert phone numbers into CustomerPhone
5. Create session
6. Return customer data

### Flight Booking

1. Validate flight exists and status is Active
2. Check flight hasn't departed
3. Verify seat availability (no conflicts)
4. Calculate total payment
5. Check customer balance (if registered)
6. Transaction:
   - Insert FlightOrder
   - Insert Ticket records
   - Deduct from customer balance
7. Update flight status to Full if all seats occupied
8. Return order details

### Order Cancellation

1. Verify order exists and belongs to customer
2. Check order status is Active
3. Check flight hasn't departed
4. Calculate refund (95%) and fee (5%)
5. Transaction:
   - Update order status to Canceled_By_Client
   - Update order payment to fee amount
   - Add refund to customer balance
6. Update flight status Full → Active if seats freed
7. Return cancellation details

### Flight Creation (Admin)

1. Validate flight route exists
2. Validate plane exists
3. Determine crew requirements:
   - Long-haul (>6h): 3 pilots, 6 attendants (qualified)
   - Short-haul (≤6h): 2-3 pilots, 3-6 attendants by plane size
4. Validate pilot/attendant qualifications
5. Check crew availability (no schedule conflicts)
6. Transaction:
   - Insert Flight
   - Insert pilot assignments
   - Insert attendant assignments
7. Return flight details

### Flight Cancellation (Admin)

1. Verify flight exists and not Landed
2. Get all active orders for flight
3. Transaction:
   - Update flight status to Canceled
   - For each active order:
     - Update status to Canceled_By_Company
     - Set payment to 0 (full refund)
     - Add 100% refund to customer balance
4. Return cancellation summary

## Security Features

### Authentication

- **Session-based authentication** using Flask-Session
- Sessions stored on filesystem
- Session cookies with HTTP-only and secure flags (production)
- 24-hour session lifetime

### Password Security

- Bcrypt hashing with cost factor 12
- Plain-text passwords from seed data handled on first login
- Never store or log plain-text passwords

### Authorization

- **@login_required** decorator for authenticated routes
- **@manager_required** decorator for admin routes
- Ownership checks for customer data access

### Input Validation

- Email format validation
- Password strength requirements (min 8 characters)
- Date/datetime format validation
- Airport code validation (3 uppercase letters)
- Seat number format validation

### Database Security

- Parameterized queries to prevent SQL injection
- Connection pooling with automatic reconnection
- Transaction rollback on errors
- Database credentials in environment variables

## Error Handling

### Custom Exception Classes

```python
APIError (400)
├── ValidationError (400)
├── AuthenticationError (401)
├── AuthorizationError (403)
├── NotFoundError (404)
└── DatabaseError (500)
```

### Global Error Handlers

All errors return standardized JSON responses:

```json
{
  "success": false,
  "error": "ErrorType",
  "message": "Detailed error message"
}
```

## Performance Considerations

### Database Connection Pooling

- Pool size: 10-20 connections
- Automatic connection recovery
- Timeout: 30 seconds
- Reuses connections for efficiency

### Query Optimization

- Indexed foreign keys
- Composite keys for efficient joins
- Strategic use of transactions
- Fetch only required columns

### Caching Strategy

- Session data cached on filesystem
- Database pool maintains active connections
- Future: Redis for session storage (scalability)

## Scalability

### Current Architecture

- Single server deployment
- Session storage on filesystem
- Connection pooling for DB efficiency

### Future Improvements

1. **Horizontal Scaling:**
   - Load balancer (Nginx, HAProxy)
   - Multiple Flask instances
   - Redis for shared session storage

2. **Database:**
   - Read replicas for reporting
   - Connection pool per instance
   - Query caching

3. **Microservices:**
   - Separate booking service
   - Separate reporting service
   - Message queue for async tasks (Celery)

## Monitoring & Logging

### Current Implementation

- Flask debug mode (development)
- Error logging to console
- MySQL query logging

### Production Recommendations

1. Application logging (Winston, Loguru)
2. Error tracking (Sentry)
3. Performance monitoring (New Relic, DataDog)
4. Database query profiling
5. API request/response logging

## Testing Strategy

### Test Coverage

- **Unit tests:** Services, utilities, models
- **Integration tests:** API endpoints
- **Authentication tests:** Login, registration, access control
- **Business logic tests:** Booking, cancellation, flight creation

### Test Database

- Separate test database (flytau_test)
- Fixtures for test data
- Cleanup after each test

### Running Tests

```bash
pytest                           # Run all tests
pytest -v                        # Verbose output
pytest --cov=app/server          # With coverage
pytest app/server/tests/test_auth.py  # Specific file
```

## Deployment

### Development

```bash
python app/server/main.py
# or
flask --app app.server.main:app run
```

### Production

```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app.server.main:app"

# With Nginx reverse proxy
# Nginx -> Gunicorn -> Flask App
```

### Environment Variables

- `FLASK_ENV`: development/production
- `SECRET_KEY`: Session encryption key
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`: Database credentials

## API Design Principles

1. **RESTful conventions:** Proper HTTP methods and status codes
2. **Consistent responses:** Standard success/error format
3. **Resource-based URLs:** `/api/flights`, `/api/orders`
4. **Authentication required:** Protected routes use decorators
5. **Meaningful errors:** Detailed error messages for debugging

## Future Enhancements

1. **Email notifications:** Order confirmations, flight cancellations
2. **Payment integration:** Stripe, PayPal
3. **Real-time updates:** WebSockets for flight status
4. **Mobile app support:** JWT authentication
5. **Admin dashboard:** Web UI for managers
6. **Analytics:** Advanced reporting and insights
7. **Multi-language support:** i18n for Hebrew/English
