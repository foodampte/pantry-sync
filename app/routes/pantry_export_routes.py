from flask import Blueprint, Response, jsonify, request
from app.services.pantry_export_service import PantryExportService
from app.routes.pantry_routes import _store

bp = Blueprint("pantry_export", __name__, url_prefix="/pantry/export")


@bp.route("/csv", methods=["GET"])
def export_csv():
    """Export all pantry items as a CSV file download."""
    include_expired = request.args.get("include_expired", "true").lower() != "false"
    service = PantryExportService(_store)
    csv_data = service.export_csv(include_expired=include_expired)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=pantry_export.csv"},
    )


@bp.route("/json", methods=["GET"])
def export_json():
    """Export all pantry items as JSON."""
    include_expired = request.args.get("include_expired", "true").lower() != "false"
    service = PantryExportService(_store)
    items = service.export_json(include_expired=include_expired)
    return jsonify(items), 200
