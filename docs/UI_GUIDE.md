# FLYTAU Web UI Guide

## Overview

The FLYTAU web UI is a server-side rendered interface built with HTML/Jinja2 templates and vanilla CSS. It provides a complete user interface for the flight booking system, supporting both customer and manager functionalities.

## Technology Stack

- **Templates**: Jinja2 (Flask templating engine)
- **Styling**: Vanilla CSS (no frameworks)
- **Backend Integration**: Direct service calls (not HTTP requests)
- **Session Management**: Flask-Session (filesystem storage)
- **Design**: Inspired by AA.com - clean, professional airline interface

## Architecture

### Directory Structure

```
app/ui/
├── __init__.py                          # UI package initialization
├── routes/                              # Route handlers
│   ├── __init__.py
│   ├── public.py                        # Public pages (landing, login, register)
│   ├── customer.py                      # Customer pages (flights, booking, orders)
│   └── manager.py                       # Manager pages (flights, reports)
├── templates/                           # Jinja2 templates
│   ├── base.html                        # Base template
│   ├── components/                      # Reusable components
│   │   ├── header.html
│   │   ├── footer.html
│   │   ├── flash_messages.html
│   │   └── flight_card.html
│   ├── public/                          # Public templates
│   │   ├── landing.html
│   │   ├── login.html
│   │   └── register.html
│   ├── customer/                        # Customer templates
│   │   ├── dashboard.html
│   │   ├── search_flights.html
│   │   ├── flight_details.html
│   │   ├── booking_form.html
│   │   ├── booking_confirmation.html
│   │   ├── my_orders.html
│   │   └── order_details.html
│   ├── manager/                         # Manager templates
│   │   ├── dashboard.html
│   │   ├── create_flight.html
│   │   ├── manage_flights.html
│   │   ├── reports.html
│   │   └── report_details.html
│   └── errors/                          # Error pages
│       ├── 404.html
│       ├── 403.html
│       ├── 500.html
│       └── error.html
└── static/                              # Static assets
    ├── css/
    │   ├── main.css                     # Global styles
    │   ├── components.css               # Component styles
    │   ├── forms.css                    # Form styling
    │   ├── tables.css                   # Table layouts
    │   └── seat-map.css                 # Seat map visualization
    └── images/                          # Images (logo, favicon)
```

### Integration with Flask

The UI is integrated into the existing Flask server in `app/server/__init__.py`:

```python
# Configure template and static folders
app = Flask(__name__,
            template_folder='../ui/templates',
            static_folder='../ui/static')

# Register UI blueprints
app.register_blueprint(public.bp, url_prefix='')
app.register_blueprint(customer.bp, url_prefix='/customer')
app.register_blueprint(manager.bp, url_prefix='/manager')
```

## URL Structure

### Public Routes (No Authentication)
- `/` - Landing page
- `/login` - Login page (customer & manager)
- `/register` - Customer registration
- `/logout` - Logout (POST only)

### Customer Routes (Requires Customer Authentication)
- `/customer/dashboard` - Customer home page
- `/customer/flights` - Search flights
- `/customer/flights/<id>` - Flight details
- `/customer/book/<id>` - Booking form
- `/customer/booking-confirmation/<order_id>` - Booking confirmation
- `/customer/orders` - View all orders
- `/customer/orders/<id>` - Order details
- `/customer/orders/<id>/cancel` - Cancel order (POST only)

### Manager Routes (Requires Manager Authentication)
- `/manager/dashboard` - Manager home page
- `/manager/flights/create` - Create new flight
- `/manager/flights` - Manage all flights
- `/manager/flights/<id>/cancel` - Cancel flight (POST only)
- `/manager/reports` - Reports dashboard
- `/manager/reports/occupancy` - Occupancy report
- `/manager/reports/revenue` - Revenue report
- `/manager/reports/staff-hours` - Staff hours report
- `/manager/reports/cancellations` - Cancellations report
- `/manager/reports/plane-activity` - Plane activity report

## Template Patterns

### Template Inheritance

All pages extend `base.html`:

```jinja2
{% extends 'base.html' %}

{% block title %}Page Title{% endblock %}

{% block extra_css %}
<!-- Optional extra CSS -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/seat-map.css') }}">
{% endblock %}

{% block content %}
<!-- Page content here -->
{% endblock %}
```

### Including Components

```jinja2
{% include 'components/header.html' %}
{% include 'components/flash_messages.html' %}
```

### Using Macros

```jinja2
{% from 'components/flight_card.html' import render_flight %}

{% for flight in flights %}
    {{ render_flight(flight) }}
{% endfor %}
```

