"""
Flight routes
Handles flight search, listing, and management
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import execute_query, db_transaction
from utils.auth import is_logged_in, is_manager, get_current_manager_id
from datetime import datetime, timedelta

bp = Blueprint('flights', __name__)

def update_expired_flights():
    """Update status of flights that have passed to 'Landed' and their orders to 'Completed'"""
    try:
        # Update flights to 'Landed'
        flight_query = """
            UPDATE Flight
            SET status = 'Landed'
            WHERE status IN ('Active', 'Full')
            AND departure_datetime < NOW()
        """
        execute_query(flight_query, commit=True)

        # Update orders to 'Completed' for landed flights
        order_query = """
            UPDATE FlightOrder fo
            JOIN Flight f ON fo.flight_id = f.flight_id
            SET fo.order_status = 'Completed'
            WHERE fo.order_status = 'Active'
            AND f.status = 'Landed'
        """
        execute_query(order_query, commit=True)
    except:
        pass  # Ignore errors

@bp.route('/search', methods=['GET', 'POST'])
def search():
    """Search flights by date, origin, and destination"""
    update_expired_flights()
    if request.method == 'POST':
        origin = request.form.get('origin_airport')
        destination = request.form.get('destination_airport')
        departure_date = request.form.get('departure_date')

        query = """
            SELECT f.flight_id, f.origin_airport, f.destination_airport,
                   f.departure_datetime, f.status, f.plane_id,
                   p.manufacturer, p.size_category,
                   fl.flight_duration
            FROM Flight f
            JOIN Plane p ON f.plane_id = p.plane_id
            JOIN FlightLine fl ON f.origin_airport = fl.origin_airport
                              AND f.destination_airport = fl.destination_airport
            WHERE f.status = 'Active'
              AND f.departure_datetime > NOW()
        """
        params = []

        if origin:
            query += " AND f.origin_airport = %s"
            params.append(origin)

        if destination:
            query += " AND f.destination_airport = %s"
            params.append(destination)

        if departure_date:
            query += " AND DATE(f.departure_datetime) = %s"
            params.append(departure_date)

        query += " ORDER BY f.departure_datetime ASC"

        flights = execute_query(query, tuple(params) if params else None, fetch_all=True)

        # Get available airports for dropdown
        airports_query = """
            SELECT DISTINCT origin_airport AS airport FROM FlightLine
            UNION
            SELECT DISTINCT destination_airport AS airport FROM FlightLine
            ORDER BY airport
        """
        airports = execute_query(airports_query, fetch_all=True)

        return render_template('flights/search.html', flights=flights, airports=airports,
                             origin=origin, destination=destination, departure_date=departure_date)

    # GET request - show search form
    airports_query = """
        SELECT DISTINCT origin_airport AS airport FROM FlightLine
        UNION
        SELECT DISTINCT destination_airport AS airport FROM FlightLine
        ORDER BY airport
    """
    airports = execute_query(airports_query, fetch_all=True)

    return render_template('flights/search.html', airports=airports, flights=[])

@bp.route('/board')
def board():
    """Show all available flights (flight board)"""
    update_expired_flights()

    query = """
        SELECT f.flight_id, f.origin_airport, f.destination_airport,
               f.departure_datetime, f.status, f.plane_id,
               p.manufacturer, p.size_category,
               fl.flight_duration
        FROM Flight f
        JOIN Plane p ON f.plane_id = p.plane_id
        JOIN FlightLine fl ON f.origin_airport = fl.origin_airport
                          AND f.destination_airport = fl.destination_airport
        WHERE f.status = 'Active'
          AND f.departure_datetime > NOW()
        ORDER BY f.departure_datetime ASC
    """
    flights = execute_query(query, fetch_all=True)

    return render_template('flights/board.html', flights=flights)

@bp.route('/<int:flight_id>/seats', methods=['GET'])
def seats(flight_id):
    """Show available seats for a flight"""
    # Get flight details
    flight_query = """
        SELECT f.*, p.manufacturer, p.size_category,
               fl.flight_duration
        FROM Flight f
        JOIN Plane p ON f.plane_id = p.plane_id
        JOIN FlightLine fl ON f.origin_airport = fl.origin_airport
                          AND f.destination_airport = fl.destination_airport
        WHERE f.flight_id = %s
    """
    flight = execute_query(flight_query, (flight_id,), fetch_one=True)

    if not flight:
        flash('טיסה לא נמצאה', 'error')
        return redirect(url_for('flights.search'))

    # Get all seats for the plane
    seats_query = """
        SELECT s.plane_id, s.class_type, s.seat_number,
               pc.rows_count, pc.cols_count
        FROM Seat s
        JOIN PlaneClass pc ON s.plane_id = pc.plane_id AND s.class_type = pc.class_type
        WHERE s.plane_id = %s
        ORDER BY s.class_type, s.seat_number
    """
    all_seats = execute_query(seats_query, (flight['plane_id'],), fetch_all=True)

    # Get occupied seats for this flight
    occupied_query = """
        SELECT t.plane_id, t.class_type, t.seat_number
        FROM Ticket t
        JOIN FlightOrder fo ON t.order_id = fo.order_id
        WHERE fo.flight_id = %s
          AND fo.order_status IN ('Active', 'Completed')
          AND t.plane_id = %s
    """
    occupied_seats = execute_query(occupied_query, (flight_id, flight['plane_id']), fetch_all=True)

    # Create a set of occupied seats for quick lookup
    occupied_set = {(s['plane_id'], s['class_type'], s['seat_number'])
                    for s in occupied_seats}

    # Mark seats as available/occupied
    for seat in all_seats:
        seat_key = (seat['plane_id'], seat['class_type'], seat['seat_number'])
        seat['available'] = seat_key not in occupied_set

    # Group seats by class, filtering out Business for small planes
    seats_by_class = {}
    for seat in all_seats:
        class_type = seat['class_type']
        # Skip Business class for small planes
        if class_type == 'Business' and flight['size_category'] == 'Small':
            continue
        if class_type not in seats_by_class:
            seats_by_class[class_type] = []
        seats_by_class[class_type].append(seat)

    return render_template('flights/seats.html', flight=flight, seats_by_class=seats_by_class)

@bp.route('/list')
def list():
    """List all flights (for managers)"""
    update_expired_flights()
    if not is_manager():
        flash('אין הרשאה לגשת לדף זה', 'error')
        return redirect(url_for('flights.search'))

    status_filter = request.args.get('status', '')

    query = """
        SELECT f.*, p.manufacturer, p.size_category,
               m.first_name_hebrew, m.last_name_hebrew,
               fl.flight_duration
        FROM Flight f
        JOIN Plane p ON f.plane_id = p.plane_id
        JOIN Manager m ON f.manager_id = m.id_number
        JOIN FlightLine fl ON f.origin_airport = fl.origin_airport
                          AND f.destination_airport = fl.destination_airport
    """
    params = []

    if status_filter:
        query += " WHERE f.status = %s"
        params.append(status_filter)

    query += " ORDER BY f.departure_datetime DESC"

    flights = execute_query(query, tuple(params) if params else None, fetch_all=True)

    # Check which planes have Business class for display
    for flight in flights:
        business_check_query = """
            SELECT COUNT(*) as has_business
            FROM PlaneClass
            WHERE plane_id = %s AND class_type = 'Business'
        """
        business_check = execute_query(business_check_query, (flight['plane_id'],), fetch_one=True)
        flight['has_business'] = business_check and business_check['has_business'] > 0

    return render_template('flights/list.html', flights=flights, current_status=status_filter)

@bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create new flight (managers only)"""
    if not is_manager():
        flash('אין הרשאה לגשת לדף זה', 'error')
        return redirect(url_for('flights.search'))

    if request.method == 'POST':
        origin_airport = request.form.get('origin_airport')
        destination_airport = request.form.get('destination_airport')
        plane_id = request.form.get('plane_id')
        departure_datetime = request.form.get('departure_datetime')
        manager_id = get_current_manager_id()
        price_economy = request.form.get('price_economy', 800)
        price_business = request.form.get('price_business', 1500)

        # Check if plane has Business class
        business_check_query = """
            SELECT COUNT(*) as has_business
            FROM PlaneClass
            WHERE plane_id = %s AND class_type = 'Business'
        """
        business_check = execute_query(business_check_query, (plane_id,), fetch_one=True)
        has_business = business_check and business_check['has_business'] > 0
        
        # Set price_business to NULL if plane doesn't have Business class
        if not has_business:
            price_business = None

        try:
            query = """
                INSERT INTO Flight (origin_airport, destination_airport, plane_id,
                                   departure_datetime, manager_id, status, price_economy, price_business)
                VALUES (%s, %s, %s, %s, %s, 'Active', %s, %s)
            """
            execute_query(query, (origin_airport, destination_airport, plane_id,
                          departure_datetime, manager_id, price_economy, price_business), commit=True)
            flash('טיסה נוצרה בהצלחה', 'success')
            return redirect(url_for('flights.list'))

        except Exception as e:
            flash(f'שגיאה ביצירת טיסה: {str(e)}', 'error')

    # GET request - show form
    # Get flight lines (for route selection)
    flightlines_query = """
        SELECT origin_airport, destination_airport, flight_duration
        FROM FlightLine
        ORDER BY origin_airport, destination_airport
    """
    flightlines = execute_query(flightlines_query, fetch_all=True)

    # Get distinct airports for dropdowns
    airports_query = """
        SELECT DISTINCT origin_airport AS airport FROM FlightLine
        UNION
        SELECT DISTINCT destination_airport AS airport FROM FlightLine
        ORDER BY airport
    """
    airports = execute_query(airports_query, fetch_all=True)

    # Get planes
    planes_query = "SELECT plane_id, manufacturer, size_category FROM Plane ORDER BY plane_id"
    planes = execute_query(planes_query, fetch_all=True)

    return render_template('flights/create.html', flightlines=flightlines, airports=airports, planes=planes)

