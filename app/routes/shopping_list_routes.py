from flask import Blueprint, jsonify, request
from app.services.shopping_list_service import ShoppingListService
from app.models.meal_plan import MealPlan
from app.models.pantry_item import PantryItem

shopping_list_bp = Blueprint("shopping_list", __name__, url_prefix="/shopping-list")

# In-memory stores (shared references — in real app, inject via DI or app context)
from app.routes.pantry_routes import pantry_store
from app.routes.meal_plan_routes import meal_plan_store

service = ShoppingListService()


@shopping_list_bp.route("/generate", methods=["GET"])
def generate_shopping_list():
    """Generate a shopping list based on all meal plans and current pantry."""
    plan_ids = request.args.getlist("plan_id")

    if plan_ids:
        selected_plans = [
            meal_plan_store[pid] for pid in plan_ids if pid in meal_plan_store
        ]
        missing_ids = [pid for pid in plan_ids if pid not in meal_plan_store]
        if missing_ids:
            return jsonify({"error": f"Plans not found: {missing_ids}"}), 404
    else:
        selected_plans = list(meal_plan_store.values())

    if not selected_plans:
        return jsonify({"shopping_list": [], "message": "No meal plans available."}), 200

    pantry_items = list(pantry_store.values())
    shopping_list = service.generate(selected_plans, pantry_items)

    return jsonify({
        "shopping_list": shopping_list,
        "plan_count": len(selected_plans),
        "item_count": len(shopping_list),
    }), 200


@shopping_list_bp.route("/generate/<plan_id>", methods=["GET"])
def generate_for_plan(plan_id):
    """Generate a shopping list for a single meal plan."""
    if plan_id not in meal_plan_store:
        return jsonify({"error": "Meal plan not found"}), 404

    pantry_items = list(pantry_store.values())
    shopping_list = service.generate([meal_plan_store[plan_id]], pantry_items)

    return jsonify({
        "plan_id": plan_id,
        "shopping_list": shopping_list,
        "item_count": len(shopping_list),
    }), 200