### URL Generation

Always use `url_for()` for generating URLs:

```jinja2
<a href="{{ url_for('customer.dashboard') }}">Dashboard</a>
<a href="{{ url_for('customer.flight_details', flight_id=123) }}">View Flight</a>
```

### Static Assets

```jinja2
<link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
<img src="{{ url_for('static', filename='images/logo.png') }}" alt="FLYTAU">
```

## Form Handling

### GET Forms (Search)

```jinja2
<form method="GET" action="{{ url_for('customer.flights') }}">
    <input type="date" name="date">
    <input type="text" name="origin">
    <input type="text" name="destination">
    <button type="submit">Search</button>
</form>
```

### POST Forms (Actions)

```jinja2
<form method="POST" action="{{ url_for('public.login') }}">
    <input type="email" name="email" required>
    <input type="password" name="password" required>
    <button type="submit">Login</button>
</form>
```

### Multi-Select Forms (Checkboxes)

```jinja2
<form method="POST">
    {% for seat in available_seats %}
    <label>
        <input type="checkbox" name="selected_seats" value="{{ seat.number }}">
        {{ seat.number }}
    </label>
    {% endfor %}
    <button type="submit">Book</button>
</form>
```

## Flash Messages

### Setting Flash Messages (in routes)

```python
from flask import flash

flash('Operation successful!', 'success')
flash('An error occurred', 'error')
flash('Please note...', 'warning')
```

### Displaying Flash Messages (in templates)

Flash messages are automatically displayed via `components/flash_messages.html` which is included in `base.html`.

## Authentication

### Route Protection

**UI Routes** use special decorators that redirect instead of returning JSON errors:

```python
from ...server.middleware.auth import ui_login_required, ui_manager_required

@bp.route('/dashboard')
@ui_login_required
def dashboard():
    # Customer or manager required
    pass

@bp.route('/manager/dashboard')
@ui_manager_required
def manager_dashboard():
    # Manager only
    pass
```

### Getting Current User

```python
from ...server.middleware.auth import get_current_user

@bp.route('/dashboard')
@ui_login_required
def dashboard():
    current_user = get_current_user()
    # Returns: {user_id, user_type, first_name, last_name, is_registered}
```

### Session Variables (in templates)

```jinja2
{% if session.get('user_id') %}
    Logged in as: {{ session.get('first_name') }}
{% endif %}

{% if session.get('user_type') == 'customer' %}
    <!-- Customer-specific content -->
{% elif session.get('user_type') == 'manager' %}
    <!-- Manager-specific content -->
{% endif %}
```

## Service Integration

### Calling Services (NOT HTTP Requests)

**IMPORTANT**: UI routes call services directly, not via HTTP:

```python
# CORRECT - Direct service call
from ...server.services.flight_service import search_flights

def flights():
    flights = search_flights(date_filter, origin, destination)
    return render_template('customer/search_flights.html', flights=flights)

# WRONG - HTTP request to own API
# import requests
# response = requests.get('http://localhost:5000/api/flights')
```

### Available Services

- `auth_service`: `login_user()`, `register_customer()`
- `flight_service`: `search_flights()`, `get_flight_details()`
- `booking_service`: `create_booking()`
- `order_service`: `get_user_orders()`, `get_order_details()`, `cancel_order()`
- `report_service`: `get_occupancy_report()`, `get_revenue_report()`, etc.

### Error Handling

```python
from ...server.middleware.error_handlers import APIError

try:
    result = some_service_call()
    flash('Success!', 'success')
    return redirect(url_for('customer.dashboard'))
except APIError as e:
    flash(e.message, 'error')
    return render_template('page.html')
```

## CSS Organization

### CSS Variables (in main.css)

```css
:root {
    --primary-blue: #0078D2;
    --spacing-md: 16px;
    --border-radius: 4px;
}

.my-component {
    background-color: var(--primary-blue);
    padding: var(--spacing-md);
    border-radius: var(--border-radius);
}
```

### File Purposes

- **main.css**: Global styles, layout, typography, CSS variables
- **components.css**: Buttons, cards, badges, flash messages, navigation
- **forms.css**: All form styles, input fields, authentication pages
- **tables.css**: Table layouts, reports
- **seat-map.css**: Seat selection interface

### Responsive Design

All CSS includes mobile-friendly breakpoints:

```css
@media (max-width: 768px) {
    .container {
        padding: 0 var(--spacing-sm);
    }
}
```

## Adding New Pages

### Step 1: Create Route

