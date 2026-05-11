from flask import Blueprint, jsonify, request
from app.models.meal_plan import MealPlan, MealPlanItem

meal_plan_bp = Blueprint("meal_plans", __name__, url_prefix="/meal-plans")

_store: dict[str, MealPlan] = {}


@meal_plan_bp.route("/", methods=["GET"])
def list_plans():
    return jsonify([p.to_dict() for p in _store.values()]), 200


@meal_plan_bp.route("/<plan_id>", methods=["GET"])
def get_plan(plan_id: str):
    plan = _store.get(plan_id)
    if not plan:
        return jsonify({"error": "Meal plan not found"}), 404
    return jsonify(plan.to_dict()), 200


@meal_plan_bp.route("/", methods=["POST"])
def create_plan():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    required = {"plan_id", "meal_name", "scheduled_date"}
    if not required.issubset(data):
        return jsonify({"error": f"Missing fields: {required - data.keys()}"}), 400
    if data["plan_id"] in _store:
        return jsonify({"error": "Meal plan already exists"}), 409
    try:
        plan = MealPlan.from_dict(data)
    except (KeyError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 422
    _store[plan.plan_id] = plan
    return jsonify(plan.to_dict()), 201


@meal_plan_bp.route("/<plan_id>/ingredients", methods=["POST"])
def add_ingredient(plan_id: str):
    plan = _store.get(plan_id)
    if not plan:
        return jsonify({"error": "Meal plan not found"}), 404
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    try:
        item = MealPlanItem.from_dict(data)
    except (KeyError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 422
    plan.add_ingredient(item)
    return jsonify(plan.to_dict()), 200


@meal_plan_bp.route("/<plan_id>", methods=["DELETE"])
def delete_plan(plan_id: str):
    if plan_id not in _store:
        return jsonify({"error": "Meal plan not found"}), 404
    del _store[plan_id]
    return "", 204


def _get_store() -> dict:
    """Expose internal store for testing."""
    return _store
