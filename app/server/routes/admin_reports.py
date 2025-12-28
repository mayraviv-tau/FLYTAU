"""
Admin report routes for FLYTAU application.
Provides access to analytical reports for managers.
"""

from flask import Blueprint, jsonify
from ..services.report_service import (
    get_occupancy_report,
    get_revenue_report,
    get_staff_hours_report,
    get_cancellations_report,
    get_plane_activity_report
)
from ..middleware.auth import manager_required

bp = Blueprint('admin_reports', __name__)


@bp.route('/occupancy', methods=['GET'])
@manager_required
def occupancy_report():
    """
    Get average flight occupancy report.

    Returns:
        200: Occupancy report data
        401: Authentication required
        403: Manager access required
    """
    report = get_occupancy_report()

    return jsonify({
        'success': True,
        'data': report,
        'message': "Occupancy report generated successfully"
    }), 200


@bp.route('/revenue', methods=['GET'])
@manager_required
def revenue_report():
    """
    Get revenue analysis report.

    Returns:
        200: Revenue report data
        401: Authentication required
        403: Manager access required
    """
    report = get_revenue_report()

    return jsonify({
        'success': True,
        'data': report,
        'message': "Revenue report generated successfully"
    }), 200


@bp.route('/staff-hours', methods=['GET'])
@manager_required
def staff_hours_report():
    """
    Get staff flight hours report.

    Returns:
        200: Staff hours report data
        401: Authentication required
        403: Manager access required
    """
    report = get_staff_hours_report()

    return jsonify({
        'success': True,
        'data': report,
        'message': "Staff hours report generated successfully"
    }), 200


@bp.route('/cancellations', methods=['GET'])
@manager_required
def cancellations_report():
    """
    Get monthly cancellation rates report.

    Returns:
        200: Cancellations report data
        401: Authentication required
        403: Manager access required
    """
    report = get_cancellations_report()

    return jsonify({
        'success': True,
        'data': report,
        'message': "Cancellations report generated successfully"
    }), 200


@bp.route('/plane-activity', methods=['GET'])
@manager_required
def plane_activity_report():
    """
    Get monthly plane activity report.

    Returns:
        200: Plane activity report data
        401: Authentication required
        403: Manager access required
    """
    report = get_plane_activity_report()

    return jsonify({
        'success': True,
        'data': report,
        'message': "Plane activity report generated successfully"
    }), 200
