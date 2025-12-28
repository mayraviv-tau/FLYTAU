"""
Manager routes for FLYTAU web UI.
Handles flight management and business reports.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.server.middleware.auth import ui_manager_required, get_current_user
from app.server.services.flight_service import search_flights
from app.server.services.report_service import (
    get_occupancy_report,
    get_revenue_report,
    get_staff_hours_report,
    get_cancellations_report,
    get_plane_activity_report
)
from app.server.middleware.error_handlers import APIError
from app.server.db.connection import get_db_connection

bp = Blueprint('manager', __name__)


@bp.route('/dashboard')
@ui_manager_required
def dashboard():
    """Manager dashboard."""
    current_user = get_current_user()
    return render_template('manager/dashboard.html', user=current_user)


@bp.route('/flights/create', methods=['GET', 'POST'])
@ui_manager_required
def create_flight():
    """Create new flight."""
    if request.method == 'POST':
        try:
            # Extract form data
            flight_data = {
                'origin_airport': request.form.get('origin_airport'),
                'destination_airport': request.form.get('destination_airport'),
                'plane_id': request.form.get('plane_id'),
                'departure_datetime': request.form.get('departure_datetime'),
                'manager_id': get_current_user()['user_id'],
                'pilot_ids': request.form.getlist('pilot_ids'),
                'attendant_ids': request.form.getlist('attendant_ids')
            }

            # We'll manually call the database operations
            with get_db_connection() as conn:
                cursor = conn.cursor(dictionary=True)

                try:
                    # 1. Get flight duration from FlightLine
                    cursor.execute("""
                        SELECT flight_duration FROM FlightLine
                        WHERE origin_airport = %s AND destination_airport = %s
                    """, (flight_data['origin_airport'], flight_data['destination_airport']))

                    flight_line = cursor.fetchone()
                    if not flight_line:
                        raise APIError(f"No flight route exists from {flight_data['origin_airport']} to {flight_data['destination_airport']}", 400)

                    flight_duration = float(flight_line['flight_duration'])
                    is_long_haul = flight_duration > 6

                    # 2. Get plane details and validate compatibility
                    cursor.execute("""
                        SELECT plane_id, size_category FROM Plane WHERE plane_id = %s
                    """, (flight_data['plane_id'],))

                    plane = cursor.fetchone()
                    if not plane:
                        raise APIError(f"Aircraft {flight_data['plane_id']} not found", 400)

                    # Validate: Small aircraft can only do short flights
                    if plane['size_category'] == 'Small' and is_long_haul:
                        raise APIError(f"Small aircraft cannot be assigned to long-haul flights (>{flight_duration}h)", 400)

                    # 3. Determine required crew counts based on aircraft size
                    if plane['size_category'] == 'Large':
                        required_pilots = 3
                        required_attendants = 6
                    else:  # Small
                        required_pilots = 2
                        required_attendants = 3

                    # 4. Validate crew counts
                    pilot_count = len([p for p in flight_data['pilot_ids'] if p])
                    attendant_count = len([a for a in flight_data['attendant_ids'] if a])

                    if pilot_count < required_pilots:
                        raise APIError(f"Insufficient pilots: {pilot_count}/{required_pilots} required for {plane['size_category']} aircraft", 400)

                    if attendant_count < required_attendants:
                        raise APIError(f"Insufficient flight attendants: {attendant_count}/{required_attendants} required for {plane['size_category']} aircraft", 400)

                    # 5. Validate pilot qualifications for long-haul flights
                    if is_long_haul and flight_data['pilot_ids']:
                        placeholders = ','.join(['%s'] * len([p for p in flight_data['pilot_ids'] if p]))
                        cursor.execute(f"""
                            SELECT id_number FROM Pilot
                            WHERE id_number IN ({placeholders})
                            AND is_long_haul_qualified = FALSE
                        """, tuple(p for p in flight_data['pilot_ids'] if p))

                        unqualified_pilots = cursor.fetchall()
                        if unqualified_pilots:
                            unqualified_ids = [p['id_number'] for p in unqualified_pilots]
                            raise APIError(f"Pilots {', '.join(unqualified_ids)} are not qualified for long-haul flights", 400)

                    # 6. Validate flight attendant qualifications for long-haul flights
                    if is_long_haul and flight_data['attendant_ids']:
                        placeholders = ','.join(['%s'] * len([a for a in flight_data['attendant_ids'] if a]))
                        cursor.execute(f"""
                            SELECT id_number FROM FlightAttendant
                            WHERE id_number IN ({placeholders})
                            AND is_long_haul_qualified = FALSE
                        """, tuple(a for a in flight_data['attendant_ids'] if a))

                        unqualified_attendants = cursor.fetchall()
                        if unqualified_attendants:
                            unqualified_ids = [a['id_number'] for a in unqualified_attendants]
                            raise APIError(f"Flight attendants {', '.join(unqualified_ids)} are not qualified for long-haul flights", 400)

                    # 7. Insert flight
                    cursor.execute("""
                        INSERT INTO Flight (origin_airport, destination_airport, plane_id,
                                          departure_datetime, status, manager_id)
                        VALUES (%s, %s, %s, %s, 'Active', %s)
                    """, (
                        flight_data['origin_airport'],
                        flight_data['destination_airport'],
                        flight_data['plane_id'],
                        flight_data['departure_datetime'],
                        flight_data['manager_id']
                    ))

                    flight_id = cursor.lastrowid

                    # 8. Assign pilots
                    for pilot_id in flight_data['pilot_ids']:
                        if pilot_id:
                            cursor.execute("""
                                INSERT INTO FlightPilotAssignment (flight_id, pilot_id)
                                VALUES (%s, %s)
                            """, (flight_id, pilot_id))

                    # 9. Assign attendants
                    for attendant_id in flight_data['attendant_ids']:
                        if attendant_id:
                            cursor.execute("""
                                INSERT INTO FlightAttendantAssignment (flight_id, flight_attendant_id)
                                VALUES (%s, %s)
                            """, (flight_id, attendant_id))

                    conn.commit()
                    flash(f'Flight {flight_id} created successfully! Duration: {flight_duration}h ({("Long-haul" if is_long_haul else "Short-haul")})', 'success')
                    return redirect(url_for('manager.manage_flights'))

                except Exception as e:
                    conn.rollback()
                    if isinstance(e, APIError):
                        raise
                    raise APIError(f'Failed to create flight: {str(e)}', 500)
                finally:
                    cursor.close()

        except APIError as e:
            flash(e.message, 'error')

    # GET: Show form with available planes and crew
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)

            # Get available planes
            cursor.execute("SELECT plane_id, manufacturer, size_category FROM Plane")
            planes = cursor.fetchall()

            # Get available pilots with qualification status
            cursor.execute("SELECT id_number, first_name_hebrew, last_name_hebrew, is_long_haul_qualified FROM Pilot")
            pilots = cursor.fetchall()

            # Get available attendants with qualification status
            cursor.execute("SELECT id_number, first_name_hebrew, last_name_hebrew, is_long_haul_qualified FROM FlightAttendant")
            attendants = cursor.fetchall()

            cursor.close()

        return render_template('manager/create_flight.html',
                             planes=planes,
                             pilots=pilots,
                             attendants=attendants)
    except Exception as e:
        flash(f'Error loading form: {str(e)}', 'error')
        return redirect(url_for('manager.dashboard'))


@bp.route('/flights')
@ui_manager_required
def manage_flights():
    """List all flights with management options."""
    try:
        # Get all flights
        flights_list = search_flights(None, None, None)
        return render_template('manager/manage_flights.html', flights=flights_list)
    except APIError as e:
        flash(e.message, 'error')
        return render_template('manager/manage_flights.html', flights=[])


@bp.route('/flights/<int:flight_id>/cancel', methods=['POST'])
@ui_manager_required
def cancel_flight(flight_id):
    """Cancel flight."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Update flight status
            cursor.execute("""
                UPDATE Flight
                SET status = 'Canceled'
                WHERE flight_id = %s
            """, (flight_id,))

            # Get affected orders
            cursor.execute("""
                SELECT order_id, customer_email, total_payment
                FROM FlightOrder
                WHERE flight_id = %s AND order_status = 'Active'
            """, (flight_id,))

            orders = cursor.fetchall()

            # Process refunds
            for order_id, customer_email, total_payment in orders:
                # Update order status
                cursor.execute("""
                    UPDATE FlightOrder
                    SET order_status = 'Canceled_By_Company'
                    WHERE order_id = %s
                """, (order_id,))

                # Refund to registered customers
                cursor.execute("""
                    UPDATE RegisteredCustomer
                    SET balance = balance + %s
                    WHERE email = %s
                """, (total_payment, customer_email))

            conn.commit()
            cursor.close()

            flash(f'Flight {flight_id} cancelled. {len(orders)} orders refunded.', 'success')
    except Exception as e:
        flash(f'Error cancelling flight: {str(e)}', 'error')

    return redirect(url_for('manager.manage_flights'))


