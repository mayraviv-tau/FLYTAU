# FLYTAU Flask REST API Server - Implementation Plan

## Overview
Create a complete Flask REST API server for the FLYTAU flight booking system under `/app/server/`. The server will implement all functionality from `docs/exercise2.txt` using session-based authentication, raw MySQL queries, and environment-based configuration.

## Database Context
- **Location:** `/db/schema.sql`, `/db/seed.sql`
- **Tables:** 15 tables (Manager, Pilot, FlightAttendant, Flight, Customer, RegisteredCustomer, FlightOrder, Ticket, Seat, Plane, PlaneClass, FlightLine, etc.)
- **Reports:** 5 pre-built SQL reports in `/db/reports_sql/`

## Directory Structure

```
app/
└── server/
    ├── __init__.py                 # Flask app factory
    ├── config.py                   # Configuration from .env
    ├── main.py                     # Application entry point
    │
    ├── db/
    │   ├── __init__.py
    │   ├── connection.py           # MySQL connection pool
    │   └── queries.py              # SQL query constants
    │
    ├── models/
    │   ├── __init__.py
    │   ├── user.py                 # User data classes
    │   ├── flight.py               # Flight data classes
    │   └── order.py                # Order data classes
    │
    ├── routes/
    │   ├── __init__.py
    │   ├── auth.py                 # POST /api/auth/register, /login, /logout
    │   ├── flights.py              # GET /api/flights, GET /api/flights/<id>
    │   ├── orders.py               # GET/POST/DELETE /api/orders
    │   ├── admin_flights.py        # POST/DELETE /api/admin/flights
    │   └── admin_reports.py        # GET /api/admin/reports/*
    │
    ├── middleware/
    │   ├── __init__.py
    │   ├── auth.py                 # @login_required, @manager_required decorators
    │   └── error_handlers.py       # Global error handlers
    │
    ├── services/
    │   ├── __init__.py
    │   ├── auth_service.py         # Register, login business logic
    │   ├── flight_service.py       # Flight search, seat availability
    │   ├── booking_service.py      # Create booking (transaction)
    │   ├── order_service.py        # Order management, cancellation
    │   └── report_service.py       # Execute SQL reports from files
    │
    ├── utils/
    │   ├── __init__.py
    │   ├── password.py             # Bcrypt hashing
    │   ├── validators.py           # Email, password, date validation
    │   └── responses.py            # Standard JSON response formatting
    │
    └── tests/
        ├── __init__.py
        ├── conftest.py             # Pytest fixtures
        ├── test_auth.py            # Auth endpoint tests
        ├── test_flights.py         # Flight endpoint tests
        ├── test_orders.py          # Order endpoint tests
        ├── test_admin_flights.py   # Admin flight tests
        └── test_admin_reports.py   # Admin report tests
```

## Core Components

### 1. Database Connection (`db/connection.py`)
- **Connection pooling** using `mysql.connector.pooling` (pool size: 10-20)
- **Functions:**
  - `get_connection_pool()` - Initialize pool from .env config
  - `get_db_connection()` - Context manager for connections
  - `execute_query(query, params, fetch_one, fetch_all, commit)` - Generic query executor
  - `execute_transaction(operations)` - Multi-operation transaction support

### 2. Authentication System (`middleware/auth.py`)
- **Session-based** using Flask-Session (filesystem storage)
- **Session structure:**
  ```python
  {
    'user_id': str,        # email (customer) or id_number (manager)
    'user_type': str,      # 'customer' or 'manager'
    'first_name': str,
    'last_name': str,
    'is_registered': bool  # True if RegisteredCustomer
  }
  ```
- **Decorators:**
  - `@login_required` - Any authenticated user
  - `@manager_required` - Manager only

### 3. Password Security (`utils/password.py`)
- **Bcrypt** hashing with cost factor 12
- `hash_password(password)` and `verify_password(password, hash)`
- **Note:** Existing plain-text passwords in seed data will need hashing

