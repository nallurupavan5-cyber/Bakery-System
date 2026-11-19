import json
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import current_user
from extensions import db
from models.product import Product, Category
from models.user import Customer
from models.order import Order, OrderItem, Bill
from models.settings import SystemSetting
from services.order_service import OrderService
from services.billing_service import BillingService
from utils.decorators import role_required, ROLE_CASHIER, ROLE_MANAGER, ROLE_ADMIN
from utils.pdf_generator import generate_invoice_pdf

cashier_bp = Blueprint('cashier', __name__, url_prefix='/cashier')


@cashier_bp.route('/pos')
@role_required(ROLE_CASHIER, ROLE_MANAGER, ROLE_ADMIN)
def pos():
    products = Product.query.filter_by(availability=True).order_by(Product.name.asc()).all()
    categories = Category.query.filter_by(is_active=True).all()
    customers = Customer.query.order_by(Customer.name.asc()).limit(50).all()

    tax_rate = float(SystemSetting.get_value('default_tax_percent', '5.0'))
    currency = SystemSetting.get_value('currency_symbol', '$')

    return render_template(
        'cashier/pos.html',
        products=products,
        categories=categories,
        customers=customers,
        tax_rate=tax_rate,
        currency=currency
    )


@cashier_bp.route('/pos/checkout', methods=['POST'])
@role_required(ROLE_CASHIER, ROLE_MANAGER, ROLE_ADMIN)
def pos_checkout():
    """Processes POS checkout form or JSON payload."""
    data = request.get_json(silent=True)
    if not data:
        # Fallback to form data
        data = request.form

    try:
        customer_type = data.get('customer_type', 'walkin')
        cust_id = None

        if customer_type == 'registered':
            cust_id = data.get('customer_id')
            if cust_id:
                cust_id = int(cust_id)
        elif customer_type == 'new':
            cname = data.get('new_customer_name', '').strip()
            cphone = data.get('new_customer_phone', '').strip()
            cemail = data.get('new_customer_email', '').strip()
            if cname and cphone:
                new_cust = Customer(name=cname, phone=cphone, email=cemail or None)
                db.session.add(new_cust)
                db.session.flush()
                cust_id = new_cust.customer_id

        # If walk-in or unresolved customer, link to walk-in customer record
        if not cust_id:
            walkin = Customer.query.filter_by(name='Walk-in Customer').first()
            if not walkin:
                walkin = Customer(name='Walk-in Customer', phone='000-0000', address='Storefront Counter')
                db.session.add(walkin)
                db.session.flush()
            cust_id = walkin.customer_id

        # Items
        items_raw = data.get('items')
        if isinstance(items_raw, str):
            items_raw = json.loads(items_raw)

        if not items_raw:
            return jsonify({'success': False, 'message': 'Billing cart is empty.'}), 400

        items_data = []
        for it in items_raw:
            items_data.append({
                'product_id': int(it['product_id']),
                'quantity': int(it['quantity']),
                'price': Decimal(str(it['price']))
            })

        discount_amount = float(data.get('discount_amount', 0.0))
        discount_percent = float(data.get('discount_percent', 0.0))
        tax_percent = float(data.get('tax_percent', SystemSetting.get_value('default_tax_percent', '5.0')))
        payment_mode = data.get('payment_mode', 'Cash')
        payment_status = data.get('payment_status', 'Paid')
        special_instructions = data.get('notes', 'Walk-in POS Sale')

        order = OrderService.create_order(
            customer_id=cust_id,
            items_data=items_data,
            order_type='Walk-in Order',
            payment_mode=payment_mode,
            payment_status=payment_status,
            discount_percent=discount_percent,
            discount_amount=discount_amount,
            tax_percent=tax_percent,
            special_instructions=special_instructions,
            created_by_user_id=current_user.user_id
        )

        return jsonify({
            'success': True,
            'order_id': order.order_id,
            'order_number': order.order_number,
            'invoice_number': order.bill.invoice_number if order.bill else '',
            'total': float(order.total_amount),
            'invoice_url': url_for('cashier.invoice_view', order_id=order.order_id)
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400


@cashier_bp.route('/invoice/<int:order_id>')
@role_required(ROLE_CASHIER, ROLE_MANAGER, ROLE_ADMIN)
def invoice_view(order_id):
    order = Order.query.get_or_404(order_id)
    bakery_name = SystemSetting.get_value('bakery_name', 'Sweet Delights Artisan Bakery')
    bakery_phone = SystemSetting.get_value('bakery_phone', '+1 (555) 234-5678')
    bakery_email = SystemSetting.get_value('bakery_email', 'contact@sweetdelightsbakery.com')
    bakery_address = SystemSetting.get_value('bakery_address', '124 Sugarloaf Lane, Flour District')
    currency = SystemSetting.get_value('currency_symbol', '$')

    return render_template(
        'cashier/invoice_view.html',
        order=order,
        bakery_name=bakery_name,
        bakery_phone=bakery_phone,
        bakery_email=bakery_email,
        bakery_address=bakery_address,
        currency=currency
    )


@cashier_bp.route('/orders')
@role_required(ROLE_CASHIER, ROLE_MANAGER, ROLE_ADMIN)
def orders():
    status_filter = request.args.get('status')
    order_type = request.args.get('type')
    query = Order.query

    if status_filter:
        query = query.filter(Order.status == status_filter)
    if order_type:
        query = query.filter(Order.order_type == order_type)

    orders = query.order_by(Order.order_date.desc()).all()
    return render_template('cashier/orders.html', orders=orders, selected_status=status_filter, selected_type=order_type)


@cashier_bp.route('/invoices')
@role_required(ROLE_CASHIER, ROLE_MANAGER, ROLE_ADMIN)
def invoices():
    bills = Bill.query.order_by(Bill.bill_date.desc()).all()
    return render_template('cashier/invoices.html', bills=bills)


@cashier_bp.route('/transactions')
@role_required(ROLE_CASHIER, ROLE_MANAGER, ROLE_ADMIN)
def transactions():
    bills = Bill.query.order_by(Bill.bill_date.desc()).all()
    total_paid = sum(b.total for b in bills if b.payment_status == 'Paid')
    return render_template('cashier/transactions.html', bills=bills, total_paid=total_paid)
