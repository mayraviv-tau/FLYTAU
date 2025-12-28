"""
SQL query constants for FLYTAU application.
Centralized location for all SQL queries.
"""

# ============================================================================
# AUTHENTICATION QUERIES
# ============================================================================

# Check if customer exists
CHECK_CUSTOMER_EXISTS = """
    SELECT email FROM Customer WHERE email = %s
"""

# Insert new customer
INSERT_CUSTOMER = """
    INSERT INTO Customer (email, first_name_english, last_name_english)
    VALUES (%s, %s, %s)
"""

# Insert registered customer
INSERT_REGISTERED_CUSTOMER = """
    INSERT INTO RegisteredCustomer
    (email, registration_date, birth_date, passport_number, account_password, balance)
    VALUES (%s, %s, %s, %s, %s, 0)
"""

# Insert customer phone
INSERT_CUSTOMER_PHONE = """
    INSERT INTO CustomerPhone (email, phone_number)
    VALUES (%s, %s)
"""

# Get registered customer for login
GET_REGISTERED_CUSTOMER = """
    SELECT rc.email, rc.account_password, c.first_name_english, c.last_name_english, rc.balance
    FROM RegisteredCustomer rc
    JOIN Customer c ON rc.email = c.email
    WHERE rc.email = %s
"""

# Get manager for login
GET_MANAGER = """
    SELECT id_number, first_name_hebrew, last_name_hebrew, account_password
    FROM Manager
    WHERE id_number = %s
"""

# Get customer info
GET_CUSTOMER_INFO = """
    SELECT c.email, c.first_name_english, c.last_name_english,
           rc.balance, rc.birth_date, rc.passport_number
    FROM Customer c
    LEFT JOIN RegisteredCustomer rc ON c.email = rc.email
    WHERE c.email = %s
"""

# ============================================================================
# FLIGHT QUERIES
# ============================================================================

# Search flights
SEARCH_FLIGHTS = """
    SELECT
        f.flight_id,
        f.origin_airport,
        f.destination_airport,
        f.departure_datetime,
        f.status,
        f.plane_id,
        p.manufacturer,
        p.size_category,
        fl.flight_duration
    FROM Flight f
    JOIN Plane p ON f.plane_id = p.plane_id
    JOIN FlightLine fl ON f.origin_airport = fl.origin_airport
                       AND f.destination_airport = fl.destination_airport
    WHERE f.status IN ('Active', 'Full')
"""

# Get flight details
GET_FLIGHT = """
    SELECT
        f.flight_id,
        f.origin_airport,
        f.destination_airport,
        f.departure_datetime,
        f.status,
        f.plane_id,
        p.manufacturer,
        p.size_category,
        fl.flight_duration
    FROM Flight f
    JOIN Plane p ON f.plane_id = p.plane_id
    JOIN FlightLine fl ON f.origin_airport = fl.origin_airport
                       AND f.destination_airport = fl.destination_airport
    WHERE f.flight_id = %s
"""

# Get plane classes and capacity
GET_PLANE_CLASSES = """
    SELECT class_type, rows_count, cols_count,
           (rows_count * cols_count) as total_seats
    FROM PlaneClass
    WHERE plane_id = %s
"""

# Get occupied seats for a flight
GET_OCCUPIED_SEATS = """
    SELECT t.class_type, t.seat_number
    FROM Ticket t
    JOIN FlightOrder fo ON t.order_id = fo.order_id
    WHERE fo.flight_id = %s
      AND fo.order_status IN ('Active', 'Completed')
"""

# Get all seats for a plane
GET_PLANE_SEATS = """
    SELECT class_type, seat_number
    FROM Seat
    WHERE plane_id = %s
    ORDER BY class_type, seat_number
"""

# Check if seat exists and is available
CHECK_SEAT_AVAILABLE = """
    SELECT s.seat_number
    FROM Seat s
    WHERE s.plane_id = %s
      AND s.class_type = %s
      AND s.seat_number = %s
      AND NOT EXISTS (
          SELECT 1 FROM Ticket t
          JOIN FlightOrder fo ON t.order_id = fo.order_id
          WHERE t.plane_id = %s
            AND t.class_type = %s
            AND t.seat_number = %s
            AND fo.flight_id = %s
            AND fo.order_status IN ('Active', 'Completed')
      )
"""

# Update flight status
UPDATE_FLIGHT_STATUS = """
    UPDATE Flight
    SET status = %s
    WHERE flight_id = %s
"""

# ============================================================================
# BOOKING & ORDER QUERIES
# ============================================================================

# Insert flight order
INSERT_FLIGHT_ORDER = """
    INSERT INTO FlightOrder
    (customer_email, flight_id, order_date, order_status, total_payment)
    VALUES (%s, %s, %s, 'Active', %s)
"""

