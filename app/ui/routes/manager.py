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

            # Call the admin flight creation logic
            from ...server.routes.admin_flights import create_flight as create_flight_api

            # We'll manually call the database operations
            conn = get_db_connection()
            cursor = conn.cursor()

            try:
                # Insert flight
                cursor.execute("""
                    INSERT INTO Flight (OriginAirport, DestinationAirport, PlaneID,
                                      DepartureDateTime, FlightStatus, ManagerID)
                    VALUES (%s, %s, %s, %s, 'Scheduled', %s)
                """, (
                    flight_data['origin_airport'],
                    flight_data['destination_airport'],
                    flight_data['plane_id'],
                    flight_data['departure_datetime'],
                    flight_data['manager_id']
                ))

                flight_id = cursor.lastrowid

                # Assign pilots
                for pilot_id in flight_data['pilot_ids']:
                    if pilot_id:
                        cursor.execute("""
                            INSERT INTO FlightPilotAssignment (FlightID, PilotID)
                            VALUES (%s, %s)
                        """, (flight_id, pilot_id))

                # Assign attendants
                for attendant_id in flight_data['attendant_ids']:
                    if attendant_id:
                        cursor.execute("""
                            INSERT INTO FlightAttendantAssignment (FlightID, AttendantID)
                            VALUES (%s, %s)
                        """, (flight_id, attendant_id))

                conn.commit()
                flash(f'Flight {flight_id} created successfully!', 'success')
                return redirect(url_for('manager.manage_flights'))

            except Exception as e:
                conn.rollback()
                raise APIError(f'Failed to create flight: {str(e)}', 500)
            finally:
                cursor.close()
                conn.close()

        except APIError as e:
            flash(e.message, 'error')

    # GET: Show form with available planes and crew
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get available planes
        cursor.execute("SELECT PlaneID, Manufacturer, Model FROM Plane WHERE PlaneStatus = 'Active'")
        planes = cursor.fetchall()

        # Get available pilots
        cursor.execute("SELECT PilotID, FirstName, LastName FROM Pilot")
        pilots = cursor.fetchall()

        # Get available attendants
        cursor.execute("SELECT AttendantID, FirstName, LastName FROM FlightAttendant")
        attendants = cursor.fetchall()

        cursor.close()
        conn.close()

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
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update flight status
        cursor.execute("""
            UPDATE Flight
            SET FlightStatus = 'Cancelled'
            WHERE FlightID = %s
        """, (flight_id,))

        # Get affected orders
        cursor.execute("""
            SELECT OrderID, CustomerEmail, TotalPayment
            FROM FlightOrder
            WHERE FlightID = %s AND OrderStatus = 'Confirmed'
        """, (flight_id,))

        orders = cursor.fetchall()

        # Process refunds
        for order_id, customer_email, total_payment in orders:
            # Update order status
            cursor.execute("""
                UPDATE FlightOrder
                SET OrderStatus = 'Cancelled'
                WHERE OrderID = %s
            """, (order_id,))

            # Refund to registered customers
            cursor.execute("""
                UPDATE RegisteredCustomer
                SET Balance = Balance + %s
                WHERE Email = %s
            """, (total_payment, customer_email))

        conn.commit()
        cursor.close()
        conn.close()

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
                             report_type='Flight Occupancy',
                             report_data=report_data,
                             columns=['Flight ID', 'Route', 'Date', 'Capacity', 'Booked', 'Occupancy %'])
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
                             columns=['Period', 'Total Revenue', 'Orders', 'Avg Order Value'])
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
                             report_type='Staff Working Hours',
                             report_data=report_data,
                             columns=['Staff ID', 'Name', 'Role', 'Total Hours', 'Flights'])
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
                             report_type='Cancellation Statistics',
                             report_data=report_data,
                             columns=['Period', 'Total Cancellations', 'Customer Initiated', 'Flight Cancelled', 'Refund Amount'])
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
                             report_type='Plane Activity',
                             report_data=report_data,
                             columns=['Plane ID', 'Model', 'Total Flights', 'Total Hours', 'Utilization %'])
    except APIError as e:
        flash(e.message, 'error')
        return redirect(url_for('manager.reports'))
