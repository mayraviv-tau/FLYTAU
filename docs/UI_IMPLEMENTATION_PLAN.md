# FLYTAU Web UI Implementation Plan

## Overview
Create a complete web UI for the FLYTAU flight booking system using server-side rendering (HTML/Jinja2, vanilla CSS, no JavaScript) integrated into the existing Flask REST API server.

## Technology Stack
- **HTML Templates**: Jinja2 templating engine
- **CSS**: Vanilla CSS only (no frameworks)
- **Backend**: Flask server-side rendering calling internal services
- **Design Inspiration**: AA.com flight booking interface (clean, professional)

## Architecture Decisions

### Integration Approach
- **Add UI to existing server** (not separate app)
- **Server-side rendering** with internal service calls (not HTTP requests)
- **Dual response types**: API routes return JSON, UI routes return HTML
- **Shared authentication**: Reuse existing session-based auth

### Directory Structure
```
app/ui/
├── __init__.py
├── routes/
│   ├── __init__.py
│   ├── public.py      # Landing, login, register
│   ├── customer.py    # Flight search, booking, orders
│   └── manager.py     # Admin dashboard, flights, reports
├── templates/
│   ├── base.html
│   ├── components/    # Reusable parts (header, footer, flash_messages, flight_card)
│   ├── public/        # Landing, login, register
│   ├── customer/      # Dashboard, search, booking, orders
│   ├── manager/       # Dashboard, create_flight, reports
│   └── errors/        # 404, 403, 500
└── static/
    ├── css/           # main.css, components.css, forms.css, tables.css, seat-map.css
    └── images/        # logo.png, favicon.ico
```

## Implementation Steps

### 1. Flask Integration
**File**: `app/server/__init__.py`

Modify `create_app()`:
- Add `template_folder='../ui/templates'` and `static_folder='../ui/static'` to Flask initialization
- Import and register UI blueprints in `register_blueprints()`

### 2. Enhanced Error Handlers
**File**: `app/server/middleware/error_handlers.py`

Update `register_error_handlers()`:
- Add `wants_json()` helper to detect request type (check if path starts with '/api/')
- Modify error handlers to return HTML templates for UI requests, JSON for API requests
- Create `render_template()` responses for APIError, 404, 403, 500

### 3. UI-Aware Auth Decorators
**File**: `app/server/middleware/auth.py`

Add new decorators:
- `ui_login_required`: Redirect to login page instead of raising 401
- `ui_manager_required`: Redirect appropriately instead of raising 403
- Store `session['next_url']` for post-login redirect

### 4. Create UI Blueprint Package
**New Files**:
- `app/ui/__init__.py` - Package initialization
- `app/ui/routes/__init__.py` - Routes package

### 5. Public Routes
**File**: `app/ui/routes/public.py`

Routes:
- `GET /` - Landing page (redirect if logged in)
- `GET /login` - Login form (dual: customer email or manager ID)
- `POST /login` - Process login, set session, redirect to dashboard
- `GET /register` - Registration form (customer only)
- `POST /register` - Process registration via `auth_service.register_customer()`
- `POST /logout` - Clear session, redirect to landing

Services used: `auth_service.login_user()`, `auth_service.register_customer()`

### 6. Customer Routes
**File**: `app/ui/routes/customer.py`

Routes:
- `GET /customer/dashboard` - Search form + upcoming orders
- `GET /customer/flights` - Search results (params: date, origin, destination)
- `GET /customer/flights/<id>` - Flight details with seat map
- `GET /customer/book/<flight_id>` - Booking form with seat selection
- `POST /customer/book/<flight_id>` - Process booking
- `GET /customer/booking-confirmation/<order_id>` - Confirmation page
- `GET /customer/orders` - All orders (tabs: future/history via ?filter=)
- `GET /customer/orders/<id>` - Order details
- `POST /customer/orders/<id>/cancel` - Cancel order

Services used: `flight_service`, `booking_service`, `order_service`

### 7. Manager Routes
**File**: `app/ui/routes/manager.py`

Routes:
- `GET /manager/dashboard` - Manager home
- `GET /manager/flights/create` - Flight creation form
- `POST /manager/flights/create` - Process flight creation
- `GET /manager/flights` - List all flights
- `POST /manager/flights/<id>/cancel` - Cancel flight
- `GET /manager/reports` - Reports dashboard (5 types)
- `GET /manager/reports/<type>` - Display specific report (occupancy, revenue, staff-hours, cancellations, plane-activity)

Services used: Internal admin services, `report_service`

### 8. Base Template
**File**: `app/ui/templates/base.html`

Structure:
- HTML5 doctype, meta tags, CSS links
- Include header component
- Main content area with flash messages
- Include footer component
- Blocks: `title`, `extra_css`, `content`

### 9. Components
**Files**: `app/ui/templates/components/`

- **header.html**: Logo, navigation (different for customer/manager), user menu, logout
- **footer.html**: Simple footer with copyright
- **flash_messages.html**: Display Flask flash messages with categories (success, error, warning)
- **flight_card.html**: Jinja2 macro for rendering flight cards

### 10. Public Templates
**Files**: `app/ui/templates/public/`

- **landing.html**: Welcome page with login/register buttons
- **login.html**: Login form with user type toggle (customer/manager)
- **register.html**: Customer registration form (email, password, name, birth_date, passport, phone)

### 11. Customer Templates
**Files**: `app/ui/templates/customer/`

