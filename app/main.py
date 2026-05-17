from flask import Flask


def create_app() -> Flask:
    app = Flask(__name__)

    from app.routes.pantry_routes import pantry_bp
    from app.routes.meal_plan_routes import meal_plan_bp
    from app.routes.shopping_list_routes import shopping_list_bp
    from app.routes.expiry_alert_routes import expiry_alert_bp
    from app.routes.recipe_routes import recipe_bp
    from app.routes.recipe_suggestion_routes import recipe_suggestion_bp
    from app.routes.pantry_summary_routes import pantry_summary_bp
    from app.routes.pantry_import_routes import pantry_import_bp
    from app.routes.pantry_export_routes import pantry_export_bp
    from app.routes.pantry_analytics_routes import pantry_analytics_bp
    from app.routes.pantry_history_routes import pantry_history_bp

    app.register_blueprint(pantry_bp)
    app.register_blueprint(meal_plan_bp)
    app.register_blueprint(shopping_list_bp)
    app.register_blueprint(expiry_alert_bp)
    app.register_blueprint(recipe_bp)
    app.register_blueprint(recipe_suggestion_bp)
    app.register_blueprint(pantry_summary_bp)
    app.register_blueprint(pantry_import_bp)
    app.register_blueprint(pantry_export_bp)
    app.register_blueprint(pantry_analytics_bp)
    app.register_blueprint(pantry_history_bp)

    return app
