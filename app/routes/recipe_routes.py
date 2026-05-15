from flask import Blueprint, jsonify, request
from app.models.recipe import Recipe
from app.services.recipe_service import RecipeService

recipe_bp = Blueprint("recipes", __name__, url_prefix="/recipes")
_service = RecipeService()


@recipe_bp.route("/", methods=["GET"])
def list_recipes():
    return jsonify([r.to_dict() for r in _service.list_recipes()]), 200


@recipe_bp.route("/<recipe_id>", methods=["GET"])
def get_recipe(recipe_id):
    recipe = _service.get_recipe(recipe_id)
    if recipe is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(recipe.to_dict()), 200


@recipe_bp.route("/", methods=["POST"])
def create_recipe():
    data = request.get_json(force=True)
    try:
        recipe = Recipe.from_dict(data)
        _service.create_recipe(recipe)
    except (KeyError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409
    return jsonify(recipe.to_dict()), 201


@recipe_bp.route("/<recipe_id>", methods=["PATCH"])
def update_recipe(recipe_id):
    data = request.get_json(force=True)
    try:
        recipe = _service.update_recipe(recipe_id, data)
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    return jsonify(recipe.to_dict()), 200


@recipe_bp.route("/<recipe_id>/ingredients", methods=["POST"])
def add_ingredient(recipe_id):
    data = request.get_json(force=True)
    try:
        recipe = _service.add_ingredient(
            recipe_id,
            name=data["name"],
            quantity=float(data["quantity"]),
            unit=data["unit"],
        )
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    return jsonify(recipe.to_dict()), 200


@recipe_bp.route("/<recipe_id>", methods=["DELETE"])
def delete_recipe(recipe_id):
    try:
        _service.delete_recipe(recipe_id)
    except KeyError as exc:
        return jsonify({"error": str(exc)}), 404
    return "", 204
