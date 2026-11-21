from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models.order import Order
from models.custom_cake import CustomCakeOrder
from services.order_service import OrderService
from utils.decorators import role_required, ROLE_BAKER, ROLE_MANAGER, ROLE_ADMIN

baker_bp = Blueprint('baker', __name__, url_prefix='/baker')


@baker_bp.route('/')
@baker_bp.route('/dashboard')
@role_required(ROLE_BAKER, ROLE_MANAGER, ROLE_ADMIN)
def dashboard():
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)

    today_orders = Order.query.filter(Order.order_date >= today_start, Order.status != 'Cancelled').all()
    new_orders = Order.query.filter(Order.status == 'Pending').order_by(Order.order_date.asc()).all()
    preparing_orders = Order.query.filter(Order.status.in_(['Confirmed', 'Preparing'])).order_by(Order.order_date.asc()).all()
    ready_orders = Order.query.filter(Order.status == 'Ready').order_by(Order.order_date.asc()).all()
    custom_cakes = CustomCakeOrder.query.filter(CustomCakeOrder.status.in_(['Pending', 'Confirmed', 'Preparing'])).order_by(CustomCakeOrder.required_date.asc()).all()

    return render_template(
        'baker/dashboard.html',
        today_orders=today_orders,
        new_orders=new_orders,
        preparing_orders=preparing_orders,
        ready_orders=ready_orders,
        custom_cakes=custom_cakes
    )


@baker_bp.route('/order/<int:order_id>/status', methods=['POST'])
@role_required(ROLE_BAKER, ROLE_MANAGER, ROLE_ADMIN)
def update_order_status(order_id):
    new_status = request.form.get('status')
    try:
        order = OrderService.update_order_status(order_id, new_status)
        flash(f"Order #{order.order_number} marked as '{new_status}'.", 'success')
    except Exception as e:
        flash(f"Error updating order status: {str(e)}", 'danger')

    return redirect(request.referrer or url_for('baker.dashboard'))


@baker_bp.route('/custom-cakes')
@role_required(ROLE_BAKER, ROLE_MANAGER, ROLE_ADMIN)
def custom_cakes():
    custom_orders = CustomCakeOrder.query.order_by(CustomCakeOrder.required_date.asc()).all()
    return render_template('baker/custom_cakes.html', custom_orders=custom_orders)


@baker_bp.route('/custom-cake/<int:custom_order_id>/status', methods=['POST'])
@role_required(ROLE_BAKER, ROLE_MANAGER, ROLE_ADMIN)
def update_custom_cake_status(custom_order_id):
    new_status = request.form.get('status')
    try:
        custom_order = OrderService.update_custom_cake_status(custom_order_id, new_status)
        flash(f"Custom cake #{custom_order.custom_order_id} marked as '{new_status}'.", 'success')
    except Exception as e:
        flash(f"Error updating custom cake status: {str(e)}", 'danger')

    return redirect(request.referrer or url_for('baker.custom_cakes'))
