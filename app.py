
import os
from decimal import Decimal, InvalidOperation
from flask import Flask, current_app
from extensions import db, migrate, login_manager
from config import Config


def currency_filter(value):
    """Format a number as currency."""
    try:
        amount = Decimal(str(value or 0))
    except (InvalidOperation, ValueError, TypeError):
        amount = Decimal("0.00")

    symbol = current_app.config.get("CURRENCY_SYMBOL", "$")

    return f"{symbol}{amount:,.2f}"


def create_app():
    """Factory that creates and configures the Flask application."""

    app = Flask(__name__)
    app.config.from_object(Config)

    # Register custom Jinja filters
    app.jinja_env.filters["currency"] = currency_filter

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Import all database models
    from models.user import User, Staff, Customer
    from models.product import Product, Category
    from models.order import Order, Bill
    from models.inventory import Ingredient
    from models.supplier import Supplier
    from models.settings import SystemSetting

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

    # Create missing database tables
    with app.app_context():
        db.create_all()

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