@bp.route('/reports')
@ui_manager_required
def reports():
    """Reports dashboard - list of available reports."""
    return render_template('manager/reports.html')


@bp.route('/reports/occupancy')
@ui_manager_required
def report_occupancy():
    """Display occupancy report."""
    try:
        report_data = get_occupancy_report()
        return render_template('manager/report_details.html',
                             report_type='Average Flight Occupancy',
                             report_data=report_data,
                             columns=['Average System Occupancy (%)'])
    except APIError as e:
        flash(e.message, 'error')
        return redirect(url_for('manager.reports'))


@bp.route('/reports/revenue')
@ui_manager_required
def report_revenue():
    """Display revenue report."""
    try:
        report_data = get_revenue_report()
        return render_template('manager/report_details.html',
                             report_type='Revenue Analysis',
                             report_data=report_data,
                             columns=['Size Category', 'Manufacturer', 'Class Type', 'Total Revenue', 'Tickets Sold Count'])
    except APIError as e:
        flash(e.message, 'error')
        return redirect(url_for('manager.reports'))


@bp.route('/reports/staff-hours')
@ui_manager_required
def report_staff_hours():
    """Display staff hours report."""
    try:
        report_data = get_staff_hours_report()
        return render_template('manager/report_details.html',
                             report_type='Staff Accumulated Flight Hours',
                             report_data=report_data,
                             columns=['Role', 'ID Number', 'First Name', 'Last Name', 'Long Haul Hours', 'Short Haul Hours', 'Total Hours'])
    except APIError as e:
        flash(e.message, 'error')
        return redirect(url_for('manager.reports'))


@bp.route('/reports/cancellations')
@ui_manager_required
def report_cancellations():
    """Display cancellations report."""
    try:
        report_data = get_cancellations_report()
        return render_template('manager/report_details.html',
                             report_type='Monthly Cancellation Rates',
                             report_data=report_data,
                             columns=['Month/Year', 'Total Orders', 'Canceled Orders', 'Cancellation Rate (%)'])
    except APIError as e:
        flash(e.message, 'error')
        return redirect(url_for('manager.reports'))


@bp.route('/reports/plane-activity')
@ui_manager_required
def report_plane_activity():
    """Display plane activity report."""
    try:
        report_data = get_plane_activity_report()
        return render_template('manager/report_details.html',
                             report_type='Monthly Plane Activity Summary',
                             report_data=report_data,
                             columns=['Month/Year', 'Plane ID', 'Flights Performed', 'Flights Canceled', 'Utilization (%)', 'Dominant Route'])
    except APIError as e:
        flash(e.message, 'error')
        return redirect(url_for('manager.reports'))
