from flask import Blueprint, request, jsonify
from app.services.pantry_import_service import PantryImportService
from app.routes.pantry_routes import pantry_store  # shared in-memory store

pantry_import_bp = Blueprint("pantry_import", __name__)


@pantry_import_bp.route("/pantry/import", methods=["POST"])
def bulk_import():
    """
    POST /pantry/import
    Body: JSON array of pantry-item objects.

    Returns 200 with an import summary, or 400 if the payload is invalid.
    """
    payload = request.get_json(silent=True)

    if not isinstance(payload, list):
        return jsonify({"error": "Request body must be a JSON array"}), 400

    service = PantryImportService(pantry_store)
    summary = service.import_items(payload)

    status = 200
    return jsonify(summary), status
