from decimal import Decimal
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from extensions import db
from models.user import User, Staff, Customer
from models.product import Product, Category
from models.order import Order, Bill
from models.inventory import Ingredient
from models.supplier import Supplier
from models.settings import SystemSetting
from services.report_service import ReportService
from utils.decorators import role_required, ROLE_ADMIN
from utils.helpers import save_uploaded_file

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@admin_bp.route('/dashboard')
@role_required(ROLE_ADMIN)
def dashboard():
    summary = ReportService.get_dashboard_summary()
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(6).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    low_stock_items = Ingredient.query.filter(Ingredient.quantity_available <= Ingredient.reorder_level).all()

    return render_template(
        'admin/dashboard.html',
        summary=summary,
        recent_orders=recent_orders,
        recent_users=recent_users,
        low_stock_items=low_stock_items
    )


# ====================================================
# USER & STAFF MANAGEMENT
# ====================================================

@admin_bp.route('/users')
@role_required(ROLE_ADMIN)
def users():
    role_filter = request.args.get('role')
    search_query = request.args.get('search', '').strip()

    query = User.query
    if role_filter:
        query = query.filter(User.role == role_filter)
    if search_query:
        query = query.filter(User.username.ilike(f"%{search_query}%"))

    users_list = query.order_by(User.user_id.desc()).all()
    roles = ['Administrator', 'Manager', 'Cashier', 'Baker', 'Store Keeper', 'Customer']

    return render_template(
        'admin/users.html',
        users=users_list,
        roles=roles,
        selected_role=role_filter,
        search_query=search_query
    )


