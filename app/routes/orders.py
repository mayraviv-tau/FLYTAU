"""
Order routes
Handles order creation, listing, cancellation, and history
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import execute_query, db_transaction
from utils.auth import is_logged_in, get_current_user_email, get_current_manager_id, is_manager
from datetime import datetime, timedelta
from routes.flights import update_expired_flights

bp = Blueprint('orders', __name__)

@bp.route('/create', methods=['POST'])
def create():
    """Create new order with tickets - supports both logged in users and guests"""
    # Prevent managers from booking flights
    if is_manager():
        flash('מנהלים אינם רשאים להזמין כרטיסים', 'error')
        return redirect(url_for('flights.search'))
    
    if not request.form.get('flight_id') or not request.form.getlist('seats'):
        flash('יש לבחור לפחות מושב אחד', 'error')
        return redirect(url_for('flights.search'))

    flight_id = int(request.form.get('flight_id'))
    plane_id = int(request.form.get('plane_id'))
    selected_seats = request.form.getlist('seats')

    # Get customer email - either from session (logged in) or from form (guest)
    customer_email = get_current_user_email()
    guest_first_name = None
    guest_last_name = None
    
    if not customer_email:
        # Guest booking - get email and name from form
        customer_email = request.form.get('guest_email', '').strip().lower()
        guest_first_name = request.form.get('guest_first_name', '').strip()
        guest_last_name = request.form.get('guest_last_name', '').strip()
        
        if not customer_email or not guest_first_name or not guest_last_name:
            flash('יש למלא שם מלא וכתובת מייל להזמנה כאורח', 'error')
            return redirect(url_for('flights.seats', flight_id=flight_id))

    # Verify flight exists and is active
    flight_query = """
        SELECT f.*, p.size_category
        FROM Flight f
        JOIN Plane p ON f.plane_id = p.plane_id
        WHERE f.flight_id = %s AND f.status IN ('Active', 'Full')
    """
    flight = execute_query(flight_query, (flight_id,), fetch_one=True)

    if not flight:
        flash('טיסה לא נמצאה או לא זמינה להזמנה', 'error')
        return redirect(url_for('flights.search'))

    # Verify plane_id matches flight plane_id
    if flight['plane_id'] != plane_id:
        flash('שגיאה: מטוס לא תואם לטיסה', 'error')
        return redirect(url_for('flights.search'))

    try:
        with db_transaction(commit=True) as db:
            # For guests, create Customer record if doesn't exist
            if guest_first_name and guest_last_name:
                # Check if customer exists
                check_customer = "SELECT email FROM Customer WHERE LOWER(email) = %s"
                db.execute(check_customer, (customer_email,))
                if not db.fetchone():
                    # Create new guest customer (not registered)
                    create_customer = """
                        INSERT INTO Customer (email, first_name_english, last_name_english)
                        VALUES (%s, %s, %s)
                    """
                    db.execute(create_customer, (customer_email, guest_first_name, guest_last_name))
            
            # Check seat availability
            occupied_query = """
                SELECT t.plane_id, t.class_type, t.seat_number
                FROM Ticket t
                JOIN FlightOrder fo ON t.order_id = fo.order_id
                WHERE fo.flight_id = %s
                  AND fo.order_status IN ('Active', 'Completed')
                  AND t.plane_id = %s
            """
            db.execute(occupied_query, (flight_id, plane_id))
            occupied_seats = {(row['plane_id'], row['class_type'], row['seat_number'])
                            for row in db.fetchall()}

            # Parse selected seats and check availability
            seats_to_book = []
            total_price = 0
            for seat_str in selected_seats:
                parts = seat_str.split(',')
                if len(parts) != 3:
                    continue
                seat_plane_id, seat_class, seat_number = int(parts[0]), parts[1], parts[2]

                # Validate: Small planes don't have Business class
                if seat_class == 'Business' and flight['size_category'] == 'Small':
                    flash('מטוסים קטנים לא כוללים מחלקת עסקים', 'error')
                    return redirect(url_for('flights.seats', flight_id=flight_id))

                seat_key = (seat_plane_id, seat_class, seat_number)
                if seat_key in occupied_seats:
                    flash(f'מושב {seat_number} במחלקה {seat_class} כבר תפוס', 'error')
                    return redirect(url_for('flights.seats', flight_id=flight_id))

                # Calculate price from flight
                if seat_class == 'Business':
                    price = float(flight['price_business']) if flight['price_business'] else 0
                else:
                    price = float(flight['price_economy'])
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
            db.execute(order_query, (customer_email, flight_id, datetime.now(), total_price))
            order_id = db.lastrowid

            # Create tickets
            ticket_query = """
                INSERT INTO Ticket (flight_id, order_id, plane_id, class_type, seat_number, price)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            for seat_plane_id, seat_class, seat_number, price in seats_to_book:
                db.execute(ticket_query, (flight_id, order_id, seat_plane_id, seat_class, seat_number, price))

            # Update flight status to Full if needed
            capacity_query = """
                SELECT SUM(rows_count * cols_count) AS total_seats
                FROM PlaneClass
                WHERE plane_id = %s
            """
            db.execute(capacity_query, (plane_id,))
            total_capacity = db.fetchone()['total_seats']

            booked_query = """
                SELECT COUNT(*) AS booked_count
                FROM Ticket t
                JOIN FlightOrder fo ON t.order_id = fo.order_id
                WHERE fo.flight_id = %s
                  AND fo.order_status IN ('Active', 'Completed')
                  AND t.plane_id = %s
            """
            db.execute(booked_query, (flight_id, plane_id))
            booked_count = db.fetchone()['booked_count']

            if booked_count >= total_capacity:
                update_query = "UPDATE Flight SET status = 'Full' WHERE flight_id = %s"
                db.execute(update_query, (flight_id,))

        # If guest, show confirmation page with order details
        if guest_first_name:
            return render_template('orders/guest_confirmation.html',
                                 order_id=order_id,
                                 email=customer_email)
        else:
            flash(f'הזמנה נוצרה בהצלחה! מספר הזמנה: {order_id}', 'success')
            return redirect(url_for('orders.details', order_id=order_id))

    except Exception as e:
        flash(f'שגיאה ביצירת הזמנה: {str(e)}', 'error')
        return redirect(url_for('flights.seats', flight_id=flight_id))