# Insert ticket
INSERT_TICKET = """
    INSERT INTO Ticket
    (order_id, plane_id, class_type, seat_number, price)
    VALUES (%s, %s, %s, %s, %s)
"""

# Get user orders
GET_USER_ORDERS = """
    SELECT
        fo.order_id,
        fo.flight_id,
        fo.order_date,
        fo.order_status,
        fo.total_payment,
        f.origin_airport,
        f.destination_airport,
        f.departure_datetime,
        f.status as flight_status
    FROM FlightOrder fo
    JOIN Flight f ON fo.flight_id = f.flight_id
    WHERE fo.customer_email = %s
    ORDER BY fo.order_date DESC
"""

# Get order details
GET_ORDER_DETAILS = """
    SELECT
        fo.order_id,
        fo.customer_email,
        fo.flight_id,
        fo.order_date,
        fo.order_status,
        fo.total_payment,
        f.origin_airport,
        f.destination_airport,
        f.departure_datetime,
        f.plane_id,
        f.status as flight_status
    FROM FlightOrder fo
    JOIN Flight f ON fo.flight_id = f.flight_id
    WHERE fo.order_id = %s
"""

# Get order tickets
GET_ORDER_TICKETS = """
    SELECT class_type, seat_number, price
    FROM Ticket
    WHERE order_id = %s
"""

# Update order status and payment
UPDATE_ORDER_CANCELLATION = """
    UPDATE FlightOrder
    SET order_status = %s, total_payment = %s
    WHERE order_id = %s
"""

# Update customer balance
UPDATE_CUSTOMER_BALANCE = """
    UPDATE RegisteredCustomer
    SET balance = balance + %s
    WHERE email = %s
"""

# Deduct from customer balance
DEDUCT_CUSTOMER_BALANCE = """
    UPDATE RegisteredCustomer
    SET balance = balance - %s
    WHERE email = %s AND balance >= %s
"""

# ============================================================================
# ADMIN - FLIGHT MANAGEMENT QUERIES
# ============================================================================

# Check flight line exists
CHECK_FLIGHT_LINE = """
    SELECT flight_duration
    FROM FlightLine
    WHERE origin_airport = %s AND destination_airport = %s
"""

# Check plane exists
CHECK_PLANE_EXISTS = """
    SELECT plane_id, size_category
    FROM Plane
    WHERE plane_id = %s
"""

# Check pilot qualification
CHECK_PILOT_QUALIFICATION = """
    SELECT id_number, is_long_haul_qualified
    FROM Pilot
    WHERE id_number = %s
"""

# Check attendant qualification
CHECK_ATTENDANT_QUALIFICATION = """
    SELECT id_number, is_long_haul_qualified
    FROM FlightAttendant
    WHERE id_number = %s
"""

# Check crew availability (no conflicts)
CHECK_PILOT_AVAILABILITY = """
    SELECT f.flight_id
    FROM Flight f
    JOIN FlightPilotAssignment fpa ON f.flight_id = fpa.flight_id
    WHERE fpa.pilot_id = %s
      AND f.departure_datetime BETWEEN %s AND %s
      AND f.status NOT IN ('Landed', 'Canceled')
"""

CHECK_ATTENDANT_AVAILABILITY = """
    SELECT f.flight_id
    FROM Flight f
    JOIN FlightAttendantAssignment faa ON f.flight_id = faa.flight_id
    WHERE faa.flight_attendant_id = %s
      AND f.departure_datetime BETWEEN %s AND %s
      AND f.status NOT IN ('Landed', 'Canceled')
"""

# Insert flight
INSERT_FLIGHT = """
    INSERT INTO Flight
    (origin_airport, destination_airport, plane_id, departure_datetime, manager_id, status)
    VALUES (%s, %s, %s, %s, %s, 'Active')
"""

# Insert pilot assignment
INSERT_PILOT_ASSIGNMENT = """
    INSERT INTO FlightPilotAssignment (pilot_id, flight_id)
    VALUES (%s, %s)
"""

# Insert attendant assignment
INSERT_ATTENDANT_ASSIGNMENT = """
    INSERT INTO FlightAttendantAssignment (flight_attendant_id, flight_id)
    VALUES (%s, %s)
"""

# Get active orders for flight
GET_FLIGHT_ACTIVE_ORDERS = """
    SELECT order_id, customer_email, total_payment
    FROM FlightOrder
    WHERE flight_id = %s AND order_status = 'Active'
"""

# ============================================================================
# ADMIN - REPORTS QUERIES
# ============================================================================

# Report file paths will be loaded dynamically from db/reports_sql/