```python
# app/ui/routes/customer.py
@bp.route('/new-page')
@ui_login_required
def new_page():
    # Get data from services
    data = some_service.get_data()

    return render_template('customer/new_page.html', data=data)
```

### Step 2: Create Template

```jinja2
{# app/ui/templates/customer/new_page.html #}
{% extends 'base.html' %}

{% block title %}New Page - FLYTAU{% endblock %}

{% block content %}
<h1>New Page</h1>
<!-- Content here -->
{% endblock %}
```

### Step 3: Add Navigation Link

```jinja2
{# app/ui/templates/components/header.html #}
<a href="{{ url_for('customer.new_page') }}" class="nav-link">New Page</a>
```

## Common Patterns

### Displaying a List

```jinja2
{% if items %}
    {% for item in items %}
    <div class="item-card">
        {{ item.name }}
    </div>
    {% endfor %}
{% else %}
    <p>No items found.</p>
{% endif %}
```

### Form with Pre-filled Data

```jinja2
<input type="text" name="email" value="{{ form_data.email if form_data else '' }}">
```

### Conditional Actions

```jinja2
{% if order.order_status == 'Confirmed' %}
    <form method="POST" action="{{ url_for('customer.cancel_order_route', order_id=order.order_id) }}">
        <button type="submit" class="btn btn-danger">Cancel Order</button>
    </form>
{% endif %}
```

### Confirmation Dialogs

```jinja2
<button onclick="return confirm('Are you sure?')">Delete</button>
```

## Testing the UI

### Manual Testing Steps

1. **Start the server**:
   ```bash
   cd app/server
   python main.py
   ```

2. **Access the UI**:
   ```
   http://localhost:5001/
   ```

3. **Test User Flows**:
   - Register a new customer
   - Login as customer
   - Search flights
   - Book a flight
   - View orders
   - Cancel order
   - Logout
   - Login as manager (ID: 100000001, Password: pass123)
   - Create flight
   - View reports

### Test Credentials

**Managers**:
- ID: `100000001`, Password: `pass123`
- ID: `100000002`, Password: `pass456`

**Customers**:
- Email: `testuser@example.com`, Password: `test123`

## Troubleshooting

### Templates Not Found

Check Flask app configuration in `app/server/__init__.py`:
```python
app = Flask(__name__,
            template_folder='../ui/templates',  # Correct path
            static_folder='../ui/static')
```

### Static Files Not Loading

Verify URL generation:
```jinja2
<link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
```

### Flash Messages Not Showing

Ensure flash_messages component is included in base template:
```jinja2
{% include 'components/flash_messages.html' %}
```

### Session Issues

Check session configuration in `app/server/config.py`:
- `SESSION_FILE_DIR` exists and is writable
- `SECRET_KEY` is set

### Authentication Redirects Not Working

Verify blueprint URL prefixes in `app/server/__init__.py`:
```python
app.register_blueprint(public.bp, url_prefix='')        # Not '/public'
app.register_blueprint(customer.bp, url_prefix='/customer')
app.register_blueprint(manager.bp, url_prefix='/manager')
```

## Best Practices

1. **Always use `url_for()`** for URLs, never hardcode paths
2. **Call services directly**, don't make HTTP requests
3. **Use flash messages** for user feedback
4. **Validate on server-side**, client-side validation not possible (no JavaScript)
5. **Handle errors gracefully** with try/except and flash messages
6. **Keep templates DRY** using includes and macros
7. **Follow CSS variable naming** for consistency
8. **Test on mobile** using browser dev tools
9. **Use semantic HTML** for accessibility
10. **Keep routes focused** - one responsibility per route

## Security Notes

- **CSRF Protection**: Consider adding Flask-WTF for CSRF tokens in production
- **Input Validation**: All form data is validated server-side
- **SQL Injection**: Prevented by parameterized queries in services
- **Session Security**: Sessions are signed and stored server-side
- **Password Storage**: Currently plain text (academic exercise only - NOT production-ready)

## Future Enhancements

Potential improvements:
- Add CSRF protection with Flask-WTF
- Implement client-side interactivity (if JavaScript allowed)
- Add email notifications
- Generate PDF tickets
- Enhanced search filters
- Guest checkout flow
- Mobile-specific layouts
- Accessibility improvements (ARIA labels, keyboard navigation)

## Support

For questions or issues:
1. Check this guide
2. Review the implementation plan in `docs/UI_IMPLEMENTATION_PLAN.md`
3. Examine existing code in `app/ui/` for examples
4. Test with browser developer tools for debugging
