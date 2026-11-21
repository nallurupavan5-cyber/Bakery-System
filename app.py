import os
from flask import Flask
from extensions import db, migrate, login_manager
from config import Config

def create_app():
    """Factory that creates and configures the Flask app."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialise extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register blueprints (adjust if you moved them)
    from routes import (
        admin, api, auth, baker, cashier,
        customer, inventory, manager
    )
    app.register_blueprint(admin.admin_bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(baker.bp)
    app.register_blueprint(cashier.bp)
    app.register_blueprint(customer.bp)
    app.register_blueprint(inventory.bp)
    app.register_blueprint(manager.bp)

    return app

# ----------------------------------------------------------------------
# Optional convenience for local development â€“ not used by Render
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # When you run `python app.py` locally you get the dev server.
    app = create_app()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

