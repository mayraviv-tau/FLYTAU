"""
Reports routes
Handles management reports
"""
from flask import Blueprint, render_template
from database import execute_query
from utils.auth import is_manager
from flask import flash, redirect, url_for

bp = Blueprint('reports', __name__)

def read_sql_file(filename):
    """Read SQL file content"""
    import os
    # Go up from routes/ to app/ to project root, then to db/reports_sql/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.dirname(current_dir)
    project_root = os.path.dirname(app_dir)
    sql_path = os.path.join(project_root, 'db', 'reports_sql', filename)
    
    with open(sql_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Extract SQL query - remove comments
        # Find the actual SELECT statement
        lines = content.split('\n')
        sql_lines = []
        in_comment = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('/*'):
                in_comment = True
            if stripped.endswith('*/'):
                in_comment = False
                continue
            if in_comment:
                continue
            if stripped.startswith('--') or not stripped:
                continue
            sql_lines.append(line)
        return ' '.join(sql_lines).strip()

@bp.route('/')
def index():
    """Reports index page (managers only)"""
    if not is_manager():
        flash('אין הרשאה לגשת לדף זה', 'error')
        return redirect(url_for('flights.search'))
    
    return render_template('reports/index.html')

@bp.route('/occupancy')
def occupancy():
    """Report 1: Average Occupancy"""
    if not is_manager():
        flash('אין הרשאה לגשת לדף זה', 'error')
        return redirect(url_for('flights.search'))
    
    try:
        query = read_sql_file('report_1.sql')
        result = execute_query(query, fetch_one=True)
        
        if result:
            average_occupancy = result.get('average_system_occupancy', 0)
        else:
            average_occupancy = 0
        
        return render_template('reports/occupancy.html', average_occupancy=average_occupancy)
    except Exception as e:
        flash(f'שגיאה בטעינת הדוח: {str(e)}', 'error')
        return redirect(url_for('reports.index'))

@bp.route('/revenue')
def revenue():
    """Report 2: Revenue Analysis"""
    if not is_manager():
        flash('אין הרשאה לגשת לדף זה', 'error')
        return redirect(url_for('flights.search'))
    
    try:
        query = read_sql_file('report_2.sql')
        results = execute_query(query, fetch_all=True)
        
        return render_template('reports/revenue.html', results=results)
    except Exception as e:
        flash(f'שגיאה בטעינת הדוח: {str(e)}', 'error')
        return redirect(url_for('reports.index'))

@bp.route('/staff-hours')
def staff_hours():
    """Report 3: Staff Flight Hours"""
    if not is_manager():
        flash('אין הרשאה לגשת לדף זה', 'error')
        return redirect(url_for('flights.search'))
    
    try:
        query = read_sql_file('report_3.sql')
        results = execute_query(query, fetch_all=True)
        
        return render_template('reports/staff_hours.html', results=results)
    except Exception as e:
        flash(f'שגיאה בטעינת הדוח: {str(e)}', 'error')
        return redirect(url_for('reports.index'))

@bp.route('/cancellations')
def cancellations():
    """Report 4: Monthly Cancellation Rates"""
    if not is_manager():
        flash('אין הרשאה לגשת לדף זה', 'error')
        return redirect(url_for('flights.search'))
    
    try:
        query = read_sql_file('report_4.sql')
        results = execute_query(query, fetch_all=True)
        
        return render_template('reports/cancellations.html', results=results)
    except Exception as e:
        flash(f'שגיאה בטעינת הדוח: {str(e)}', 'error')
        return redirect(url_for('reports.index'))

@bp.route('/plane-activity')
def plane_activity():
    """Report 5: Monthly Plane Activity"""
    if not is_manager():
        flash('אין הרשאה לגשת לדף זה', 'error')
        return redirect(url_for('flights.search'))
    
    try:
        query = read_sql_file('report_5.sql')
        results = execute_query(query, fetch_all=True)
        
        return render_template('reports/plane_activity.html', results=results)
    except Exception as e:
        flash(f'שגיאה בטעינת הדוח: {str(e)}', 'error')
        return redirect(url_for('reports.index'))

@bp.route("/debug-session")
def debug_session():
    from flask import session
    return f"Session: {dict(session)}, is_manager: {is_manager()}"
