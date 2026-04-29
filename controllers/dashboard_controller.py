# controllers/dashboard_controller.py
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models.prediction import Prediction
from extensions.db import db  # ✅ योग्य import - extensions.db पासून
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard view"""
    # Get user's recent predictions
    recent_predictions = Prediction.get_user_predictions(current_user.id, limit=5)
    
    # Calculate statistics
    stats = get_dashboard_stats()
    
    # Get chart data
    chart_data = get_chart_data()
    
    return render_template(
        'dashboard/dashboard.html',
        predictions=recent_predictions,
        stats=stats,
        chart_data=chart_data
    )


@dashboard_bp.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for dashboard statistics"""
    stats = get_dashboard_stats()
    return jsonify({'status': 'success', 'stats': stats})


@dashboard_bp.route('/api/chart-data')
@login_required
def api_chart_data():
    """API endpoint for chart data"""
    data = get_chart_data()
    return jsonify({'status': 'success', 'data': data})


def get_dashboard_stats():
    """Calculate dashboard statistics"""
    
    # --- Total predictions ---
    total_predictions = Prediction.query.filter_by(
        user_id=current_user.id
    ).count()

    # --- Most common disease ---
    common_disease = db.session.query(
        Prediction.disease_name,
        func.count(Prediction.disease_name).label('count')
    ).filter_by(
        user_id=current_user.id
    ).group_by(
        Prediction.disease_name
    ).order_by(
        func.count(Prediction.disease_name).desc()
    ).first()

    # --- Healthy vs Diseased count ---
    healthy_count = Prediction.query.filter_by(
        user_id=current_user.id,
        disease_name='Healthy'
    ).count()

    diseased_count = total_predictions - healthy_count

    # --- Average confidence ---
    avg_confidence = db.session.query(
        func.avg(Prediction.confidence)
    ).filter_by(
        user_id=current_user.id
    ).scalar() or 0

    # --- Predictions this month ---
    first_day = datetime.utcnow().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    
    this_month = Prediction.query.filter(
        Prediction.user_id == current_user.id,
        Prediction.created_at >= first_day
    ).count()

    # --- Last 30 days ---
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    last_30_days = Prediction.query.filter(
        Prediction.user_id == current_user.id,
        Prediction.created_at >= thirty_days_ago
    ).count()

    # Calculate percentages (avoid division by zero)
    healthy_percent = 0
    diseased_percent = 0
    
    if total_predictions > 0:
        healthy_percent = round((healthy_count / total_predictions * 100), 1)
        diseased_percent = round((diseased_count / total_predictions * 100), 1)

    return {
        'total_predictions': total_predictions,
        'common_disease': common_disease[0] if common_disease else 'None',
        'common_disease_count': common_disease[1] if common_disease else 0,
        'healthy_count': healthy_count,
        'diseased_count': diseased_count,
        'healthy_percent': healthy_percent,
        'diseased_percent': diseased_percent,
        'avg_confidence': round(avg_confidence * 100, 1) if avg_confidence else 0,
        'this_month': this_month,
        'last_30_days': last_30_days
    }


def get_chart_data():
    """Get data for charts"""
    
    # --- Last 7 days data ---
    dates = []
    counts = []

    for i in range(6, -1, -1):
        date = datetime.utcnow().date() - timedelta(days=i)
        next_date = date + timedelta(days=1)

        count = Prediction.query.filter(
            Prediction.user_id == current_user.id,
            Prediction.created_at >= datetime.combine(date, datetime.min.time()),
            Prediction.created_at < datetime.combine(next_date, datetime.min.time())
        ).count()

        dates.append(date.strftime('%d %b'))
        counts.append(count)

    # --- Disease distribution (top 5) ---
    disease_dist = db.session.query(
        Prediction.disease_name,
        func.count(Prediction.disease_name).label('count')
    ).filter_by(
        user_id=current_user.id
    ).group_by(
        Prediction.disease_name
    ).order_by(
        func.count(Prediction.disease_name).desc()
    ).limit(5).all()

    # Format labels for display
    disease_names = []
    for d in disease_dist:
        if d[0] == 'Healthy':
            disease_names.append('🌿 Healthy Plant')
        elif d[0] == 'Rice_blast':
            disease_names.append('🔥 Leaf Blast')
        elif d[0] == 'Rice_brown_spot':
            disease_names.append('🟤 Brown Spot')
        elif d[0] == 'Rice_bacterial_blight':
            disease_names.append('🦠 Bacterial Blight')
        else:
            disease_names.append(d[0].replace('_', ' ').title())

    disease_counts = [d[1] for d in disease_dist]

    return {
        'daily': {
            'labels': dates,
            'data': counts
        },
        'distribution': {
            'labels': disease_names,
            'data': disease_counts
        }
    }