@bp.route('/')
def list():
    """List ACTIVE orders for current user (upcoming flights)"""
    # Update expired flights and their orders first
    update_expired_flights()

    if not is_logged_in():
        flash('יש להתחבר כדי לראות הזמנות', 'error')
        return redirect(url_for('auth.login'))

    customer_email = get_current_user_email()
    if not customer_email:
        flash('לא מזוהה כמשתמש', 'error')
        return redirect(url_for('auth.login'))

    # Only show Active orders, sorted by flight departure date (ascending - nearest first)
    query = """
        SELECT fo.*, f.origin_airport, f.destination_airport,
               f.departure_datetime, f.status AS flight_status,
               COUNT(t.order_id) AS ticket_count
        FROM FlightOrder fo
        JOIN Flight f ON fo.flight_id = f.flight_id
        LEFT JOIN Ticket t ON fo.order_id = t.order_id
        WHERE fo.customer_email = %s
          AND fo.order_status = 'Active'
        GROUP BY fo.order_id
        ORDER BY f.departure_datetime ASC
    """
    orders = execute_query(query, (customer_email,), fetch_all=True)

    # Get order numbers based on all orders for this customer
    all_orders_query = """
        SELECT order_id FROM FlightOrder
        WHERE customer_email = %s
        ORDER BY order_date ASC
    """
    all_orders = execute_query(all_orders_query, (customer_email,), fetch_all=True)
    order_id_to_number = {o['order_id']: idx + 1 for idx, o in enumerate(all_orders)}

    for order in orders:
        order['customer_order_number'] = order_id_to_number.get(order['order_id'], 0)

    return render_template('orders/list.html', orders=orders)

