from flask import Blueprint, jsonify, request
from app.services.recipe_suggestion_service import RecipeSuggestionService
from app.services.recipe_service import RecipeService
from app.routes.pantry_routes import _pantry_store
from app.routes.recipe_routes import _recipe_store

bp = Blueprint("recipe_suggestions", __name__, url_prefix="/suggestions")


@bp.route("/", methods=["GET"])
def suggest_recipes():
    """GET /suggestions/?max_missing=<int>

    Returns recipes sorted by how achievable they are with current pantry.
    """
    try:
        max_missing = int(request.args.get("max_missing", 0))
    except ValueError:
        return jsonify({"error": "max_missing must be an integer"}), 400

    if max_missing < 0:
        return jsonify({"error": "max_missing must be >= 0"}), 400

    service = RecipeSuggestionService(
        recipe_store=_recipe_store,
        pantry_store=_pantry_store,
    )
    suggestions = service.suggest(max_missing=max_missing)
    return jsonify(suggestions), 200
