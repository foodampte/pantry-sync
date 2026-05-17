from flask import Blueprint, jsonify, request
from app.services.pantry_analytics_service import PantryAnalyticsService
from app.routes.pantry_routes import _store as pantry_store

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics/pantry")


@analytics_bp.get("")
def get_pantry_analytics():
    """Return analytics summary for the current pantry inventory."""
    try:
        days_window = int(request.args.get("days", 30))
        if days_window < 1 or days_window > 365:
            return jsonify({"error": "days must be between 1 and 365"}), 400
    except ValueError:
        return jsonify({"error": "days must be an integer"}), 400

    service = PantryAnalyticsService(pantry_store)
    return jsonify(service.get_analytics(days_window=days_window)), 200