@admin_bp.route('/users/add', methods=['GET', 'POST'])
@role_required(ROLE_ADMIN)
def add_user():
    roles = ['Administrator', 'Manager', 'Cashier', 'Baker', 'Store Keeper', 'Customer']
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        name = request.form.get('name', '').strip()
        role = request.form.get('role', 'Customer')
        password = request.form.get('password', '')
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()

        if not username or not password or not name:
            flash('Username, full name, and password are required.', 'danger')
            return render_template('admin/user_form.html', roles=roles, user=None)

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('admin/user_form.html', roles=roles, user=None)

        user = User(username=username, role=role, active=True)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        if role == 'Customer':
            customer = Customer(user_id=user.user_id, name=name, phone=phone or 'N/A', email=email or None, address=address or None)
            db.session.add(customer)
        else:
            staff = Staff(
                user_id=user.user_id,
                name=name,
                role=role,
                phone=phone or 'N/A',
                username=username,
                password_hash=user.password_hash
            )
            db.session.add(staff)

        db.session.commit()
        flash(f"User '{username}' created successfully as '{role}'.", 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/user_form.html', roles=roles, user=None)


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@role_required(ROLE_ADMIN)
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    roles = ['Administrator', 'Manager', 'Cashier', 'Baker', 'Store Keeper', 'Customer']

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        role = request.form.get('role')
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        active = request.form.get('active') == '1'
        new_password = request.form.get('new_password', '').strip()

        user.role = role
        user.active = active

        if new_password:
            if len(new_password) < 6:
                flash('Password must be at least 6 characters.', 'danger')
                return render_template('admin/user_form.html', roles=roles, user=user)
            user.set_password(new_password)

        if user.customer_profile:
            user.customer_profile.name = name
            user.customer_profile.phone = phone
            user.customer_profile.email = email or None
            user.customer_profile.address = address or None
        elif user.staff_profile:
            user.staff_profile.name = name
            user.staff_profile.role = role
            user.staff_profile.phone = phone
            if new_password:
                user.staff_profile.password_hash = user.password_hash

        db.session.commit()
        flash(f"User '{user.username}' updated successfully.", 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/user_form.html', roles=roles, user=user)


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@role_required(ROLE_ADMIN)
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.user_id == current_user.user_id:
        flash('You cannot deactivate your own account.', 'warning')
        return redirect(url_for('admin.users'))

    user.active = not user.active
    db.session.commit()
    status_str = 'activated' if user.active else 'deactivated'
    flash(f"User '{user.username}' has been {status_str}.", 'info')
    return redirect(url_for('admin.users'))


# ====================================================
# PRODUCT & CATEGORY MANAGEMENT
# ====================================================

@admin_bp.route('/products')
@role_required(ROLE_ADMIN)
def products():
    search_query = request.args.get('search', '').strip()
    category_id = request.args.get('category')

    query = Product.query
    if search_query:
        query = query.filter(Product.name.ilike(f"%{search_query}%"))
    if category_id and category_id.isdigit():
        query = query.filter(Product.category_id == int(category_id))

    products_list = query.order_by(Product.name.asc()).all()
    categories = Category.query.filter_by(is_active=True).all()

    return render_template(
        'admin/products.html',
        products=products_list,
        categories=categories,
        search_query=search_query,
        selected_category=int(category_id) if category_id and category_id.isdigit() else None
    )


@admin_bp.route('/products/add', methods=['GET', 'POST'])
@role_required(ROLE_ADMIN)
def add_product():
    categories = Category.query.filter_by(is_active=True).all()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category_id = int(request.form.get('category_id'))
        price = Decimal(str(request.form.get('price', '0.00')))
        description = request.form.get('description', '').strip()
        availability = request.form.get('availability') == '1'

        image_path = None
        if 'image' in request.files and request.files['image'].filename:
            try:
                image_path = save_uploaded_file(request.files['image'], subfolder='products')
            except Exception as e:
                flash(f"Image upload warning: {str(e)}", 'warning')

        product = Product(
            name=name,
            category_id=category_id,
            price=price,
            description=description,
            image=image_path,
            availability=availability
        )
        db.session.add(product)
        db.session.commit()
        flash(f"Product '{name}' created successfully.", 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/product_form.html', categories=categories, product=None)


@admin_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@role_required(ROLE_ADMIN)
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.filter_by(is_active=True).all()

    if request.method == 'POST':
        product.name = request.form.get('name', '').strip()
        product.category_id = int(request.form.get('category_id'))
        product.price = Decimal(str(request.form.get('price', '0.00')))
        product.description = request.form.get('description', '').strip()
        product.availability = request.form.get('availability') == '1'

        if 'image' in request.files and request.files['image'].filename:
            try:
                uploaded = save_uploaded_file(request.files['image'], subfolder='products')
                if uploaded:
                    product.image = uploaded
            except Exception as e:
                flash(f"Image upload note: {str(e)}", 'warning')

        db.session.commit()
        flash(f"Product '{product.name}' updated successfully.", 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/product_form.html', categories=categories, product=product)


@admin_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@role_required(ROLE_ADMIN)
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    pname = product.name
    try:
        db.session.delete(product)
        db.session.commit()
        flash(f"Product '{pname}' deleted.", 'info')
    except Exception as e:
        db.session.rollback()
        flash(f"Cannot delete product with existing order history. You can mark it unavailable instead.", 'warning')

    return redirect(url_for('admin.products'))


@admin_bp.route('/categories', methods=['GET', 'POST'])
@role_required(ROLE_ADMIN)
def categories():
    if request.method == 'POST':
        action = request.form.get('action', 'add')
        if action == 'add':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            if not name:
                flash('Category name is required.', 'danger')
                return redirect(url_for('admin.categories'))

            cat = Category(name=name, description=description)
            db.session.add(cat)
            db.session.commit()
            flash(f"Category '{name}' created.", 'success')

        elif action == 'edit':
            cat_id = int(request.form.get('category_id'))
            cat = Category.query.get_or_404(cat_id)
            cat.name = request.form.get('name', '').strip()
            cat.description = request.form.get('description', '').strip()
            cat.is_active = request.form.get('is_active') == '1'
            db.session.commit()
            flash(f"Category '{cat.name}' updated.", 'success')

        elif action == 'delete':
            cat_id = int(request.form.get('category_id'))
            cat = Category.query.get_or_404(cat_id)
            cname = cat.name
            try:
                db.session.delete(cat)
                db.session.commit()
                flash(f"Category '{cname}' deleted.", 'info')
            except Exception as e:
                db.session.rollback()
                flash(f"Cannot delete category with active products.", 'danger')

        return redirect(url_for('admin.categories'))

    categories_list = Category.query.all()
    return render_template('admin/categories.html', categories=categories_list)


# ====================================================
# ORDERS & SETTINGS
# ====================================================

@admin_bp.route('/orders')
@role_required(ROLE_ADMIN)
def orders():
    status_filter = request.args.get('status')
    order_type = request.args.get('type')
    query = Order.query

    if status_filter:
        query = query.filter(Order.status == status_filter)
    if order_type:
        query = query.filter(Order.order_type == order_type)

    orders_list = query.order_by(Order.order_date.desc()).all()
    return render_template('admin/orders.html', orders=orders_list, selected_status=status_filter, selected_type=order_type)


@admin_bp.route('/settings', methods=['GET', 'POST'])
@role_required(ROLE_ADMIN)
def settings():
    if request.method == 'POST':
        SystemSetting.set_value('bakery_name', request.form.get('bakery_name', 'Sweet Delights Artisan Bakery'))
        SystemSetting.set_value('bakery_tagline', request.form.get('bakery_tagline', 'Freshly Baked, Made With Love'))
        SystemSetting.set_value('bakery_phone', request.form.get('bakery_phone', '+1 (555) 234-5678'))
        SystemSetting.set_value('bakery_email', request.form.get('bakery_email', 'contact@sweetdelightsbakery.com'))
        SystemSetting.set_value('bakery_address', request.form.get('bakery_address', '124 Sugarloaf Lane, Flour District'))
        SystemSetting.set_value('currency_symbol', request.form.get('currency_symbol', '$'))
        SystemSetting.set_value('default_tax_percent', request.form.get('default_tax_percent', '5.0'))
        SystemSetting.set_value('default_discount_percent', request.form.get('default_discount_percent', '0.0'))

        flash('System settings updated successfully.', 'success')
        return redirect(url_for('admin.settings'))

    settings_dict = {s.key: s.value for s in SystemSetting.query.all()}
    return render_template('admin/settings.html', settings=settings_dict)
