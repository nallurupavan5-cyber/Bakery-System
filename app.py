
import os
from flask import Flask
from extensions import db, migrate, login_manager
from config import Config


def create_app():
    """Factory that creates and configures the Flask application."""

    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Import application blueprints
    from routes import (
        admin,
        api,
        auth,
        baker,
        cashier,
        customer,
        inventory,
        manager
    )

    # Register all blueprints
    app.register_blueprint(admin.admin_bp)
    app.register_blueprint(api.api_bp)
    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(baker.baker_bp)
    app.register_blueprint(cashier.cashier_bp)
    app.register_blueprint(customer.customer_bp)
    app.register_blueprint(inventory.inventory_bp)
    app.register_blueprint(manager.manager_bp)

    return app


# Local development entry point
if __name__ == "__main__":
    app = create_app()

    port = int(os.getenv("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