## API Endpoints

### Authentication (`/api/auth`)
- **POST /api/auth/register** - Register customer (email, password, first_name, last_name, birth_date, passport, phones)
  - Creates Customer + RegisteredCustomer + CustomerPhone records
  - Returns 201 with session

- **POST /api/auth/login** - Login customer or manager (email, password, user_type)
  - Verifies bcrypt password
  - Creates session

- **POST /api/auth/logout** - Clear session
- **GET /api/auth/me** - Get current user info (requires auth)

### Flights (`/api/flights`)
- **GET /api/flights** - Search flights (query: date, origin, destination)
  - Returns flights with status IN ('Active', 'Full')
  - Includes available seat counts per class

- **GET /api/flights/<id>** - Get flight details with seat map
  - Shows occupied vs available seats per class
  - Occupied = seats in Ticket table for active orders

### Bookings & Orders (`/api/orders`)
- **POST /api/bookings** - Create booking (requires customer auth)
  - **Transaction:** Insert FlightOrder + Tickets, update Flight status to 'Full' if needed
  - Deduct from RegisteredCustomer balance

- **GET /api/orders** - Get user's orders (query: filter=future|history)
  - Future: Active orders with departure > NOW()

- **GET /api/orders/<id>** - Get order details (must own order)
- **DELETE /api/orders/<id>** - Cancel order (must own order)
  - **Transaction:** Update order_status='Canceled_By_Client', total_payment=original*0.05, refund 95% to balance
  - Update Flight status from 'Full' to 'Active' if needed

### Admin - Flight Management (`/api/admin/flights`)
- **POST /api/admin/flights** - Create flight (requires manager auth)
  - **Validation:** Check crew requirements (long-haul vs short-haul), crew availability
  - **Transaction:** Insert Flight + FlightPilotAssignment + FlightAttendantAssignment

- **DELETE /api/admin/flights/<id>** - Cancel flight (requires manager auth)
  - **Transaction:** Update Flight status='Canceled', cancel all orders (100% refund to balance)

### Admin - Reports (`/api/admin/reports`)
All require manager auth. Execute SQL files from `/db/reports_sql/`:
- **GET /api/admin/reports/occupancy** - Average flight occupancy (report_1.sql)
- **GET /api/admin/reports/revenue** - Revenue by size/manufacturer/class (report_2.sql)
- **GET /api/admin/reports/staff-hours** - Staff flight hours (report_3.sql)
- **GET /api/admin/reports/cancellations** - Monthly cancellation rates (report_4.sql)
- **GET /api/admin/reports/plane-activity** - Plane utilization (report_5.sql)

## Key Business Logic

### Booking Creation (`services/booking_service.py`)
1. Validate flight exists and status='Active'
2. Check seat availability (no conflicts in Ticket table)
3. Calculate total_payment
4. **Transaction:**
   - INSERT FlightOrder
   - INSERT Ticket rows
   - UPDATE RegisteredCustomer balance (deduct)
   - UPDATE Flight status to 'Full' if all seats occupied

### Order Cancellation (`services/order_service.py`)
1. Verify order_status='Active' and flight not departed
2. Calculate refund: 95% (5% cancellation fee)
3. **Transaction:**
   - UPDATE FlightOrder (status='Canceled_By_Client', total_payment=original*0.05)
   - UPDATE RegisteredCustomer balance (add 95% refund)
   - UPDATE Flight status 'Full'->'Active' if seats freed

### Flight Creation (`services/flight_service.py`)
1. Validate FlightLine exists for route
2. Check crew requirements:
   - Long-haul (>6h): 3 pilots, 6 attendants (all long_haul_qualified)
   - Short-haul (≤6h): Large plane (3,6) or Small plane (2,3)
3. Verify crew availability (no schedule conflicts)
4. **Transaction:** INSERT Flight + crew assignments

