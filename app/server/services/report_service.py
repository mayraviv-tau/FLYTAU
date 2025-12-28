"""
Report service for FLYTAU application.
Executes SQL reports for administrative analytics.
"""

import os
from ..db import execute_query


def execute_sql_report(report_file_path):
    """
    Execute a SQL report from a file.

    Args:
        report_file_path (str): Path to SQL file

    Returns:
        list: Query results

    Raises:
        FileNotFoundError: If SQL file not found
    """
    if not os.path.exists(report_file_path):
        raise FileNotFoundError(f"Report file not found: {report_file_path}")

    # Read SQL file
    with open(report_file_path, 'r', encoding='utf-8') as f:
        sql_query = f.read()

    # Execute query
    results = execute_query(sql_query, fetch_all=True)

    return results or []


def get_all_reports():
    """
    Get all available reports with their metadata.

    Returns:
        dict: Report metadata
    """
    # Get project root (3 levels up from this file)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    reports_dir = os.path.join(project_root, 'db', 'reports_sql')

    return {
        'report_1': {
            'name': 'Average Flight Occupancy',
            'description': 'Average occupancy percentage for completed flights',
            'path': os.path.join(reports_dir, 'report_1.sql')
        },
        'report_2': {
            'name': 'Revenue Analysis',
            'description': 'Revenue breakdown by plane size, manufacturer, and class',
            'path': os.path.join(reports_dir, 'report_2.sql')
        },
        'report_3': {
            'name': 'Staff Flight Hours',
            'description': 'Accumulated flight hours for pilots and flight attendants',
            'path': os.path.join(reports_dir, 'report_3.sql')
        },
        'report_4': {
            'name': 'Monthly Cancellation Rates',
            'description': 'Percentage of canceled orders per month',
            'path': os.path.join(reports_dir, 'report_4.sql')
        },
        'report_5': {
            'name': 'Monthly Plane Activity',
            'description': 'Plane utilization and activity metrics per month',
            'path': os.path.join(reports_dir, 'report_5.sql')
        }
    }


def get_occupancy_report():
    """Execute occupancy report (report_1)."""
    reports = get_all_reports()
    results = execute_sql_report(reports['report_1']['path'])
    return {
        'report_name': reports['report_1']['name'],
        'description': reports['report_1']['description'],
        'data': results
    }


def get_revenue_report():
    """Execute revenue report (report_2)."""
    reports = get_all_reports()
    results = execute_sql_report(reports['report_2']['path'])
    return {
        'report_name': reports['report_2']['name'],
        'description': reports['report_2']['description'],
        'data': results
    }


def get_staff_hours_report():
    """Execute staff hours report (report_3)."""
    reports = get_all_reports()
    results = execute_sql_report(reports['report_3']['path'])
    return {
        'report_name': reports['report_3']['name'],
        'description': reports['report_3']['description'],
        'data': results
    }


def get_cancellations_report():
    """Execute cancellations report (report_4)."""
    reports = get_all_reports()
    results = execute_sql_report(reports['report_4']['path'])
    return {
        'report_name': reports['report_4']['name'],
        'description': reports['report_4']['description'],
        'data': results
    }


def get_plane_activity_report():
    """Execute plane activity report (report_5)."""
    reports = get_all_reports()
    results = execute_sql_report(reports['report_5']['path'])
    return {
        'report_name': reports['report_5']['name'],
        'description': reports['report_5']['description'],
        'data': results
    }
