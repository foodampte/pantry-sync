from flask import Flask


def create_app(testing: bool = False) -> Flask:
    app = Flask(__name__)
    app.config["TESTING"] = testing

    from app.routes.pantry_routes import pantry_bp
    from app.routes.meal_plan_routes import meal_plan_bp

    app.register_blueprint(pantry_bp)
    app.register_blueprint(meal_plan_bp)

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True)
