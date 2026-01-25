"""
Manager routes
Handles manager-only operations like crew assignment
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import execute_query, db_transaction
from utils.auth import is_manager, get_current_manager_id

bp = Blueprint('managers', __name__)

@bp.route('/flights/<int:flight_id>/crew', methods=['GET', 'POST'])
def assign_crew(flight_id):
    """Assign crew (pilots and flight attendants) to a flight"""
    if not is_manager():
        flash('אין הרשאה לגשת לדף זה', 'error')
        return redirect(url_for('flights.search'))

    # Get flight details
    flight_query = """
        SELECT f.*, fl.flight_duration
        FROM Flight f
        JOIN FlightLine fl ON f.origin_airport = fl.origin_airport
                          AND f.destination_airport = fl.destination_airport
        WHERE f.flight_id = %s
    """
    flight = execute_query(flight_query, (flight_id,), fetch_one=True)

    if not flight:
        flash('טיסה לא נמצאה', 'error')
        return redirect(url_for('flights.list'))

    # Determine required crew based on flight duration
    is_long_haul = flight['flight_duration'] > 6
    required_pilots = 3 if is_long_haul else 2
    required_fas = 6 if is_long_haul else 3

    if request.method == 'POST':
        pilot_ids = list(set(request.form.getlist('pilot_id')))
        fa_ids = list(set(request.form.getlist('flight_attendant_id')))

        # Validate crew counts
        if len(pilot_ids) != required_pilots:
            flash(f'נדרשים בדיוק {required_pilots} טייסים לטיסה זו', 'error')
            return redirect(url_for('managers.assign_crew', flight_id=flight_id))

        if len(fa_ids) != required_fas:
            flash(f'נדרשים בדיוק {required_fas} דיילים לטיסה זו', 'error')
            return redirect(url_for('managers.assign_crew', flight_id=flight_id))

        # If long haul, verify all crew is qualified
        if is_long_haul:
            for pilot_id in pilot_ids:
                pilot_query = "SELECT is_long_haul_qualified FROM Pilot WHERE id_number = %s"
                pilot = execute_query(pilot_query, (pilot_id,), fetch_one=True)
                if not pilot or not pilot['is_long_haul_qualified']:
                    flash(f'טייס {pilot_id} לא מוכשר לטיסות ארוכות', 'error')
                    return redirect(url_for('managers.assign_crew', flight_id=flight_id))

            for fa_id in fa_ids:
                fa_query = "SELECT is_long_haul_qualified FROM FlightAttendant WHERE id_number = %s"
                fa = execute_query(fa_query, (fa_id,), fetch_one=True)
                if not fa or not fa['is_long_haul_qualified']:
                    flash(f'דייל {fa_id} לא מוכשר לטיסות ארוכות', 'error')
                    return redirect(url_for('managers.assign_crew', flight_id=flight_id))

        try:
            with db_transaction(commit=True) as db:
                # Delete existing assignments
                db.execute("DELETE FROM FlightPilotAssignment WHERE flight_id = %s", (flight_id,))
                db.execute("DELETE FROM FlightAttendantAssignment WHERE flight_id = %s", (flight_id,))

                # Insert pilot assignments
                pilot_insert = "INSERT INTO FlightPilotAssignment (pilot_id, flight_id) VALUES (%s, %s)"
                for pilot_id in pilot_ids:
                    db.execute(pilot_insert, (pilot_id, flight_id))

                # Insert flight attendant assignments
                fa_insert = "INSERT INTO FlightAttendantAssignment (flight_attendant_id, flight_id) VALUES (%s, %s)"
                for fa_id in fa_ids:
                    db.execute(fa_insert, (fa_id, flight_id))

            flash('צוות שובץ בהצלחה', 'success')
            return redirect(url_for('flights.list'))

        except Exception as e:
            flash(f'שגיאה בשיבוץ צוות: {str(e)}', 'error')

    # GET request - show form
    # Get available pilots
    if is_long_haul:
        pilots_query = """
            SELECT id_number, first_name_hebrew, last_name_hebrew
            FROM Pilot
            WHERE is_long_haul_qualified = TRUE
            ORDER BY first_name_hebrew, last_name_hebrew
        """
    else:
        pilots_query = """
            SELECT id_number, first_name_hebrew, last_name_hebrew
            FROM Pilot
            ORDER BY first_name_hebrew, last_name_hebrew
        """
    pilots = execute_query(pilots_query, fetch_all=True)

    # Get available flight attendants
    if is_long_haul:
        fas_query = """
            SELECT id_number, first_name_hebrew, last_name_hebrew
            FROM FlightAttendant
            WHERE is_long_haul_qualified = TRUE
            ORDER BY first_name_hebrew, last_name_hebrew
        """
    else:
        fas_query = """
            SELECT id_number, first_name_hebrew, last_name_hebrew
            FROM FlightAttendant
            ORDER BY first_name_hebrew, last_name_hebrew
        """
    flight_attendants = execute_query(fas_query, fetch_all=True)

    # Get current assignments
    current_pilots_query = """
        SELECT pilot_id FROM FlightPilotAssignment WHERE flight_id = %s
    """
    current_pilots = [row['pilot_id'] for row in execute_query(current_pilots_query, (flight_id,), fetch_all=True)]

    current_fas_query = """
        SELECT flight_attendant_id FROM FlightAttendantAssignment WHERE flight_id = %s
    """
    current_fas = [row['flight_attendant_id'] for row in execute_query(current_fas_query, (flight_id,), fetch_all=True)]

    return render_template('flights/crew.html',
                         flight=flight,
                         pilots=pilots,
                         flight_attendants=flight_attendants,
                         required_pilots=required_pilots,
                         required_fas=required_fas,
                         current_pilots=current_pilots,
                         current_fas=current_fas,
                         is_long_haul=is_long_haul)


# ==================== PLANES MANAGEMENT ====================

@bp.route('/manager/planes', methods=['GET'])
def planes_list():
    """List all planes"""
    if not is_manager():
        flash('אין הרשאה לגשת לדף זה', 'error')
        return redirect(url_for('flights.search'))

    query = """
        SELECT p.plane_id, p.manufacturer, p.size_category, p.acquisition_date,
               COUNT(DISTINCT pc.class_type) as classes_count
        FROM Plane p
        LEFT JOIN PlaneClass pc ON p.plane_id = pc.plane_id
        GROUP BY p.plane_id, p.manufacturer, p.size_category, p.acquisition_date
        ORDER BY p.plane_id
    """
    planes = execute_query(query, fetch_all=True)

    return render_template('managers/planes_list.html', planes=planes)

@bp.route('/manager/planes/add', methods=['GET', 'POST'])
def plane_add():
    """Add new plane"""
    if not is_manager():
        flash('אין הרשאה לגשת לדף זה', 'error')
        return redirect(url_for('flights.search'))

    if request.method == 'POST':
        plane_id = request.form.get('plane_id')
        manufacturer = request.form.get('manufacturer')
        size_category = request.form.get('size_category')
        acquisition_date = request.form.get('acquisition_date')

        # Validate inputs
        if not all([plane_id, manufacturer, size_category, acquisition_date]):
            flash('כל השדות נדרשים', 'error')
            return redirect(url_for('managers.plane_add'))

        try:
            plane_id = int(plane_id)
        except ValueError:
            flash('מספר מטוס חייב להיות מספר', 'error')
            return redirect(url_for('managers.plane_add'))

        # Check if plane_id already exists
        check_query = "SELECT plane_id FROM Plane WHERE plane_id = %s"
        existing = execute_query(check_query, (plane_id,), fetch_one=True)
        if existing:
            flash(f'מטוס עם מספר {plane_id} כבר קיים במערכת', 'error')
            return redirect(url_for('managers.plane_add'))

        try:
            insert_query = """
                INSERT INTO Plane (plane_id, manufacturer, size_category, acquisition_date)
                VALUES (%s, %s, %s, %s)
            """
            execute_query(insert_query, (plane_id, manufacturer, size_category, acquisition_date), commit=True)
            flash('מטוס נוסף בהצלחה', 'success')
            return redirect(url_for('managers.plane_classes', plane_id=plane_id))

        except Exception as e:
            flash(f'שגיאה בהוספת מטוס: {str(e)}', 'error')

    return render_template('managers/plane_add.html')

@bp.route('/manager/planes/<int:plane_id>/classes', methods=['GET', 'POST'])
def plane_classes(plane_id):
    """Manage plane classes and generate seats"""
    if not is_manager():
        flash('אין הרשאה לגשת לדף זה', 'error')
        return redirect(url_for('flights.search'))

    # Check if plane exists
    plane_query = "SELECT * FROM Plane WHERE plane_id = %s"
    plane = execute_query(plane_query, (plane_id,), fetch_one=True)
    if not plane:
        flash('מטוס לא נמצא', 'error')
        return redirect(url_for('managers.planes_list'))

    if request.method == 'POST':
        class_type = request.form.get('class_type')
        rows_count = request.form.get('rows_count')
        cols_count = request.form.get('cols_count')

        if not all([class_type, rows_count, cols_count]):
            flash('כל השדות נדרשים', 'error')
            return redirect(url_for('managers.plane_classes', plane_id=plane_id))

        # Validate: Small planes can only have Economy class
        if class_type == 'Business' and plane['size_category'] == 'Small':
            flash('מטוסים קטנים יכולים לכלול רק מחלקת Economy', 'error')
            return redirect(url_for('managers.plane_classes', plane_id=plane_id))

        try:
            rows_count = int(rows_count)
            cols_count = int(cols_count)

            if rows_count <= 0 or cols_count <= 0:
                flash('מספר השורות והטורים חייב להיות חיובי', 'error')
                return redirect(url_for('managers.plane_classes', plane_id=plane_id))

            # Check if class already exists
            check_query = "SELECT * FROM PlaneClass WHERE plane_id = %s AND class_type = %s"
            existing = execute_query(check_query, (plane_id, class_type), fetch_one=True)

            if existing:
                flash(f'מחלקה {class_type} כבר קיימת למטוס זה', 'error')
                return redirect(url_for('managers.plane_classes', plane_id=plane_id))

            # Insert PlaneClass
            class_query = """
                INSERT INTO PlaneClass (plane_id, class_type, rows_count, cols_count)
                VALUES (%s, %s, %s, %s)
            """
            execute_query(class_query, (plane_id, class_type, rows_count, cols_count), commit=True)

            # Generate seats automatically
            # Column labels: A, B, C, D, E, F, etc.
            import string
            cols = list(string.ascii_uppercase[:cols_count])

            with db_transaction(commit=True) as db:
                seat_insert = "INSERT INTO Seat (plane_id, class_type, seat_number) VALUES (%s, %s, %s)"
                for row in range(1, rows_count + 1):
                    for col in cols:
                        seat_number = f"{row}{col}"
                        db.execute(seat_insert, (plane_id, class_type, seat_number))

            flash(f'מחלקה {class_type} נוספה בהצלחה עם {rows_count * cols_count} מושבים', 'success')
            return redirect(url_for('managers.plane_classes', plane_id=plane_id))

        except ValueError:
            flash('מספר שורות וטורים חייב להיות מספר', 'error')
        except Exception as e:
            flash(f'שגיאה בהוספת מחלקה: {str(e)}', 'error')

    # GET request - show current classes
    classes_query = """
        SELECT class_type, rows_count, cols_count,
               (SELECT COUNT(*) FROM Seat WHERE Seat.plane_id = PlaneClass.plane_id
                AND Seat.class_type = PlaneClass.class_type) as seats_count
        FROM PlaneClass
        WHERE plane_id = %s
        ORDER BY class_type
    """
    classes = execute_query(classes_query, (plane_id,), fetch_all=True)

    return render_template('managers/plane_classes.html', plane=plane, classes=classes)


# ==================== PILOTS MANAGEMENT ====================

@bp.route('/manager/pilots', methods=['GET'])
def pilots_list():
    """List all pilots"""
    if not is_manager():
        flash('אין הרשאה לגשת לדף זה', 'error')
        return redirect(url_for('flights.search'))

    query = """
        SELECT id_number, first_name_hebrew, last_name_hebrew, start_date,
               phone_number, is_long_haul_qualified
        FROM Pilot
        ORDER BY first_name_hebrew, last_name_hebrew
    """
    pilots = execute_query(query, fetch_all=True)

    return render_template('managers/pilots_list.html', pilots=pilots)

@bp.route('/manager/pilots/add', methods=['GET', 'POST'])
def pilot_add():
    """Add new pilot"""
    if not is_manager():
        flash('אין הרשאה לגשת לדף זה', 'error')
        return redirect(url_for('flights.search'))

    if request.method == 'POST':
        id_number = request.form.get('id_number')
        first_name_hebrew = request.form.get('first_name_hebrew')
        last_name_hebrew = request.form.get('last_name_hebrew')
        start_date = request.form.get('start_date')
        phone_number = request.form.get('phone_number')
        city = request.form.get('city', '')
        street = request.form.get('street', '')
        house_number = request.form.get('house_number', '')
        is_long_haul_qualified = request.form.get('is_long_haul_qualified') == 'on'

        # Validate required fields
        if not all([id_number, first_name_hebrew, last_name_hebrew, start_date, phone_number]):
            flash('שדות חובה: תעודת זהות, שם פרטי, שם משפחה, תאריך התחלה, טלפון', 'error')
            return redirect(url_for('managers.pilot_add'))

        # Validate ID number (9 digits)
        if not id_number.isdigit() or len(id_number) != 9:
            flash('תעודת זהות חייבת להכיל 9 ספרות', 'error')
            return redirect(url_for('managers.pilot_add'))

        # Check if pilot already exists
        check_query = "SELECT id_number FROM Pilot WHERE id_number = %s"
        existing = execute_query(check_query, (id_number,), fetch_one=True)
        if existing:
            flash(f'טייס עם תעודת זהות {id_number} כבר קיים במערכת', 'error')
            return redirect(url_for('managers.pilot_add'))

        try:
            insert_query = """
                INSERT INTO Pilot (id_number, first_name_hebrew, last_name_hebrew, start_date,
                                 phone_number, city, street, house_number, is_long_haul_qualified)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            execute_query(insert_query, (id_number, first_name_hebrew, last_name_hebrew, start_date,
                                        phone_number, city, street, house_number, is_long_haul_qualified), commit=True)
            flash('טייס נוסף בהצלחה', 'success')
            return redirect(url_for('managers.pilots_list'))

        except Exception as e:
            flash(f'שגיאה בהוספת טייס: {str(e)}', 'error')

    return render_template('managers/pilot_add.html')


