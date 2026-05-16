from flask import Blueprint, jsonify
from app.services.pantry_summary_service import PantrySummaryService
from app.routes.pantry_routes import pantry_store

summary_bp = Blueprint("summary", __name__, url_prefix="/pantry/summary")


@summary_bp.route("", methods=["GET"])
def get_pantry_summary():
    """Return a high-level overview of the pantry state."""
    service = PantrySummaryService(pantry_store)
    summary = service.get_summary()
    return jsonify(summary), 200
