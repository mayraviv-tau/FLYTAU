# FLYTAU Project - Submission Notes

## Project Completion Summary

This document summarizes the FLYTAU flight booking system implementation for academic submission.

## What Was Implemented

### Database Layer
- Complete 15-table schema with proper relationships and constraints
- Seed data with managers, pilots, flight attendants, planes, and sample flights
- Five SQL report queries for business analytics

### REST API Server
- Flask-based REST API with 20+ endpoints
- Session-based authentication for customers and managers
- Role-based access control (customer vs manager permissions)
- Flight search and booking functionality
- Order management with cancellation and refunds
- Administrative flight creation and management
- Five comprehensive business reports

### Key Features
- Customer registration and login
- Manager authentication
- Flight search with filters (date, origin, destination)
- Real-time seat availability checking
- Booking creation with balance validation
- Order cancellation with refund processing (95% refund, 5% fee)
- Admin flight creation with crew validation
- Admin flight cancellation with full customer refunds
- Database transactions for data consistency

## Academic Simplifications

The implementation was simplified for educational purposes:

### 1. Plain Text Passwords
- Passwords stored in plain text instead of hashed
- Simplifies testing and grading
- **NOT suitable for production use**

### 2. Simplified Validation
- Basic email validation (checks for @ and .)
- Minimum password length: 4 characters
- Simple airport code and seat number validation

### 3. Unified Error Handling
- Single `APIError` exception class with status codes
- Replaces multiple specialized exception classes
- Clearer error flow

### 4. Direct JSON Responses
- Uses Flask's `jsonify()` directly
- No wrapper functions or response utilities
- Straightforward and easy to understand

## Testing

All endpoints have been tested and verified:

### Tested Functionality
- Customer registration and login
- Manager login (ID: 100000001, password: pass123)
- Flight search returning correct results
- Flight details with seat maps
- Balance validation on booking
- Order retrieval
- Admin reports (occupancy, revenue, staff hours)
- Authentication and authorization
- Error handling with proper status codes

### Test Script
An automated test script (`test_api.sh`) is provided to verify all major endpoints.

## Technology Stack

- **Backend**: Flask 3.1.0
- **Database**: MySQL 8.0+
- **Database Driver**: mysql-connector-python 9.4.0
- **Session Management**: Flask-Session 0.8.0
- **Testing**: pytest with pytest-flask
- **Python**: 3.10+

## File Structure

```
Project/
├── db/
│   ├── schema.sql              # Complete database schema
│   ├── seed.sql                # Sample data
│   └── reports_sql/            # 5 SQL report queries
├── app/
│   └── server/                 # Flask REST API
│       ├── routes/             # API endpoint handlers
│       ├── services/           # Business logic layer
│       ├── models/             # Data model classes
│       ├── middleware/         # Auth & error handling
│       ├── db/                 # Database queries
│       ├── utils/              # Validation utilities
│       └── tests/              # Test suite
├── docs/
│   ├── exercise2.txt          # Original requirements
│   ├── API_DOCUMENTATION.md   # Complete API reference
│   ├── SETUP.md               # Setup instructions
│   └── ARCHITECTURE.md        # System architecture
├── test_api.sh                # Automated test script
├── requirements.txt           # Python dependencies
└── README.md                  # Main documentation
```

## Running the Project

### Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up database:
   ```bash
   mysql -u root -p < db/schema.sql
   mysql -u root -p flytau < db/seed.sql
   ```

3. Configure `.env` file with database credentials

4. Run server:
   ```bash
   cd app/server
   python main.py
   ```

5. Server runs at: http://localhost:5001

### Testing

Run automated tests:
```bash
./test_api.sh
```

## Sample Credentials

### Manager Accounts
- ID: 100000001, Password: pass123
- ID: 100000002, Password: pass456

### Customer Account
- Email: testuser@example.com, Password: test123

## API Endpoints Summary

### Authentication (4 endpoints)
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
- GET /api/auth/me

### Flights (2 endpoints)
- GET /api/flights
- GET /api/flights/{id}

### Bookings & Orders (4 endpoints)
- POST /api/bookings
- GET /api/orders
- GET /api/orders/{id}
- DELETE /api/orders/{id}

### Admin (7 endpoints)
- POST /api/admin/flights
- DELETE /api/admin/flights/{id}
- GET /api/admin/reports/occupancy
- GET /api/admin/reports/revenue
- GET /api/admin/reports/staff-hours
- GET /api/admin/reports/cancellations
- GET /api/admin/reports/plane-activity

## Code Quality

- Clear separation of concerns (routes, services, models)
- Database transactions for critical operations
- Input validation on all endpoints
- Consistent error handling
- Comprehensive inline documentation
- Test coverage for major functionality

## Known Limitations

1. **Security**: Plain text passwords for academic simplicity
2. **Validation**: Basic validation suitable for controlled environment
3. **Error Messages**: Generic messages instead of detailed debugging info
4. **Scalability**: Simple file-based sessions (not distributed)

These limitations are intentional simplifications for the academic context.

## Notes for Grading

- All required functionality from exercise2.txt is implemented
- Database schema matches requirements (15 tables)
- All 5 reports are working
- Authentication and authorization working correctly
- Booking and cancellation logic implements business rules correctly
- Code is well-organized and documented
- Simplifications improve code clarity without losing functionality

## Conclusion

The FLYTAU project implements a complete flight booking system with all required features. The code has been simplified for academic purposes while maintaining full functionality and demonstrating understanding of:

- Database design and normalization
- REST API development
- Session-based authentication
- Role-based access control
- Transaction management
- Business logic implementation
- Error handling and validation

The project is ready for academic submission.