@bp.route('/<int:flight_id>/cancel', methods=['POST'])
def cancel(flight_id):
    """Cancel a flight (managers only) - must be at least 72 hours before departure"""
    if not is_manager():
        flash('אין הרשאה לבצע פעולה זו', 'error')
        return redirect(url_for('flights.search'))

    # Get flight departure time
    flight_query = "SELECT departure_datetime FROM Flight WHERE flight_id = %s"
    flight = execute_query(flight_query, (flight_id,), fetch_one=True)

    if not flight:
        flash('טיסה לא נמצאה', 'error')
        return redirect(url_for('flights.list'))

    # Check 72-hour rule
    departure_time = flight['departure_datetime']
    time_until_departure = departure_time - datetime.now()

    if time_until_departure < timedelta(hours=72):
        flash('לא ניתן לבטל טיסה פחות מ-72 שעות לפני מועד ההמראה', 'error')
        return redirect(url_for('flights.list'))

    try:
        with db_transaction(commit=True) as db:
            # Update flight status
            db.execute("UPDATE Flight SET status = 'Canceled' WHERE flight_id = %s", (flight_id,))

            # Get all active orders for this flight to refund registered customers
            db.execute("""
                SELECT fo.customer_email, fo.total_payment
                FROM FlightOrder fo
                WHERE fo.flight_id = %s AND fo.order_status = 'Active'
            """, (flight_id,))
            orders_to_refund = db.fetchall()

            # Add full refund to registered customers' balance
            for order in orders_to_refund:
                refund_amount = float(order['total_payment'])
                db.execute("""
                    UPDATE RegisteredCustomer
                    SET balance = balance + %s
                    WHERE email = %s
                """, (refund_amount, order['customer_email']))

            # Update all related orders to Canceled_By_Company with full refund (total_payment = 0)
            db.execute("""
                UPDATE FlightOrder
                SET order_status = 'Canceled_By_Company', total_payment = 0
                WHERE flight_id = %s AND order_status = 'Active'
            """, (flight_id,))

        flash('טיסה בוטלה בהצלחה. כל ההזמנות הפעילות קיבלו זיכוי מלא', 'success')
    except Exception as e:
        flash(f'שגיאה בביטול טיסה: {str(e)}', 'error')

    return redirect(url_for('flights.list'))

