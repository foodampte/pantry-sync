from flask import Blueprint, jsonify, request
from app.services.pantry_history_service import PantryHistoryService

pantry_history_bp = Blueprint("pantry_history", __name__)
_service = PantryHistoryService()


def get_service() -> PantryHistoryService:
    return _service


@pantry_history_bp.route("/pantry/history", methods=["GET"])
def list_history():
    """Return pantry change history, optionally filtered by item_name or action."""
    svc = get_service()
    item_name = request.args.get("item_name")
    action = request.args.get("action")
    valid_actions = {"added", "updated", "removed", "consumed"}
    if action and action not in valid_actions:
        return jsonify({"error": f"Invalid action. Must be one of: {', '.join(sorted(valid_actions))}"}), 400
    entries = svc.get_history(item_name=item_name, action=action)
    return jsonify(entries), 200


@pantry_history_bp.route("/pantry/history/<string:item_name>", methods=["GET"])
def item_history(item_name: str):
    """Return history for a specific pantry item."""
    svc = get_service()
    entries = svc.get_history(item_name=item_name)
    return jsonify(entries), 200
