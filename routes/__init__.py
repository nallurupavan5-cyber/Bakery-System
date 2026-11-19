from routes.auth import auth_bp
from routes.customer import customer_bp
from routes.admin import admin_bp
from routes.manager import manager_bp
from routes.cashier import cashier_bp
from routes.baker import baker_bp
from routes.inventory import inventory_bp
from routes.api import api_bp

__all__ = [
    'auth_bp',
    'customer_bp',
    'admin_bp',
    'manager_bp',
    'cashier_bp',
    'baker_bp',
    'inventory_bp',
    'api_bp'
]