@bp.route('/<int:order_id>')
def details(order_id):
    """Order details"""
    customer_email = get_current_user_email()
    if not customer_email:
        flash('יש להתחבר כדי לראות פרטי הזמנה', 'error')
        return redirect(url_for('auth.login'))

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

    flight_query = """
        SELECT departure_datetime 
        FROM Flight 
        WHERE flight_id = (SELECT flight_id FROM FlightOrder WHERE order_id = %s)
    """
    flight = execute_query(flight_query, (order_id,), fetch_one=True)
    
    if flight:
        departure_time = flight['departure_datetime']
        time_until_departure = departure_time - datetime.now()
        
        if time_until_departure < timedelta(hours=36):
            flash('לא ניתן לבטל הזמנה פחות מ-36 שעות לפני מועד הטיסה', 'error')
            return redirect(url_for('orders.details', order_id=order_id))

    try:
        with db_transaction(commit=True) as db:
            original_payment = float(order['total_payment'])
            cancellation_fee = original_payment * 0.05
            refund_amount = original_payment * 0.95

            # Update order status and set payment to cancellation fee
            update_query = """
                UPDATE FlightOrder
                SET order_status = 'Canceled_By_Client', total_payment = %s
                WHERE order_id = %s
            """
            db.execute(update_query, (cancellation_fee, order_id))

            # Add refund to registered customer's balance (if registered)
            db.execute("""
                UPDATE RegisteredCustomer
                SET balance = balance + %s
                WHERE email = %s
            """, (refund_amount, customer_email))

        flash(f'הזמנה בוטלה. דמי ביטול: {cancellation_fee:.2f} ₪. זיכוי: {refund_amount:.2f} ₪', 'success')
        return redirect(url_for('orders.details', order_id=order_id))

    except Exception as e:
        flash(f'שגיאה בביטול הזמנה: {str(e)}', 'error')
        return redirect(url_for('orders.details', order_id=order_id))

@bp.route('/lookup', methods=['GET', 'POST'])
def lookup():
    """Guest order lookup - view and cancel orders using order_id + email"""
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        email = request.form.get('email', '').strip().lower()
        
        if not order_id or not email:
            flash('יש למלא את קוד ההזמנה וכתובת המייל', 'error')
            return render_template('orders/guest_view.html')
        
        try:
            order_id = int(order_id)
        except ValueError:
            flash('קוד הזמנה חייב להיות מספר', 'error')
            return render_template('orders/guest_view.html')
        
        order_query = """
            SELECT fo.*, f.origin_airport, f.destination_airport,
                   f.departure_datetime, f.status AS flight_status,
                   c.first_name_english, c.last_name_english
            FROM FlightOrder fo
            JOIN Flight f ON fo.flight_id = f.flight_id
            JOIN Customer c ON fo.customer_email = c.email
            WHERE fo.order_id = %s AND LOWER(fo.customer_email) = %s
        """
        order = execute_query(order_query, (order_id, email), fetch_one=True)
        
        if not order:
            flash('הזמנה לא נמצאה. אנא ודא שקוד ההזמנה וכתובת המייל נכונים', 'error')
            return render_template('orders/guest_view.html')
        
        tickets_query = """
            SELECT t.*
            FROM Ticket t
            WHERE t.order_id = %s
            ORDER BY t.class_type, t.seat_number
        """
        tickets = execute_query(tickets_query, (order_id,), fetch_all=True)
        
        # Check if cancellation is allowed (more than 36 hours before departure)
        can_cancel = False
        if order['order_status'] == 'Active':
            departure_time = order['departure_datetime']
            time_until_departure = departure_time - datetime.now()
            can_cancel = time_until_departure >= timedelta(hours=36)
        
        return render_template('orders/guest_details.html', order=order, tickets=tickets, 
                             can_cancel=can_cancel, guest_email=email)
    
    return render_template('orders/guest_view.html')

