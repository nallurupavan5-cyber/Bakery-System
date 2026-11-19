from functools import wraps
from flask import abort, redirect, url_for, flash, request
from flask_login import current_user

ROLE_ADMIN = 'Administrator'
ROLE_MANAGER = 'Manager'
ROLE_CASHIER = 'Cashier'
ROLE_BAKER = 'Baker'
ROLE_STORE_KEEPER = 'Store Keeper'
ROLE_CUSTOMER = 'Customer'


def role_required(*allowed_roles):
    """
    Decorator to restrict view access to users with specified roles.
    If the user is unauthenticated, redirect to login page.
    If the user is authenticated but lacks required role, return 403 Forbidden.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))

            # Administrator has access to all internal staff modules
            user_role = current_user.role
            if user_role == ROLE_ADMIN:
                return f(*args, **kwargs)

            if user_role not in allowed_roles:
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def anonymous_only(f):
    """Decorator to redirect authenticated users away from login/register pages."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            # Redirect to their role-specific dashboard
            role = current_user.role
            if role == ROLE_ADMIN:
                return redirect(url_for('admin.dashboard'))
            elif role == ROLE_MANAGER:
                return redirect(url_for('manager.dashboard'))
            elif role == ROLE_CASHIER:
                return redirect(url_for('cashier.pos'))
            elif role == ROLE_BAKER:
                return redirect(url_for('baker.dashboard'))
            elif role == ROLE_STORE_KEEPER:
                return redirect(url_for('inventory.dashboard'))
            else:
                return redirect(url_for('customer.home'))
        return f(*args, **kwargs)
    return decorated_function
