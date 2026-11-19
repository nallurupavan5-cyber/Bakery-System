import os
from flask import Flask, render_template, session
from config import Config
from extensions import db, login_manager
from models.settings import SystemSetting
from models.inventory import Ingredient
from utils.helpers import format_currency


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure uploads folder exists
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'static/uploads'), exist_ok=True)
    os.makedirs(os.path.join(app.config.get('UPLOAD_FOLDER', 'static/uploads'), 'products'), exist_ok=True)
    os.makedirs(os.path.join(app.config.get('UPLOAD_FOLDER', 'static/uploads'), 'custom_cakes'), exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.customer import customer_bp
    from routes.admin import admin_bp
    from routes.manager import manager_bp
    from routes.cashier import cashier_bp
    from routes.baker import baker_bp
    from routes.inventory import inventory_bp
    from routes.api import api_bp

    app.register_blueprint(customer_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(manager_bp)
    app.register_blueprint(cashier_bp)
    app.register_blueprint(baker_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(api_bp)

    # Context Processors & Filters
    @app.context_processor
    def inject_global_vars():
        cart = session.get('cart', {})
        cart_count = sum(cart.values()) if isinstance(cart, dict) else 0

        # Safe read of system settings
        try:
            b_name = SystemSetting.get_value('bakery_name', 'Sweet Delights Artisan Bakery')
            c_sym = SystemSetting.get_value('currency_symbol', '$')
            low_stock_c = Ingredient.query.filter(Ingredient.quantity_available <= Ingredient.reorder_level).count()
        except Exception:
            b_name = 'Sweet Delights Artisan Bakery'
            c_sym = '$'
            low_stock_c = 0

        return {
            'bakery_name': b_name,
            'currency_symbol': c_sym,
            'cart_item_count': cart_count,
            'global_low_stock_count': low_stock_c
        }

    @app.template_filter('currency')
    def currency_filter(val):
        return format_currency(val)

    # Error Handlers
    @app.errorhandler(400)
    def bad_request_error(error):
        return render_template('errors/400.html'), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        return render_template('errors/401.html'), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # Auto-init tables on startup
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.warning(f"Database auto-creation note: {e}")

    # Register CLI commands
    @app.cli.command("seed-db")
    def seed_db_command():
        """Seeds the database with realistic sample data."""
        from database.seed import seed_database
        seed_database(app)
        print("Database seeded successfully via CLI command!")

    return app


if __name__ == '__main__':
    application = create_app()
    # Auto-seed if not seeded
    with application.app_context():
        from models.user import User
        if not User.query.filter_by(username='admin').first():
            from database.seed import seed_database
            seed_database(application)

    print("=" * 60)
    print(" Sweet Delights Bakery Management System is running!")
    print(" Access at: http://127.0.0.1:5000")
    print(" Demo Logins:")
    print("   Administrator: admin / admin123")
    print("   Manager:       manager / manager123")
    print("   Cashier:       cashier / cashier123")
    print("   Baker:         baker / baker123")
    print("   Store Keeper:  store / store123")
    print("   Customer:      customer / customer123")
    print("=" * 60)
    application.run(host='0.0.0.0', port=5000, debug=True)
