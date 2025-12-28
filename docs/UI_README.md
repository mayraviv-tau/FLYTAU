# FLYTAU Web UI Documentation

## Overview

This document describes the web-based user interface implemented for the FLYTAU flight booking system as part of an academic exercise in information systems.

## Features Implemented

### Customer Features
- Landing page with registration and login
- User registration and authentication
- Flight search with filters (date, origin, destination)
- Flight details with seat availability
- Interactive seat selection for booking
- Booking confirmation
- View all orders (upcoming and past)
- Order details
- Cancel orders with refund processing

### Manager Features
- Manager dashboard
- Create new flights with crew assignment
- Business logic validation during flight creation
- Manage all flights
- Cancel flights (with automatic customer refunds)
- Business reports (5 types):
  - Average flight occupancy
  - Revenue analysis
  - Staff accumulated flight hours
  - Monthly cancellation rates
  - Monthly plane activity summary

## Technology Stack

- **Backend**: Flask (server-side rendering)
- **Templates**: Jinja2
- **Styling**: Vanilla CSS (no frameworks)
- **Design**: Professional airline interface
- **JavaScript**: None (pure server-side rendering)

## Starting the Server

```bash
# From project root
source venv/bin/activate
PYTHONPATH=. python app/server/main.py
```

The server will start on: `http://localhost:5001`

## Accessing the UI

