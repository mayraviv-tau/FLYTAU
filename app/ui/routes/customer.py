"""
Customer routes for FLYTAU web UI.
Handles flight search, booking, and order management.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.server.middleware.auth import ui_login_required, get_current_user
from app.server.services.flight_service import search_flights, get_flight_details
from app.server.services.booking_service import create_booking
from app.server.services.order_service import get_user_orders, get_order_details, cancel_order
from app.server.middleware.error_handlers import APIError

bp = Blueprint('customer', __name__)


@bp.route('/dashboard')
@ui_login_required
def dashboard():
    """Customer dashboard with search form and upcoming orders."""
    current_user = get_current_user()

    if current_user['user_type'] != 'customer':
        flash('Access denied', 'error')
        return redirect(url_for('manager.dashboard'))

    # Get upcoming orders
    try:
        upcoming_orders = get_user_orders(current_user['user_id'], 'future')
    except:
        upcoming_orders = []

    return render_template('customer/dashboard.html',
                         user=current_user,
                         upcoming_orders=upcoming_orders)


@bp.route('/flights')
@ui_login_required
def flights():
    """Search flights based on query parameters."""
    date_filter = request.args.get('date')
    origin = request.args.get('origin')
    destination = request.args.get('destination')

    try:
        # Call internal service
        flights_list = search_flights(date_filter, origin, destination)
    except APIError as e:
        flash(e.message, 'error')
        flights_list = []

    return render_template('customer/search_flights.html',
                         flights=flights_list,
                         search_params={
                             'date': date_filter,
                             'origin': origin,
                             'destination': destination
                         })


@bp.route('/flights/<int:flight_id>')
@ui_login_required
def flight_details(flight_id):
    """Display flight details with seat map."""
    try:
        flight = get_flight_details(flight_id)
        return render_template('customer/flight_details.html', flight=flight)
    except APIError as e:
        flash(e.message, 'error')
        return redirect(url_for('customer.dashboard'))


@bp.route('/book/<int:flight_id>', methods=['GET', 'POST'])
@ui_login_required
def book_flight(flight_id):
    """Display booking form and handle submission."""
    current_user = get_current_user()

    if request.method == 'POST':
        try:
            # Parse selected seats from form
            selected_seats = request.form.getlist('selected_seats')

            if not selected_seats:
                flash('Please select at least one seat.', 'error')
                return redirect(url_for('customer.book_flight', flight_id=flight_id))

            # Get flight details to get prices
            flight = get_flight_details(flight_id)

            # Build tickets list
            tickets = []
            for seat_num in selected_seats:
                seat_info = flight['seat_map'].get(seat_num)
                if seat_info and seat_info['status'] == 'Available':
                    tickets.append({
                        'class_type': seat_info['class_type'],
                        'seat_number': seat_num,
                        'price': float(seat_info['price'])
                    })

            if not tickets:
                flash('Selected seats are not available.', 'error')
                return redirect(url_for('customer.book_flight', flight_id=flight_id))

            # Create booking
            order = create_booking(
                customer_email=current_user['user_id'],
                flight_id=flight_id,
                tickets=tickets
            )

            flash('Booking created successfully!', 'success')
            return redirect(url_for('customer.booking_confirmation',
                                  order_id=order['order_id']))

        except APIError as e:
            flash(e.message, 'error')

    # GET: Show booking form with flight details
    try:
        flight = get_flight_details(flight_id)
        return render_template('customer/booking_form.html', flight=flight)
    except APIError as e:
        flash(e.message, 'error')
        return redirect(url_for('customer.dashboard'))


@bp.route('/booking-confirmation/<int:order_id>')
@ui_login_required
def booking_confirmation(order_id):
    """Booking confirmation page."""
    current_user = get_current_user()

    try:
        order = get_order_details(current_user['user_id'], order_id)
        return render_template('customer/booking_confirmation.html', order=order)
    except APIError as e:
        flash(e.message, 'error')
        return redirect(url_for('customer.orders'))


@bp.route('/orders')
@ui_login_required
def orders():
    """View all orders with filter (future/history)."""
    current_user = get_current_user()
    filter_type = request.args.get('filter', 'future')

    try:
        orders_list = get_user_orders(current_user['user_id'], filter_type)
    except APIError as e:
        flash(e.message, 'error')
        orders_list = []

    return render_template('customer/my_orders.html',
                         orders=orders_list,
                         filter_type=filter_type)


@bp.route('/orders/<int:order_id>')
@ui_login_required
def order_details(order_id):
    """View single order details."""
    current_user = get_current_user()

    try:
        order = get_order_details(current_user['user_id'], order_id)
        return render_template('customer/order_details.html', order=order)
    except APIError as e:
        flash(e.message, 'error')
        return redirect(url_for('customer.orders'))


@bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
@ui_login_required
def cancel_order_route(order_id):
    """Cancel order."""
    current_user = get_current_user()

    try:
        result = cancel_order(current_user['user_id'], order_id)
        flash(f'Order cancelled successfully. Refund: ${result["refund_amount"]:.2f}', 'success')
    except APIError as e:
        flash(e.message, 'error')

    return redirect(url_for('customer.orders'))
