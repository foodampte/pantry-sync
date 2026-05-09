from flask import Blueprint, jsonify, request
from app.models.pantry_item import PantryItem
from datetime import datetime

pantry_bp = Blueprint("pantry", __name__, url_prefix="/pantry")

# In-memory store for now; replace with DB layer later
_pantry: dict[str, PantryItem] = {}


@pantry_bp.get("/")
def list_items():
    """Return all pantry items."""
    return jsonify([item.to_dict() for item in _pantry.values()]), 200


@pantry_bp.get("/<item_id>")
def get_item(item_id: str):
    """Return a single pantry item by ID."""
    item = _pantry.get(item_id)
    if item is None:
        return jsonify({"error": f"Item '{item_id}' not found"}), 404
    return jsonify(item.to_dict()), 200


@pantry_bp.post("/")
def create_item():
    """Add a new pantry item."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    try:
        item = PantryItem.from_dict(data)
    except (KeyError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 422
    if item.id in _pantry:
        return jsonify({"error": f"Item '{item.id}' already exists"}), 409
    _pantry[item.id] = item
    return jsonify(item.to_dict()), 201


@pantry_bp.put("/<item_id>")
def update_item(item_id: str):
    """Replace an existing pantry item."""
    if item_id not in _pantry:
        return jsonify({"error": f"Item '{item_id}' not found"}), 404
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    data["id"] = item_id  # ensure path param wins
    try:
        item = PantryItem.from_dict(data)
    except (KeyError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 422
    _pantry[item_id] = item
    return jsonify(item.to_dict()), 200


@pantry_bp.delete("/<item_id>")
def delete_item(item_id: str):
    """Remove a pantry item."""
    if item_id not in _pantry:
        return jsonify({"error": f"Item '{item_id}' not found"}), 404
    _pantry.pop(item_id)
    return "", 204


@pantry_bp.get("/alerts/low-stock")
def low_stock_alerts():
    """Return items that are at or below their low-stock threshold."""
    low = [item.to_dict() for item in _pantry.values() if item.is_low_stock()]
    return jsonify(low), 200


@pantry_bp.get("/alerts/expired")
def expired_alerts():
    """Return items that are past their expiry date."""
    expired = [item.to_dict() for item in _pantry.values() if item.is_expired()]
    return jsonify(expired), 200
