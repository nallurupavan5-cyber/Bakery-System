from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models.user import User, Customer, Staff
from utils.decorators import anonymous_only, ROLE_ADMIN, ROLE_MANAGER, ROLE_CASHIER, ROLE_BAKER, ROLE_STORE_KEEPER

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
@anonymous_only
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            if not user.active:
                flash('Your account has been deactivated. Please contact an administrator.', 'danger')
                return render_template('auth/login.html')

            login_user(user, remember=remember)
            flash(f'Welcome back, {user.username}!', 'success')

            # Redirect target
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)

            # Role-specific redirection
            if user.role == ROLE_ADMIN:
                return redirect(url_for('admin.dashboard'))
            elif user.role == ROLE_MANAGER:
                return redirect(url_for('manager.dashboard'))
            elif user.role == ROLE_CASHIER:
                return redirect(url_for('cashier.pos'))
            elif user.role == ROLE_BAKER:
                return redirect(url_for('baker.dashboard'))
            elif user.role == ROLE_STORE_KEEPER:
                return redirect(url_for('inventory.dashboard'))
            else:
                return redirect(url_for('customer.home'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
@anonymous_only
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        address = request.form.get('address', '').strip()

        # Validation
        if not username or not name or not phone or not password:
            flash('Please fill in all required fields.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash('Username is already taken. Please choose another.', 'danger')
            return render_template('auth/register.html')

        # Create user
        user = User(username=username, role='Customer', active=True)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        customer = Customer(
            user_id=user.user_id,
            name=name,
            phone=phone,
            email=email or None,
            address=address or None
        )
        db.session.add(customer)
        db.session.commit()

        login_user(user)
        flash('Account created successfully! Welcome to our bakery.', 'success')
        return redirect(url_for('customer.home'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out securely.', 'info')
    return redirect(url_for('customer.home'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    customer = current_user.customer_profile
    staff = current_user.staff_profile

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        new_password = request.form.get('new_password', '')

        if not name or not phone:
            flash('Name and phone number are required.', 'danger')
            return render_template('customer/profile.html', customer=customer, staff=staff)

        if customer:
            customer.name = name
            customer.phone = phone
            customer.email = email or None
            customer.address = address or None
        elif staff:
            staff.name = name
            staff.phone = phone

        if new_password:
            if len(new_password) < 6:
                flash('Password must be at least 6 characters long.', 'danger')
                return render_template('customer/profile.html', customer=customer, staff=staff)
            current_user.set_password(new_password)
            if staff:
                staff.password_hash = current_user.password_hash

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('customer/profile.html', customer=customer, staff=staff)
