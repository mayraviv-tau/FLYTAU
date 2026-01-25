"""
Authentication routes
Handles login, register, logout for customers and managers
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import execute_query, db_transaction
from utils.auth import login_customer, login_manager, logout, verify_customer, verify_manager
from datetime import date

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register new customer"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()  # Normalize email
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        password = request.form.get('password', '')
        registration_date = date.today()  # Auto-set to current date
        birth_date = request.form.get('birth_date', '').strip()
        passport_number = request.form.get('passport_number', '').strip()
        phone_numbers = request.form.getlist('phone_number')

        # Validate required fields
        if not all([email, first_name, last_name, password, birth_date, passport_number]):
            flash('יש למלא את כל השדות הנדרשים', 'error')
            return render_template('auth/register.html')
        
        try:
            with db_transaction(commit=True) as db:
                # Check if customer already exists
                check_query = "SELECT email FROM Customer WHERE LOWER(email) = %s"
                db.execute(check_query, (email,))
                if db.fetchone():
                    flash('כתובת המייל כבר קיימת במערכת', 'error')
                    return render_template('auth/register.html')
                
                # Insert into Customer table
                customer_query = """
                    INSERT INTO Customer (email, first_name_english, last_name_english)
                    VALUES (%s, %s, %s)
                """
                db.execute(customer_query, (email, first_name, last_name))
                
                # Insert into RegisteredCustomer table (plain text password for university project)
                registered_query = """
                    INSERT INTO RegisteredCustomer 
                    (email, registration_date, birth_date, passport_number, account_password)
                    VALUES (%s, %s, %s, %s, %s)
                """
                db.execute(registered_query, (email, registration_date, birth_date, passport_number, password))
                
                # Insert phone numbers if provided
                if phone_numbers:
                    phone_query = "INSERT INTO CustomerPhone (email, phone_number) VALUES (%s, %s)"
                    for phone in phone_numbers:
                        if phone.strip():
                            db.execute(phone_query, (email, phone.strip()))
            
            flash('ההרשמה בוצעה בהצלחה! אנא התחבר', 'success')
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            flash(f'שגיאה בהרשמה: {str(e)}', 'error')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Customer login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()  # Normalize email
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('יש למלא כתובת מייל וסיסמה', 'error')
            return render_template('auth/login.html')
        
        if verify_customer(email, password):
            login_customer(email)
            flash('התחברת בהצלחה!', 'success')
            return redirect(url_for('flights.search'))
        else:
            flash('כתובת מייל או סיסמה לא נכונים', 'error')
    
    return render_template('auth/login.html')

@bp.route('/manager/login', methods=['GET', 'POST'])
def manager_login():
    """Manager login"""
    if request.method == 'POST':
        manager_id = request.form.get('manager_id')
        password = request.form.get('password')
        
        if not manager_id or not password:
            flash('יש למלא תעודת זהות וסיסמה', 'error')
            return render_template('auth/manager_login.html')
        
        if verify_manager(manager_id, password):
            login_manager(manager_id)
            flash('התחברת כמנהל בהצלחה!', 'success')
            return redirect(url_for('flights.list'))
        else:
            flash('תעודת זהות או סיסמה לא נכונים', 'error')
    
    return render_template('auth/manager_login.html')

@bp.route('/logout')
def logout_user():
    """Logout current user"""
    logout()
    flash('התנתקת בהצלחה', 'info')
    return redirect(url_for('auth.login'))