@bp.route('/<int:flight_id>/status', methods=['POST'])
def update_status(flight_id):
    """Update flight status (managers only)"""
    if not is_manager():
        flash('אין הרשאה לבצע פעולה זו', 'error')
        return redirect(url_for('flights.search'))

    new_status = request.form.get('status')
    if new_status not in ['Active', 'Full', 'Landed', 'Canceled']:
        flash('סטטוס לא תקין', 'error')
        return redirect(url_for('flights.list'))

    try:
        query = "UPDATE Flight SET status = %s WHERE flight_id = %s"
        execute_query(query, (new_status, flight_id), commit=True)
        flash('סטטוס טיסה עודכן בהצלחה', 'success')
    except Exception as e:
        flash(f'שגיאה בעדכון סטטוס: {str(e)}', 'error')
    
    return redirect(url_for('flights.list'))

@bp.route('/<int:flight_id>/edit-prices', methods=['GET', 'POST'])
def edit_prices(flight_id):
    """Edit flight prices (managers only)"""
    if not is_manager():
        flash('אין הרשאה לגשת לדף זה', 'error')
        return redirect(url_for('flights.search'))

    # Get flight details
    flight_query = "SELECT * FROM Flight WHERE flight_id = %s"
    flight = execute_query(flight_query, (flight_id,), fetch_one=True)

    if not flight:
        flash('טיסה לא נמצאה', 'error')
        return redirect(url_for('flights.list'))
    
    # Check if plane has Business class
    business_check_query = """
        SELECT COUNT(*) as has_business
        FROM PlaneClass
        WHERE plane_id = %s AND class_type = 'Business'
    """
    business_check = execute_query(business_check_query, (flight['plane_id'],), fetch_one=True)
    flight['has_business'] = business_check and business_check['has_business'] > 0

    if request.method == 'POST':
        price_economy = request.form.get('price_economy')
        price_business = request.form.get('price_business')
        
        # Check if plane has Business class
        business_check_query = """
            SELECT COUNT(*) as has_business
            FROM PlaneClass
            WHERE plane_id = %s AND class_type = 'Business'
        """
        business_check = execute_query(business_check_query, (flight['plane_id'],), fetch_one=True)
        has_business = business_check and business_check['has_business'] > 0
        
        # Set price_business to NULL if plane doesn't have Business class
        if not has_business:
            price_business = None

        try:
            update_query = """
                UPDATE Flight
                SET price_economy = %s, price_business = %s
                WHERE flight_id = %s
            """
            execute_query(update_query, (price_economy, price_business, flight_id), commit=True)
            flash('מחירים עודכנו בהצלחה', 'success')
            return redirect(url_for('flights.list'))
        except Exception as e:
            flash(f'שגיאה בעדכון מחירים: {str(e)}', 'error')

    return render_template('flights/edit_prices.html', flight=flight)






