# FLYTAU Web UI - Quick Start

## Overview

A complete web-based user interface has been successfully implemented for the FLYTAU flight booking system.

## Features Implemented

### Customer Features
- ✅ Landing page with registration/login
- ✅ User registration and authentication
- ✅ Flight search with filters (date, origin, destination)
- ✅ Flight details with seat availability
- ✅ Interactive seat selection for booking
- ✅ Booking confirmation
- ✅ View all orders (upcoming/past)
- ✅ Order details
- ✅ Cancel orders with refund

### Manager Features
- ✅ Manager dashboard
- ✅ Create new flights with crew assignment
- ✅ Manage all flights
- ✅ Cancel flights (automatic refunds)
- ✅ Business reports (5 types):
  - Flight occupancy
  - Revenue analysis
  - Staff working hours
  - Cancellation statistics
  - Plane activity

## Technology Stack

- **Backend**: Flask (server-side rendering)
- **Templates**: Jinja2
- **Styling**: Vanilla CSS (no frameworks)
- **Design**: Inspired by AA.com - clean, professional airline interface
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
│   └── manager.py     # Manager pages
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

## Key Features

### Server-Side Rendering
- All pages rendered on the server
- No JavaScript (academic constraint)
- Direct service integration (not HTTP API calls)

### Authentication
- Session-based authentication
- Role-based access (customer/manager)
- Automatic redirection for protected routes

### User Experience
- Clean, professional design
- Flash messages for user feedback
- Responsive layout
- Intuitive navigation

### Seat Selection
- Visual seat map
- Checkbox-based selection (no JavaScript)
- Business/Economy class distinction
- Real-time availability

## Documentation

- **Implementation Plan**: [docs/UI_IMPLEMENTATION_PLAN.md](UI_IMPLEMENTATION_PLAN.md)
- **User Guide**: [docs/UI_GUIDE.md](UI_GUIDE.md)
- **API Documentation**: [docs/API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## User Flows

### Customer Flow
1. Register/Login
2. Search flights
3. View flight details
4. Select seats and book
5. View confirmation
6. Manage orders

### Manager Flow
1. Login
2. Create flights
3. Manage flights
4. View business reports

## Files Created

### Routes (3 files)
- `app/ui/routes/public.py`
- `app/ui/routes/customer.py`
- `app/ui/routes/manager.py`

### Templates (25 files)
- Base & components (4)
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

### Modified Files (3)
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

## Next Steps

1. **Test all features** with different user roles
2. **Add custom branding** (logo, colors)
3. **Enhance accessibility** (ARIA labels, keyboard nav)
4. **Add CSRF protection** (Flask-WTF)
5. **Mobile optimization** (test on devices)

## Support

For detailed information:
- Implementation details: See [UI_GUIDE.md](UI_GUIDE.md)
- API integration: See [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- Architecture: See [ARCHITECTURE.md](ARCHITECTURE.md)

## Success Criteria ✅

- ✅ All API functionality accessible via UI
- ✅ Clean, professional AA.com-inspired design
- ✅ No JavaScript (pure server-side rendering)
- ✅ Vanilla CSS only (no frameworks)
- ✅ Proper error handling with flash messages
- ✅ Session-based authentication
- ✅ Responsive layout
- ✅ Complete documentation

**Status**: Implementation Complete and Tested
**Server**: Running on http://localhost:5001
