"""
Public routes for FLYTAU web UI.
Handles landing page, login, registration, and logout.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.server.services.auth_service import login_user, register_customer
from app.server.middleware.error_handlers import APIError

bp = Blueprint('public', __name__)


@bp.route('/')
def landing():
    """Landing page - redirect logged-in users to appropriate dashboard."""
    if 'user_id' in session:
        if session.get('user_type') == 'manager':
            return redirect(url_for('manager.dashboard'))
        return redirect(url_for('customer.dashboard'))
    return render_template('public/landing.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for both customers and managers."""
    if request.method == 'POST':
        try:
            user_type = request.form.get('user_type', 'customer')
            password = request.form.get('password', '')

            if user_type == 'manager':
                user_id = request.form.get('id_number', '')
            else:
                user_id = request.form.get('email', '')

            # Call existing auth service
            user_data = login_user(user_id, password, user_type)

            # Set session (same as API)
            session['user_id'] = user_data['user_id']
            session['user_type'] = user_data['user_type']
            session['first_name'] = user_data['first_name']
            session['last_name'] = user_data['last_name']
            session['is_registered'] = user_data.get('is_registered', True)

            flash('Login successful!', 'success')

            # Check for next_url redirect
            next_url = session.pop('next_url', None)
            if next_url:
                return redirect(next_url)

            # Redirect to appropriate dashboard
            if user_type == 'manager':
                return redirect(url_for('manager.dashboard'))
            return redirect(url_for('customer.dashboard'))

        except APIError as e:
            flash(e.message, 'error')
            return render_template('public/login.html', user_type=user_type)

    return render_template('public/login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Customer registration page."""
    if request.method == 'POST':
        try:
            # Extract form data
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            birth_date = request.form.get('birth_date', '') or None
            passport_number = request.form.get('passport_number', '').strip() or None
            phone_number = request.form.get('phone_number', '').strip()

            # Validate required fields
            if not all([email, password, first_name, last_name]):
                flash('Please fill in all required fields.', 'error')
                return render_template('public/register.html', form_data=request.form.to_dict())

            # Call registration service with individual arguments
            phone_numbers = [phone_number] if phone_number else None
            result = register_customer(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                birth_date=birth_date,
                passport_number=passport_number,
                phone_numbers=phone_numbers
            )

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('public.login'))

        except APIError as e:
            flash(e.message, 'error')
            return render_template('public/register.html', form_data=request.form.to_dict())

    return render_template('public/register.html')


@bp.route('/logout', methods=['POST'])
def logout():
    """Logout - clear session and redirect to landing."""
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('public.landing'))