1. **Home Page**: [http://localhost:5001/](http://localhost:5001/)
2. **Customer Login**: [http://localhost:5001/login](http://localhost:5001/login)
3. **Customer Registration**: [http://localhost:5001/register](http://localhost:5001/register)
4. **Manager Login**: [http://localhost:5001/login](http://localhost:5001/login) (select "Manager" tab)

## Test Credentials

### Manager Accounts
- ID: `100000001`, Password: `pass123`
- ID: `100000002`, Password: `pass456`

### Customer Account
- Email: `testuser@example.com`, Password: `test123`

Or register a new customer account.

## URL Structure

### Public (No Authentication)
- `/` - Landing page
- `/login` - Login
- `/register` - Registration
- `/logout` - Logout (POST)

### Customer Pages
- `/customer/dashboard` - Home
- `/customer/flights` - Search results
- `/customer/flights/<id>` - Flight details
- `/customer/book/<id>` - Booking form
- `/customer/orders` - My orders
- `/customer/orders/<id>` - Order details

### Manager Pages
- `/manager/dashboard` - Manager home
- `/manager/flights/create` - Create flight
- `/manager/flights` - Manage flights
- `/manager/reports` - Reports dashboard
- `/manager/reports/<type>` - View specific report

## Project Structure

```
app/ui/
├── routes/
│   ├── public.py      # Landing, login, register
│   ├── customer.py    # Customer pages
│   └── manager.py     # Manager pages with business logic
├── templates/
│   ├── base.html
│   ├── components/    # Reusable components
│   ├── public/        # Public pages
│   ├── customer/      # Customer pages
│   ├── manager/       # Manager pages
│   └── errors/        # Error pages
└── static/
    ├── css/           # Stylesheets
    └── images/        # Assets
```

## Key Implementation Details

### Server-Side Rendering
- All pages rendered on the server
- No JavaScript (academic constraint)
- Direct service integration (not HTTP API calls)

### Authentication
- Session-based authentication using Flask-Session
- Role-based access control (customer/manager)
- Automatic redirection for protected routes
- Managers cannot purchase tickets (enforced at both route and service levels)

### Business Logic Validation

The flight creation form includes comprehensive validation:

#### Aircraft and Flight Compatibility
- Small aircraft can only be assigned to short-haul flights (6 hours or less)
- Large aircraft can handle both short and long-haul flights
- Flight duration is automatically retrieved from the FlightLine table

#### Crew Requirements
- Large aircraft require 3 pilots and 6 flight attendants
- Small aircraft require 2 pilots and 3 flight attendants
- Long-haul flights (over 6 hours) require crew with long-haul qualifications
- Crew qualification status is displayed in the UI during flight creation

#### Flight Status Transitions
- Flights start with "Active" status
- Automatically transition to "Full" when all seats are booked
- Automatically transition to "Landed" after departure time plus flight duration
- The `update_completed_flights()` function should be called periodically

### User Experience
- Clean, professional design
- Flash messages for user feedback
- Responsive layout
- Intuitive navigation

### Seat Selection
- Visual seat map
- Checkbox-based selection (no JavaScript)
- Business and Economy class distinction
- Real-time availability display

## Business Reports

All five business reports use SQL queries from the `db/reports_sql` directory:

1. **Average Flight Occupancy** - Shows occupancy percentage for completed flights
2. **Revenue Analysis** - Breakdown by plane size, manufacturer, and class
3. **Staff Accumulated Flight Hours** - Separates long-haul and short-haul hours
4. **Monthly Cancellation Rates** - Percentage of canceled orders per month
5. **Monthly Plane Activity Summary** - Plane utilization metrics

## User Flows

### Customer Flow
1. Register or login
2. Search for flights
3. View flight details
4. Select seats and book
5. View confirmation
6. Manage orders and cancellations

### Manager Flow
1. Login with manager credentials
2. Create flights with proper crew assignment
3. Manage existing flights
4. View business analytics reports

## Files Created

### Routes (3 files)
- `app/ui/routes/public.py`
- `app/ui/routes/customer.py`
- `app/ui/routes/manager.py`

### Templates (25 files)
- Base and components (4)
- Public pages (3)
- Customer pages (7)
- Manager pages (5)
- Error pages (4)
- Additional error template (1)

### Stylesheets (5 files)
- `static/css/main.css`
- `static/css/components.css`
- `static/css/forms.css`
- `static/css/tables.css`
- `static/css/seat-map.css`

### Modified Files
- `app/server/__init__.py` - Flask integration
- `app/server/middleware/error_handlers.py` - Dual HTML/JSON responses
- `app/server/middleware/auth.py` - UI-aware decorators

## Troubleshooting

### Server Won't Start
- Ensure virtual environment is activated: `source venv/bin/activate`
- Set PYTHONPATH: `PYTHONPATH=. python app/server/main.py`
- Check database connection in `.env`

### Templates Not Found
- Verify template_folder path in `app/server/__init__.py`
- Check templates exist in `app/ui/templates/`

### CSS Not Loading
- Check static_folder path in `app/server/__init__.py`
- Verify CSS files exist in `app/ui/static/css/`
- Clear browser cache

### Session Issues
- Verify `app/server/flask_session/` directory exists
- Check SECRET_KEY in `.env`
- Clear session directory if needed

### Flight Creation Errors
- Ensure valid flight route exists in FlightLine table
- Check crew qualifications match flight duration requirements
- Verify sufficient crew members are selected for aircraft size

## Academic Notes

This UI implementation has been designed for academic purposes with the following considerations:

- Session-based authentication using Flask-Session (server-side sessions)
- No JavaScript requirement maintains simplicity for educational demonstration
- Direct service layer integration instead of internal API calls
- Flash messages provide immediate user feedback
- Business logic validation demonstrates understanding of database constraints

All business rules are enforced at the service level to maintain data integrity and demonstrate proper application architecture.

## Related Documentation

- Implementation details: See [UI_GUIDE.md](UI_GUIDE.md)
- API integration: See [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- Architecture: See [ARCHITECTURE.md](ARCHITECTURE.md)
- Business logic: See [business-logic-implementation.md](business-logic-implementation.md)
- Test results: See [test-results.md](test-results.md)

## Implementation Status

The web UI is complete and operational with all required features:
- Customer booking workflow
- Manager flight management
- Business logic validation
- Comprehensive reporting
- Role-based access control

Server running on http://localhost:5001