# ==================== FLIGHT ATTENDANTS MANAGEMENT ====================

@bp.route('/manager/attendants', methods=['GET'])
def attendants_list():
    """List all flight attendants"""
    if not is_manager():
        flash('אין הרשאה לגשת לדף זה', 'error')
        return redirect(url_for('flights.search'))

    query = """
        SELECT id_number, first_name_hebrew, last_name_hebrew, start_date,
               phone_number, is_long_haul_qualified
        FROM FlightAttendant
        ORDER BY first_name_hebrew, last_name_hebrew
    """
    attendants = execute_query(query, fetch_all=True)

    return render_template('managers/attendants_list.html', attendants=attendants)

@bp.route('/manager/attendants/add', methods=['GET', 'POST'])
def attendant_add():
    """Add new flight attendant"""
    if not is_manager():
        flash('אין הרשאה לגשת לדף זה', 'error')
        return redirect(url_for('flights.search'))

    if request.method == 'POST':
        id_number = request.form.get('id_number')
        first_name_hebrew = request.form.get('first_name_hebrew')
        last_name_hebrew = request.form.get('last_name_hebrew')
        start_date = request.form.get('start_date')
        phone_number = request.form.get('phone_number')
        city = request.form.get('city', '')
        street = request.form.get('street', '')
        house_number = request.form.get('house_number', '')
        is_long_haul_qualified = request.form.get('is_long_haul_qualified') == 'on'

        # Validate required fields
        if not all([id_number, first_name_hebrew, last_name_hebrew, start_date, phone_number]):
            flash('שדות חובה: תעודת זהות, שם פרטי, שם משפחה, תאריך התחלה, טלפון', 'error')
            return redirect(url_for('managers.attendant_add'))

        # Validate ID number (9 digits)
        if not id_number.isdigit() or len(id_number) != 9:
            flash('תעודת זהות חייבת להכיל 9 ספרות', 'error')
            return redirect(url_for('managers.attendant_add'))

        # Check if attendant already exists
        check_query = "SELECT id_number FROM FlightAttendant WHERE id_number = %s"
        existing = execute_query(check_query, (id_number,), fetch_one=True)
        if existing:
            flash(f'דייל עם תעודת זהות {id_number} כבר קיים במערכת', 'error')
            return redirect(url_for('managers.attendant_add'))

        try:
            insert_query = """
                INSERT INTO FlightAttendant (id_number, first_name_hebrew, last_name_hebrew, start_date,
                                           phone_number, city, street, house_number, is_long_haul_qualified)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            execute_query(insert_query, (id_number, first_name_hebrew, last_name_hebrew, start_date,
                                        phone_number, city, street, house_number, is_long_haul_qualified), commit=True)
            flash('דייל נוסף בהצלחה', 'success')
            return redirect(url_for('managers.attendants_list'))

        except Exception as e:
            flash(f'שגיאה בהוספת דייל: {str(e)}', 'error')

    return render_template('managers/attendant_add.html')