- **dashboard.html**: Search form + upcoming orders cards
- **search_flights.html**: Flight results list (flight cards)
- **flight_details.html**: Detailed flight info with seat map
- **booking_form.html**: Seat selection interface (checkboxes or multi-step)
- **booking_confirmation.html**: Success message with order details
- **my_orders.html**: Orders list with filter tabs (future/history)
- **order_details.html**: Single order with tickets, cancel button

### 12. Manager Templates
**Files**: `app/ui/templates/manager/`

- **dashboard.html**: Manager home with quick stats
- **create_flight.html**: Complex form (origin, destination, plane, crew selection)
- **manage_flights.html**: Flights table with cancel actions
- **reports.html**: 5 report type buttons
- **report_details.html**: Reusable template for all report types (tables)

### 13. Error Templates
**Files**: `app/ui/templates/errors/`

- **404.html**: Not found page
- **403.html**: Forbidden/access denied
- **500.html**: Server error

### 14. CSS Foundation
**File**: `app/ui/static/css/main.css`

CSS Variables:
- Colors: Primary blue (#0078D2), grays, semantic colors (success, error, warning)
- Typography: Font family, sizes
- Spacing: xs, sm, md, lg, xl

Global styles:
- Box sizing, body defaults
- Container (max-width 1200px, centered)
- Header, main-content, footer layouts
- Responsive breakpoints

### 15. Component Styles
**File**: `app/ui/static/css/components.css`

Styles for:
- Buttons (btn, btn-primary, btn-secondary, btn-danger)
- Flight cards with hover effects
- Navigation menu
- Flash messages (color-coded by type)
- User menu

### 16. Form Styles
**File**: `app/ui/static/css/forms.css`

Styles for:
- Search form (prominent, shadowed)
- Form rows (grid layout)
- Form groups and labels
- Input fields with focus states
- Validation error display

### 17. Table Styles
**File**: `app/ui/static/css/tables.css`

Styles for:
- Orders tables
- Reports tables
- Responsive table layouts

### 18. Seat Map Styles
**File**: `app/ui/static/css/seat-map.css`

Styles for:
- Seat grid layout
- Seat states (available, occupied, selected)
- Business vs Economy visual distinction
- Aisle spacing

### 19. Static Assets
**Files**: `app/ui/static/images/`

- `logo.png` - FLYTAU logo for header
- `favicon.ico` - Browser favicon

### 20. Documentation
**File**: `docs/UI_GUIDE.md`

Create comprehensive guide:
- UI architecture overview
- How to add new pages
- Template inheritance patterns
- CSS organization
- Form handling patterns
- Common UI patterns (flash messages, error handling)

## Key Implementation Patterns

### Service Integration
```python
# CORRECT: Direct service call
from ...server.services.flight_service import search_flights
flights = search_flights(date_filter, origin, destination)

# WRONG: HTTP request
# requests.get('http://localhost:5000/api/flights')
```

### Form Handling
```python
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            # Validate and process
            user = login_user(email, password, user_type)
            # Set session
            session['user_id'] = user['user_id']
            flash('Login successful!', 'success')
            return redirect(url_for('customer.dashboard'))
        except APIError as e:
            flash(e.message, 'error')
    return render_template('public/login.html')
```

### Seat Selection (No JavaScript)
**Approach**: Single form with checkboxes for all available seats
- User checks desired seats
- Submit form with all selections
- Server validates seat availability
- Process booking or show errors

## User Flows

### Customer Journey
```
Landing → Register → Login → Dashboard → Search Flights →
Select Flight → View Details → Book (Select Seats) →
Confirmation → My Orders → View Details / Cancel
```

### Manager Journey
```
Landing → Login (Manager) → Manager Dashboard →
Create Flight / Manage Flights / View Reports
```

## Files Summary

### New Files (37)
**Core (5)**: UI package, routes modules
**Templates (25)**: Base, components, public, customer, manager, errors
**CSS (5)**: main, components, forms, tables, seat-map
**Images (2)**: logo, favicon

### Modified Files (3)
- `app/server/__init__.py` - Flask app factory
- `app/server/middleware/error_handlers.py` - Dual response types
- `app/server/middleware/auth.py` - UI decorators

## Critical Files Priority

1. **app/server/__init__.py** - Integration point
2. **app/ui/routes/public.py** - Authentication foundation
3. **app/ui/templates/base.html** - Master template
4. **app/ui/routes/customer.py** - Core booking logic
5. **app/ui/static/css/main.css** - Design system

## Testing Checklist

- [ ] Customer registration and login
- [ ] Manager login
- [ ] Flight search with filters
- [ ] Flight details and seat map display
- [ ] Complete booking flow
- [ ] Order viewing (future/history)
- [ ] Order cancellation
- [ ] Manager flight creation
- [ ] Manager flight cancellation
- [ ] All 5 report types
- [ ] Error pages (404, 403, 500)
- [ ] Flash messages
- [ ] Session persistence
- [ ] Responsive design (desktop, tablet, mobile)

## Success Criteria

- ✅ All existing API functionality accessible via UI
- ✅ Clean, professional design inspired by AA.com
- ✅ No JavaScript (pure server-side rendering)
- ✅ Vanilla CSS only (no frameworks)
- ✅ Proper error handling with user-friendly messages
- ✅ Session-based authentication working
- ✅ Responsive layout
- ✅ Complete documentation
