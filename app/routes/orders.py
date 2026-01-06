"""
Order routes
Handles order creation, listing, cancellation, and history
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import execute_query, get_db_cursor
from utils.auth import is_logged_in, get_current_user_email, get_current_manager_id, is_manager
from datetime import datetime, timedelta

bp = Blueprint('orders', __name__)

@bp.route('/create', methods=['POST'])
def create():
    """Create new order with tickets"""
    # Prevent managers from booking flights
    if is_manager():
        flash('מנהלים לא יכולים להזמין טיסות', 'error')
        return redirect(url_for('flights.search'))
    
    if not request.form.get('flight_id') or not request.form.getlist('seats'):
        flash('יש לבחור לפחות מושב אחד', 'error')
        return redirect(url_for('flights.search'))

    flight_id = int(request.form.get('flight_id'))
    plane_id = int(request.form.get('plane_id'))
    selected_seats = request.form.getlist('seats')

    # Get customer email (use guest email if not logged in)
    customer_email = get_current_user_email()
    if not customer_email:
        # For guests, we need to create a customer record
        # In a real system, we'd ask for guest details
        flash('יש להתחבר כדי להזמין טיסה', 'error')
        return redirect(url_for('auth.login'))

    # Verify flight exists and is active
    flight_query = "SELECT * FROM Flight WHERE flight_id = %s AND status IN ('Active', 'Full')"
    flight = execute_query(flight_query, (flight_id,), fetch_one=True)

    if not flight:
        flash('טיסה לא נמצאה או לא זמינה להזמנה', 'error')
        return redirect(url_for('flights.search'))

    # Verify plane_id matches flight plane_id
    if flight['plane_id'] != plane_id:
        flash('שגיאה: מטוס לא תואם לטיסה', 'error')
        return redirect(url_for('flights.search'))

    try:
        with get_db_cursor(commit=True) as cursor:
            # Check seat availability
            occupied_query = """
                SELECT t.plane_id, t.class_type, t.seat_number
                FROM Ticket t
                JOIN FlightOrder fo ON t.order_id = fo.order_id
                WHERE fo.flight_id = %s
                  AND fo.order_status IN ('Active', 'Completed')
                  AND t.plane_id = %s
            """
            cursor.execute(occupied_query, (flight_id, plane_id))
            occupied_seats = {(row['plane_id'], row['class_type'], row['seat_number'])
                            for row in cursor.fetchall()}

            # Parse selected seats and check availability
            seats_to_book = []
            total_price = 0
            for seat_str in selected_seats:
                parts = seat_str.split(',')
                if len(parts) != 3:
                    continue
                seat_plane_id, seat_class, seat_number = int(parts[0]), parts[1], parts[2]

                seat_key = (seat_plane_id, seat_class, seat_number)
                if seat_key in occupied_seats:
                    flash(f'מושב {seat_number} במחלקה {seat_class} כבר תפוס', 'error')
                    return redirect(url_for('flights.seats', flight_id=flight_id))

                # Calculate price (Business: 1500, Economy: 800)
                # Calculate price from flight
                price = float(flight['price_business']) if seat_class == 'Business' else float(flight['price_economy'])
                seats_to_book.append((seat_plane_id, seat_class, seat_number, price))
                total_price += price

            if not seats_to_book:
                flash('לא נבחרו מושבים', 'error')
                return redirect(url_for('flights.seats', flight_id=flight_id))

            # Create order
            order_query = """
                INSERT INTO FlightOrder (customer_email, flight_id, order_date, order_status, total_payment)
                VALUES (%s, %s, %s, 'Active', %s)
            """
            cursor.execute(order_query, (customer_email, flight_id, datetime.now(), total_price))
            order_id = cursor.lastrowid

            # Create tickets
            ticket_query = """
                INSERT INTO Ticket (order_id, plane_id, class_type, seat_number, price)
                VALUES (%s, %s, %s, %s, %s)
            """
            for seat_plane_id, seat_class, seat_number, price in seats_to_book:
                cursor.execute(ticket_query, (order_id, seat_plane_id, seat_class, seat_number, price))

            # Update flight status to Full if needed (check capacity)
            capacity_query = """
                SELECT SUM(rows_count * cols_count) AS total_seats
                FROM PlaneClass
                WHERE plane_id = %s
            """
            cursor.execute(capacity_query, (plane_id,))
            total_capacity = cursor.fetchone()['total_seats']

            booked_query = """
                SELECT COUNT(*) AS booked_count
                FROM Ticket t
                JOIN FlightOrder fo ON t.order_id = fo.order_id
                WHERE fo.flight_id = %s
                  AND fo.order_status IN ('Active', 'Completed')
                  AND t.plane_id = %s
            """
            cursor.execute(booked_query, (flight_id, plane_id))
            booked_count = cursor.fetchone()['booked_count']

            if booked_count >= total_capacity:
                update_query = "UPDATE Flight SET status = 'Full' WHERE flight_id = %s"
                cursor.execute(update_query, (flight_id,))

        flash(f'הזמנה נוצרה בהצלחה! מספר הזמנה: {order_id}', 'success')
        return redirect(url_for('orders.details', order_id=order_id))

    except Exception as e:
        flash(f'שגיאה ביצירת הזמנה: {str(e)}', 'error')
        return redirect(url_for('flights.seats', flight_id=flight_id))

@bp.route('/')
def list():
    """List orders for current user"""
    if not is_logged_in():
        flash('יש להתחבר כדי לראות הזמנות', 'error')
        return redirect(url_for('auth.login'))

    customer_email = get_current_user_email()
    if not customer_email:
        flash('לא מזוהה כמשתמש', 'error')
        return redirect(url_for('auth.login'))

    query = """
        SELECT fo.*, f.origin_airport, f.destination_airport,
               f.departure_datetime, f.status AS flight_status,
               COUNT(t.order_id) AS ticket_count
        FROM FlightOrder fo
        JOIN Flight f ON fo.flight_id = f.flight_id
        LEFT JOIN Ticket t ON fo.order_id = t.order_id
        WHERE fo.customer_email = %s
        GROUP BY fo.order_id
        ORDER BY fo.order_date ASC
    """
    orders = execute_query(query, (customer_email,), fetch_all=True)
    
    # Add per-customer order number (chronological, starting from 1)
    # Order 1 = oldest order, Order 2 = second oldest, etc.
    for idx, order in enumerate(orders, start=1):
        order['customer_order_number'] = idx
    
    # Reverse to show newest first (but numbers remain chronological)
    orders_list = list(orders)
    orders_list.reverse()

    return render_template('orders/list.html', orders=orders_list)

@bp.route('/<int:order_id>')
def details(order_id):
    """Order details"""
    customer_email = get_current_user_email()
    if not customer_email:
        flash('יש להתחבר כדי לראות פרטי הזמנה', 'error')
        return redirect(url_for('auth.login'))

    # Get order details
    order_query = """
        SELECT fo.*, f.origin_airport, f.destination_airport,
               f.departure_datetime, f.status AS flight_status,
               c.first_name_english, c.last_name_english
        FROM FlightOrder fo
        JOIN Flight f ON fo.flight_id = f.flight_id
        JOIN Customer c ON fo.customer_email = c.email
        WHERE fo.order_id = %s AND fo.customer_email = %s
    """
    order = execute_query(order_query, (order_id, customer_email), fetch_one=True)

    if not order:
        flash('הזמנה לא נמצאה', 'error')
        return redirect(url_for('orders.list'))

    # Calculate per-customer order number (chronological)
    # Count orders that come before this one (by date, then by ID)
    order_number_query = """
        SELECT COUNT(*) + 1 AS customer_order_number
        FROM FlightOrder
        WHERE customer_email = %s 
          AND (order_date < %s OR (order_date = %s AND order_id <= %s))
    """
    order_number_result = execute_query(order_number_query, 
                                        (customer_email, order['order_date'], order['order_date'], order_id), 
                                        fetch_one=True)
    order['customer_order_number'] = order_number_result['customer_order_number'] if order_number_result else 1

    # Get tickets for this order
    tickets_query = """
        SELECT t.*
        FROM Ticket t
        WHERE t.order_id = %s
        ORDER BY t.class_type, t.seat_number
    """
    tickets = execute_query(tickets_query, (order_id,), fetch_all=True)

    return render_template('orders/details.html', order=order, tickets=tickets)

@bp.route('/<int:order_id>/cancel', methods=['POST'])
def cancel(order_id):
    """Cancel order (with 5% cancellation fee)"""
    customer_email = get_current_user_email()
    if not customer_email:
        flash('יש להתחבר כדי לבטל הזמנה', 'error')
        return redirect(url_for('auth.login'))

    # Get order details
    order_query = """
        SELECT * FROM FlightOrder
        WHERE order_id = %s AND customer_email = %s
    """
    order = execute_query(order_query, (order_id, customer_email), fetch_one=True)

    if not order:
        flash('הזמנה לא נמצאה', 'error')
        return redirect(url_for('orders.list'))

    if order['order_status'] != 'Active':
        flash('לא ניתן לבטל הזמנה שכבר בוטלה או הושלמה', 'error')
        return redirect(url_for('orders.details', order_id=order_id))

    # Get flight departure time to check 36 hours limit
    flight_query = """
        SELECT departure_datetime 
        FROM Flight 
        WHERE flight_id = (SELECT flight_id FROM FlightOrder WHERE order_id = %s)
    """
    flight = execute_query(flight_query, (order_id,), fetch_one=True)
    
    if flight:
        departure_time = flight['departure_datetime']
        time_until_departure = departure_time - datetime.now()
        
        # Check if less than 36 hours before departure
        if time_until_departure < timedelta(hours=36):
            flash('לא ניתן לבטל הזמנה פחות מ-36 שעות לפני מועד הטיסה', 'error')
            return redirect(url_for('orders.details', order_id=order_id))

    try:
        with get_db_cursor(commit=True) as cursor:
            # Calculate cancellation fee (5% of original total)
            cancellation_fee = float(order['total_payment']) * 0.05

            # Update order status
            update_query = """
                UPDATE FlightOrder
                SET order_status = 'Canceled_By_Client', total_payment = %s
                WHERE order_id = %s
            """
            cursor.execute(update_query, (cancellation_fee, order_id))

            # If registered customer, update balance (refund minus fee)
            # Note: This would require updating RegisteredCustomer.balance
            # For now, we just update the order status

        flash(f'הזמנה בוטלה. דמי ביטול: {cancellation_fee:.2f} ₪', 'success')
        return redirect(url_for('orders.details', order_id=order_id))

    except Exception as e:
        flash(f'שגיאה בביטול הזמנה: {str(e)}', 'error')
        return redirect(url_for('orders.details', order_id=order_id))

@bp.route('/guest-view', methods=['GET', 'POST'])
def guest_view():
    """Allow guests to view tickets using order ID and email"""
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        email = request.form.get('email')
        
        if not order_id or not email:
            flash('יש למלא את קוד ההזמנה וכתובת המייל', 'error')
            return render_template('orders/guest_view.html')
        
        try:
            order_id = int(order_id)
        except ValueError:
            flash('קוד הזמנה חייב להיות מספר', 'error')
            return render_template('orders/guest_view.html')
        
        # Get order details
        order_query = """
            SELECT fo.*, f.origin_airport, f.destination_airport,
                   f.departure_datetime, f.status AS flight_status
            FROM FlightOrder fo
            JOIN Flight f ON fo.flight_id = f.flight_id
            WHERE fo.order_id = %s AND fo.customer_email = %s
        """
        order = execute_query(order_query, (order_id, email), fetch_one=True)
        
        if not order:
            flash('הזמנה לא נמצאה. אנא ודא שקוד ההזמנה וכתובת המייל נכונים', 'error')
            return render_template('orders/guest_view.html')
        
        # Get tickets for this order
        tickets_query = """
            SELECT t.*
            FROM Ticket t
            WHERE t.order_id = %s
            ORDER BY t.class_type, t.seat_number
        """
        tickets = execute_query(tickets_query, (order_id,), fetch_all=True)
        
        return render_template('orders/guest_details.html', order=order, tickets=tickets)
    
    return render_template('orders/guest_view.html')

@bp.route('/history')
def history():
    """Purchase history (registered customers only)"""
    customer_email = get_current_user_email()
    if not customer_email:
        flash('יש להתחבר כדי לראות היסטוריה', 'error')
        return redirect(url_for('auth.login'))

    # Check if registered customer
    check_query = "SELECT email FROM RegisteredCustomer WHERE email = %s"
    if not execute_query(check_query, (customer_email,), fetch_one=True):
        flash('היסטוריית רכישות זמינה רק ללקוחות רשומים', 'error')
        return redirect(url_for('orders.list'))

    # Get filter parameter
    status_filter = request.args.get('status', '')

    query = """
        SELECT fo.*, f.origin_airport, f.destination_airport,
               f.departure_datetime, f.status AS flight_status,
               COUNT(t.order_id) AS ticket_count
        FROM FlightOrder fo
        JOIN Flight f ON fo.flight_id = f.flight_id
        LEFT JOIN Ticket t ON fo.order_id = t.order_id
        WHERE fo.customer_email = %s
    """
    params = [customer_email]

    if status_filter:
        query += " AND fo.order_status = %s"
        params.append(status_filter)

    query += " GROUP BY fo.order_id ORDER BY fo.order_date ASC"

    orders = execute_query(query, tuple(params), fetch_all=True)
    
    # Add per-customer order number (chronological, starting from 1)
    for idx, order in enumerate(orders, start=1):
        order['customer_order_number'] = idx
    
    # Reverse to show newest first (but numbers remain chronological)
    orders_list = list(orders)
    orders_list.reverse()

    return render_template('orders/history.html', orders=orders_list, current_status=status_filter)

