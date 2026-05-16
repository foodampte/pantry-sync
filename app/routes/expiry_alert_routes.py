from flask import Blueprint, jsonify, request
from app.services.expiry_alert_service import ExpiryAlertService
from app.models.pantry_item import PantryItem

# In-process store shared with pantry_routes
from app.routes.pantry_routes import _store as pantry_store

bp = Blueprint("expiry_alerts", __name__, url_prefix="/expiry-alerts")

MAX_WARNING_DAYS = 365


@bp.get("/")
def get_expiry_alerts():
    """Return expired and expiring-soon items.

    Optional query param: warning_days (int, default 7)
    """
    try:
        warning_days = int(request.args.get("warning_days", 7))
        if warning_days < 0:
            return jsonify({"error": "warning_days must be non-negative"}), 400
        if warning_days > MAX_WARNING_DAYS:
            return jsonify({"error": f"warning_days must not exceed {MAX_WARNING_DAYS}"}), 400
    except ValueError:
        return jsonify({"error": "warning_days must be an integer"}), 400

    items: list[PantryItem] = list(pantry_store.values())
    service = ExpiryAlertService(warning_days=warning_days)
    alerts = service.get_alerts(items)
    return jsonify(alerts), 200
