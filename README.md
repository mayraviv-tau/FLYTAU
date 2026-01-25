# FLYTAU Flight Booking System

Academic project implementing a complete flight booking management system with Flask web application.

**Live Demo:** https://amithovav.pythonanywhere.com

## Project Overview

FLYTAU is a flight booking system that manages flights, customer bookings, and administrative operations. The system includes:

- Customer registration and authentication
- Flight search and booking (registered users and guests)
- Order management with cancellation and refunds
- Administrative flight creation and management
- Staff management (pilots, flight attendants, planes)
- Comprehensive reporting for business analytics

## Project Structure

```
FLYTAU/
├── app/                        # Flask Application
│   ├── routes/                 # Route handlers
│   │   ├── auth.py            # Authentication routes
│   │   ├── flights.py         # Flight search & management
│   │   ├── orders.py          # Order & booking management
│   │   ├── managers.py        # Admin operations
│   │   └── reports.py         # Business reports
│   ├── templates/              # Jinja2 HTML templates
│   │   ├── base.html          # Base template
│   │   ├── auth/              # Login & registration
│   │   ├── flights/           # Flight pages
│   │   ├── orders/            # Order pages
│   │   ├── managers/          # Admin pages
│   │   └── reports/           # Report pages
│   ├── static/                 # Static assets
│   │   ├── css/style.css      # Stylesheet
│   │   └── images/            # Images & logo
│   ├── utils/                  # Utility functions
│   │   └── auth.py            # Authentication helpers
│   ├── app.py                  # Flask app factory
│   ├── config.py               # Configuration
│   ├── database.py             # Database connection
│   └── requirements.txt        # Python dependencies
├── db/                         # Database layer
│   ├── schema.sql              # Database schema
│   ├── seed.sql                # Sample data
│   ├── init_database.sql       # Full initialization script
│   └── reports_sql/            # SQL queries for reports
│       ├── report_1.sql        # Average occupancy
│       ├── report_2.sql        # Revenue analysis
│       ├── report_3.sql        # Staff flight hours
│       ├── report_4.sql        # Cancellation rates
│       └── report_5.sql        # Plane activity
├── credentials.txt             # Test credentials
└── README.md                   # This file
```

## Quick Start

### Prerequisites

- Python 3.10 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/Amithovav/Flytau.git
   cd Flytau
   ```

2. **Install dependencies**
   ```bash
   cd app
   pip install -r requirements.txt
   ```

3. **Configure database**

   Set environment variables or edit `app/config.py`:
   ```bash
   export DB_HOST=localhost
   export DB_USER=root
   export DB_PASSWORD=your_password
   export DB_NAME=flytau
   export DB_PORT=3306
   ```

   Or edit the defaults directly in `app/config.py`.

4. **Initialize database**
   ```bash
   mysql -u root -p < db/init_database.sql
   ```

   Or run schema and seed separately:
   ```bash
   mysql -u root -p < db/schema.sql
   mysql -u root -p flytau < db/seed.sql
   ```

5. **Run the application**
   ```bash
   cd app
   python app.py
   ```

   Application will be available at: http://localhost:5001

## Features

### Customer Features
- **Flight Search**: Search by origin, destination, and date
- **Seat Selection**: Visual seat map with class selection
- **Guest Booking**: Book without registration using email
- **Order Management**: View active orders and history
- **Order Cancellation**: Cancel orders (5% fee, 36+ hours before flight)

### Manager Features
- **Flight Management**: Create flights, set prices, cancel flights
- **Staff Management**: Add/view pilots and flight attendants
- **Plane Management**: Add planes, configure seat classes
- **Reports**: 5 business analytics reports
  1. Average flight occupancy
  2. Revenue by plane size, manufacturer, and class
  3. Staff cumulative flight hours
  4. Monthly cancellation rates
  5. Plane activity and utilization

## Sample Credentials

### Manager Accounts
| ID Number | Password |
|-----------|----------|
| 100000001 | pass123  |
| 100000002 | pass456  |

### Customer Accounts
| Email | Password |
|-------|----------|
| c1@test.com | pass |
| c2@test.com | pass |

## Database Schema

The system uses 15 tables:

**Users:**
- Customer, RegisteredCustomer, CustomerPhone
- Manager, Pilot, FlightAttendant

**Assets:**
- Plane, PlaneClass, Seat, FlightLine

**Operations:**
- Flight, FlightPilotAssignment, FlightAttendantAssignment
- FlightOrder, Ticket

See `db/schema.sql` for complete schema definition.

## Business Rules

- **Cancellation by Customer**: Allowed 36+ hours before departure, 5% fee
- **Cancellation by Company**: Allowed 72+ hours before departure, full refund
- **Flight Status**: Active → Full (when sold out) → Landed (after departure)
- **Order Status**: Active → Completed/Canceled_By_Client/Canceled_By_Company
- **Small Planes**: Economy class only (no Business class)

## Technology Stack

- **Backend**: Flask 3.x (Python web framework)
- **Database**: MySQL 8.0+ with mysql-connector-python
- **Templates**: Jinja2
- **Session**: Flask-Session (filesystem)
- **Frontend**: HTML5, CSS3, Font Awesome icons
- **Language**: Python 3.10+

## Academic Notes

This project was developed for academic purposes:
- Plain text password storage (NOT suitable for production)
- Simplified input validation
- Session-based authentication
- Hebrew RTL interface support

## Authors

Group 14 - Database Systems Course

## License

Academic project - for educational purposes only.