@bp.route('/guest-cancel', methods=['POST'])
def guest_cancel():
    """Cancel order for guests (with 5% cancellation fee)"""
    order_id = request.form.get('order_id')
    email = request.form.get('email', '').strip().lower()
    
    if not order_id or not email:
        flash('פרטי הזמנה חסרים', 'error')
        return redirect(url_for('orders.lookup'))
    
    try:
        order_id = int(order_id)
    except ValueError:
        flash('קוד הזמנה לא תקין', 'error')
        return redirect(url_for('orders.lookup'))
    
    order_query = """
        SELECT fo.*, f.departure_datetime
        FROM FlightOrder fo
        JOIN Flight f ON fo.flight_id = f.flight_id
        WHERE fo.order_id = %s AND LOWER(fo.customer_email) = %s
    """
    order = execute_query(order_query, (order_id, email), fetch_one=True)
    
    if not order:
        flash('הזמנה לא נמצאה', 'error')
        return redirect(url_for('orders.lookup'))
    
    if order['order_status'] != 'Active':
        flash('לא ניתן לבטל הזמנה שכבר בוטלה או הושלמה', 'error')
        return redirect(url_for('orders.lookup'))
    
    # Check 36 hours limit
    departure_time = order['departure_datetime']
    time_until_departure = departure_time - datetime.now()
    
    if time_until_departure < timedelta(hours=36):
        flash('לא ניתן לבטל הזמנה פחות מ-36 שעות לפני מועד הטיסה', 'error')
        return redirect(url_for('orders.lookup'))
    
    try:
        with db_transaction(commit=True) as db:
            original_payment = float(order['total_payment'])
            cancellation_fee = original_payment * 0.05
            refund_amount = original_payment * 0.95

            # Update order status and set payment to cancellation fee
            update_query = """
                UPDATE FlightOrder
                SET order_status = 'Canceled_By_Client', total_payment = %s
                WHERE order_id = %s
            """
            db.execute(update_query, (cancellation_fee, order_id))

            # Add refund to registered customer's balance (if registered)
            db.execute("""
                UPDATE RegisteredCustomer
                SET balance = balance + %s
                WHERE email = %s
            """, (refund_amount, email))

        flash(f'הזמנה בוטלה בהצלחה. דמי ביטול: {cancellation_fee:.2f} ₪. זיכוי: {refund_amount:.2f} ₪', 'success')
        return redirect(url_for('orders.lookup'))
    
    except Exception as e:
        flash(f'שגיאה בביטול הזמנה: {str(e)}', 'error')
        return redirect(url_for('orders.lookup'))

# Keep old route for backward compatibility
@bp.route('/guest-view', methods=['GET', 'POST'])
def guest_view():
    """Redirect to new lookup route"""
    return redirect(url_for('orders.lookup'))

@bp.route('/history')
def history():
    """Purchase history - past/closed orders (registered customers only)"""
    # Update expired flights and their orders first
    update_expired_flights()

    customer_email = get_current_user_email()
    if not customer_email:
        flash('יש להתחבר כדי לראות היסטוריה', 'error')
        return redirect(url_for('auth.login'))

    check_query = "SELECT email FROM RegisteredCustomer WHERE email = %s"
    if not execute_query(check_query, (customer_email,), fetch_one=True):
        flash('היסטוריית רכישות זמינה רק ללקוחות רשומים', 'error')
        return redirect(url_for('orders.list'))

    status_filter = request.args.get('status', '')

    # Only show non-Active orders (Completed, Canceled_By_Client, Canceled_By_Company)
    query = """
        SELECT fo.*, f.origin_airport, f.destination_airport,
               f.departure_datetime, f.status AS flight_status,
               COUNT(t.order_id) AS ticket_count
        FROM FlightOrder fo
        JOIN Flight f ON fo.flight_id = f.flight_id
        LEFT JOIN Ticket t ON fo.order_id = t.order_id
        WHERE fo.customer_email = %s
          AND fo.order_status IN ('Completed', 'Canceled_By_Client', 'Canceled_By_Company')
    """
    params = [customer_email]

    if status_filter:
        query += " AND fo.order_status = %s"
        params.append(status_filter)

    # Sort by order_date descending (newest first)
    query += " GROUP BY fo.order_id ORDER BY fo.order_date DESC"

    orders = execute_query(query, tuple(params), fetch_all=True)

    # Get order numbers based on all orders for this customer
    all_orders_query = """
        SELECT order_id FROM FlightOrder
        WHERE customer_email = %s
        ORDER BY order_date ASC
    """
    all_orders = execute_query(all_orders_query, (customer_email,), fetch_all=True)
    order_id_to_number = {o['order_id']: idx + 1 for idx, o in enumerate(all_orders)}

    for order in orders:
        order['customer_order_number'] = order_id_to_number.get(order['order_id'], 0)

    return render_template('orders/history.html', orders=orders, current_status=status_filter)