### Flight Cancellation (`services/flight_service.py`)
1. **Transaction:**
   - UPDATE Flight status='Canceled'
   - For each active order: UPDATE status='Canceled_By_Company', total_payment=0
   - For registered customers: UPDATE balance (add 100% refund)

## Testing Strategy

### Fixtures (`tests/conftest.py`)
- `app()` - Test Flask app
- `client()` - Test client
- `db_connection()` - Test DB connection
- `authenticated_customer()` - Logged-in customer session
- `authenticated_manager()` - Logged-in manager session

### Test Coverage
- **test_auth.py** - Register (success, duplicate, invalid password), Login (success, wrong password), Logout, Get user
- **test_flights.py** - Search flights (filters), Get flight details, Seat availability
- **test_orders.py** - Create booking (success, invalid seats), Get orders (all/future), Cancel order
- **test_admin_flights.py** - Create flight (success, invalid crew), Cancel flight
- **test_admin_reports.py** - All 5 report endpoints return data

## Configuration Files

### `.env.example`
```bash
DB_HOST=localhost
DB_PORT=3306
DB_NAME=flytau
DB_USER=root
DB_PASSWORD=your_password

SECRET_KEY=generate_random_key_here
FLASK_ENV=development
FLASK_DEBUG=True
SESSION_TYPE=filesystem
```

### `requirements.txt`
```
Flask==3.0.0
mysql-connector-python==8.2.0
bcrypt==4.1.2
python-dotenv==1.0.0
pytest==7.4.3
pytest-flask==1.3.0
Flask-Session==0.5.0
```

### `pytest.ini`
```ini
[pytest]
testpaths = app/server/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

## Documentation Files

### `docs/API_DOCUMENTATION.md`
- Complete endpoint reference with request/response examples
- Authentication flow
- Error codes reference

### `docs/SETUP.md`
- Prerequisites (Python 3.10+, MySQL 8.0+)
- Database setup (run schema.sql, seed.sql)
- Environment configuration (.env)
- Running server: `python app/server/main.py`
- Running tests: `pytest`

### `docs/ARCHITECTURE.md`
- System architecture overview
- Database schema explanation
- Business logic flows (booking, cancellation, flight creation)
- Security considerations

## Critical Implementation Notes

1. **Transaction Safety:** Booking creation, order cancellation, flight creation, and flight cancellation MUST use database transactions
2. **Password Migration:** Seed data has plain-text passwords - hash on first use
3. **Race Conditions:** Use row-level locking when checking seat availability in transactions
4. **Flight Status Automation:** Auto-update status between Active/Full based on seat occupancy
5. **Balance Tracking:** Only for RegisteredCustomer (guests assumed to pay externally)

## Implementation Order

1. **Foundation** - config.py, db/connection.py, utils/ (password, validators, responses), middleware/error_handlers.py
2. **App Factory** - __init__.py
3. **Authentication** - models/user.py, services/auth_service.py, middleware/auth.py, routes/auth.py
4. **Core Features** - models/ (flight, order), services/ (flight, booking, order), routes/ (flights, orders)
5. **Admin Features** - services/report_service.py, routes/ (admin_flights, admin_reports)
6. **Entry Point** - main.py
7. **Documentation** - API_DOCUMENTATION.md, SETUP.md, ARCHITECTURE.md
8. **Testing** - tests/ (conftest.py, all test files)
9. **Configuration** - .env.example, requirements.txt, pytest.ini

## Success Criteria

✅ All endpoints from exercise2.txt implemented
✅ Session-based authentication working
✅ Database transactions for critical operations
✅ Tests passing for all endpoints
✅ API documentation complete
✅ Simple, readable code structure
✅ Ready for UI integration

---

**Total Files:** ~35 files
**Estimated Lines:** ~2500-3000 lines of Python code
**Key Files:** db/connection.py, services/booking_service.py, middleware/auth.py, routes/flights.py, __init__.py
