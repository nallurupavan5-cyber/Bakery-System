import os
from datetime import datetime, date
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, send_file
from flask_login import current_user, login_required
from extensions import db
from models.product import Product, Category
from models.order import Order, OrderItem, Bill
from models.custom_cake import CustomCakeOrder
from models.user import Customer
from models.settings import SystemSetting
from services.order_service import OrderService
from services.billing_service import BillingService
from utils.helpers import save_uploaded_file, format_currency
from utils.pdf_generator import generate_invoice_pdf

customer_bp = Blueprint('customer', __name__)


def get_cart():
    return session.get('cart', {})


def save_cart(cart):
    session['cart'] = cart
    session.modified = True


@customer_bp.route('/')
def home():
    featured_products = Product.query.filter_by(availability=True).limit(4).all()
    popular_products = Product.query.filter_by(availability=True).offset(4).limit(4).all()
    if not popular_products:
        popular_products = featured_products
    categories = Category.query.filter_by(is_active=True).all()
    bakery_name = SystemSetting.get_value('bakery_name', 'Sweet Delights Artisan Bakery')
    return render_template(
        'customer/home.html',
        featured_products=featured_products,
        popular_products=popular_products,
        categories=categories,
        bakery_name=bakery_name
    )


@customer_bp.route('/menu')
def menu():
    search_query = request.args.get('search', '').strip()
    category_id = request.args.get('category')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    sort_by = request.args.get('sort', 'newest')
    availability = request.args.get('availability')

    query = Product.query

    if search_query:
        query = query.filter(Product.name.ilike(f"%{search_query}%") | Product.description.ilike(f"%{search_query}%"))

    if category_id and category_id.isdigit():
        query = query.filter(Product.category_id == int(category_id))

    if min_price:
        try:
            query = query.filter(Product.price >= float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            query = query.filter(Product.price <= float(max_price))
        except ValueError:
            pass

    if availability == '1':
        query = query.filter(Product.availability == True)
    elif availability == '0':
        query = query.filter(Product.availability == False)

    # Sorting
    if sort_by == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'name':
        query = query.order_by(Product.name.asc())
    else:  # newest
        query = query.order_by(Product.created_at.desc())

    products = query.all()
    categories = Category.query.filter_by(is_active=True).all()

    return render_template(
        'customer/menu.html',
        products=products,
        categories=categories,
        search_query=search_query,
        selected_category=int(category_id) if category_id and category_id.isdigit() else None,
        min_price=min_price or '',
        max_price=max_price or '',
        sort_by=sort_by,
        availability=availability or ''
    )


@customer_bp.route('/product/<int:product_id>')
def product_details(product_id):
    product = Product.query.get_or_404(product_id)
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.product_id != product.product_id,
        Product.availability == True
    ).limit(4).all()
    return render_template('customer/product_details.html', product=product, related_products=related_products)


# ====================================================
# CART MANAGEMENT
# ====================================================

@customer_bp.route('/cart')
def cart():
    cart_data = get_cart()
    cart_items = []
    subtotal = Decimal('0.00')

    for prod_id_str, qty in cart_data.items():
        prod = Product.query.get(int(prod_id_str))
        if prod:
            item_sub = prod.price * qty
            subtotal += item_sub
            cart_items.append({
                'product': prod,
                'quantity': qty,
                'subtotal': item_sub
            })

    # Calculate summary
    totals = BillingService.calculate_totals(
        [{'price': item['product'].price, 'quantity': item['quantity']} for item in cart_items]
    )

    return render_template(
        'customer/cart.html',
        cart_items=cart_items,
        totals=totals
    )


@customer_bp.route('/cart/add', methods=['POST'])
def cart_add():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))

    if quantity <= 0:
        quantity = 1

    product = Product.query.get_or_404(product_id)
    if not product.availability:
        flash(f"'{product.name}' is currently out of stock.", 'danger')
        return redirect(request.referrer or url_for('customer.menu'))

    cart = get_cart()
    current_qty = cart.get(str(product_id), 0)
    cart[str(product_id)] = current_qty + quantity
    save_cart(cart)

    flash(f"Added {quantity}x '{product.name}' to your cart!", 'success')
    return redirect(request.referrer or url_for('customer.cart'))


@customer_bp.route('/cart/update', methods=['POST'])
def cart_update():
    product_id = request.form.get('product_id')
    action = request.form.get('action')  # 'increase', 'decrease', 'set'
    quantity = request.form.get('quantity')

    cart = get_cart()
    pid = str(product_id)

    if pid in cart:
        if action == 'increase':
            cart[pid] += 1
        elif action == 'decrease':
            cart[pid] -= 1
            if cart[pid] <= 0:
                del cart[pid]
        elif action == 'set' and quantity:
            q = int(quantity)
            if q > 0:
                cart[pid] = q
            else:
                del cart[pid]

    save_cart(cart)
    flash('Cart updated.', 'info')
    return redirect(url_for('customer.cart'))


@customer_bp.route('/cart/remove/<int:product_id>', methods=['POST'])
def cart_remove(product_id):
    cart = get_cart()
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
        save_cart(cart)
        flash('Item removed from cart.', 'info')
    return redirect(url_for('customer.cart'))


@customer_bp.route('/cart/clear', methods=['POST'])
def cart_clear():
    save_cart({})
    flash('Cart emptied.', 'info')
    return redirect(url_for('customer.cart'))


# ====================================================
# CHECKOUT & ORDER PLACEMENT
# ====================================================

@customer_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart_data = get_cart()
    if not cart_data:
        flash('Your cart is empty. Please add items before checking out.', 'warning')
        return redirect(url_for('customer.menu'))

    # Prepare cart items
    items_list = []
    items_for_billing = []
    for prod_id_str, qty in cart_data.items():
        prod = Product.query.get(int(prod_id_str))
        if prod and prod.availability:
            items_list.append({'product': prod, 'quantity': qty, 'subtotal': prod.price * qty})
            items_for_billing.append({'product_id': prod.product_id, 'quantity': qty, 'price': prod.price})

    if not items_list:
        flash('The items in your cart are no longer available.', 'danger')
        save_cart({})
        return redirect(url_for('customer.menu'))

    totals = BillingService.calculate_totals(items_for_billing)

    # Pre-fill customer details if logged in
    customer = current_user.customer_profile if current_user.is_authenticated and current_user.customer_profile else None

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        payment_mode = request.form.get('payment_mode', 'Cash')
        special_instructions = request.form.get('special_instructions', '').strip()

        if not name or not phone:
            flash('Name and phone number are required.', 'danger')
            return render_template('customer/checkout.html', items=items_list, totals=totals, customer=customer)

        # Get or create customer record
        if customer:
            cust_id = customer.customer_id
            if address and not customer.address:
                customer.address = address
                db.session.commit()
        else:
            new_cust = Customer(name=name, phone=phone, email=email or None, address=address or None)
            db.session.add(new_cust)
            db.session.flush()
            cust_id = new_cust.customer_id

        # Place order
        try:
            payment_status = 'Paid' if payment_mode in ('Card', 'UPI') else 'Pending'
            order = OrderService.create_order(
                customer_id=cust_id,
                items_data=items_for_billing,
                order_type='Online Order',
                payment_mode=payment_mode,
                payment_status=payment_status,
                discount_percent=0.0,
                special_instructions=special_instructions,
                created_by_user_id=current_user.user_id if current_user.is_authenticated else None
            )

            # Clear cart
            save_cart({})
            flash(f"Order #{order.order_number} placed successfully! Thank you for your order.", 'success')
            return redirect(url_for('customer.order_tracking', order_number=order.order_number))
        except Exception as e:
            db.session.rollback()
            flash(f"Failed to place order: {str(e)}", 'danger')

    return render_template('customer/checkout.html', items=items_list, totals=totals, customer=customer)


# ====================================================
# CUSTOM CAKE MODULE
# ====================================================

@customer_bp.route('/custom-cake', methods=['GET', 'POST'])
def custom_cake():
    customer = current_user.customer_profile if current_user.is_authenticated and current_user.customer_profile else None

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        cake_type = request.form.get('cake_type', '').strip()
        flavour = request.form.get('flavour', '').strip()
        size = request.form.get('size', '').strip()
        quantity = int(request.form.get('quantity', 1))
        required_date_str = request.form.get('required_date', '').strip()
        required_time = request.form.get('required_time', '').strip()
        design_notes = request.form.get('design_notes', '').strip()
        special_instructions = request.form.get('special_instructions', '').strip()

        # Handle optional image upload
        image_path = None
        if 'image' in request.files and request.files['image'].filename:
            try:
                image_path = save_uploaded_file(request.files['image'], subfolder='custom_cakes')
            except Exception as e:
                flash(f"Image upload note: {str(e)}", 'warning')

        if not name or not phone or not cake_type or not flavour or not size or not required_date_str:
            flash('Please fill in all mandatory fields.', 'danger')
            return render_template('customer/custom_cake.html', customer=customer)

        try:
            req_date = datetime.strptime(required_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please select a valid date.', 'danger')
            return render_template('customer/custom_cake.html', customer=customer)

        if customer:
            cust_id = customer.customer_id
        else:
            new_cust = Customer(name=name, phone=phone, email=email or None)
            db.session.add(new_cust)
            db.session.flush()
            cust_id = new_cust.customer_id

        # Calculate an estimated base price based on size
        size_pricing = {
            '0.5 kg': Decimal('22.00'),
            '1.0 kg': Decimal('38.00'),
            '1.5 kg': Decimal('52.00'),
            '2.0 kg': Decimal('68.00'),
            '3.0 kg': Decimal('98.00'),
            '5.0 kg': Decimal('160.00'),
        }
        base_price = size_pricing.get(size, Decimal('45.00')) * quantity

        custom_order = OrderService.create_custom_cake_order(
            customer_id=cust_id,
            cake_type=cake_type,
            flavour=flavour,
            size=size,
            quantity=quantity,
            required_date=req_date,
            required_time=required_time,
            design_notes=design_notes,
            special_instructions=special_instructions,
            image_path=image_path,
            estimated_price=base_price
        )

        flash(f"Custom cake order request #{custom_order.custom_order_id} received! Our bakers will review and confirm shortly.", 'success')
        return redirect(url_for('customer.my_orders' if current_user.is_authenticated else 'customer.home'))

    return render_template('customer/custom_cake.html', customer=customer)


# ====================================================
# CUSTOMER ORDERS & TRACKING
# ====================================================

@customer_bp.route('/my-orders')
@login_required
def my_orders():
    customer = current_user.customer_profile
    if not customer:
        flash('No customer profile associated with this account.', 'info')
        return redirect(url_for('customer.home'))

    orders = Order.query.filter_by(customer_id=customer.customer_id).order_by(Order.order_date.desc()).all()
    custom_orders = CustomCakeOrder.query.filter_by(customer_id=customer.customer_id).order_by(CustomCakeOrder.created_at.desc()).all()

    return render_template('customer/my_orders.html', orders=orders, custom_orders=custom_orders)


@customer_bp.route('/orders/<int:order_id>')
def order_details(order_id):
    order = Order.query.get_or_404(order_id)
    # Check authorization if customer logged in
    if current_user.is_authenticated and current_user.role == 'Customer':
        if order.customer_id != current_user.customer_profile.customer_id:
            flash('Unauthorized to view this order.', 'danger')
            return redirect(url_for('customer.my_orders'))

    return render_template('customer/order_details.html', order=order)


@customer_bp.route('/track/<string:order_number>')
def order_tracking(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    statuses = ['Pending', 'Confirmed', 'Preparing', 'Ready', 'Delivered']
    current_step = statuses.index(order.status) if order.status in statuses else 0
    return render_template('customer/order_tracking.html', order=order, statuses=statuses, current_step=current_step)


@customer_bp.route('/invoices')
@login_required
def invoices():
    customer = current_user.customer_profile
    if not customer:
        flash('No customer profile found.', 'info')
        return redirect(url_for('customer.home'))

    bills = Bill.query.join(Order).filter(Order.customer_id == customer.customer_id).order_by(Bill.bill_date.desc()).all()
    return render_template('customer/invoices.html', bills=bills)


@customer_bp.route('/invoice/<int:order_id>/pdf')
def download_pdf_invoice(order_id):
    order = Order.query.get_or_404(order_id)
    if current_user.is_authenticated and current_user.role == 'Customer':
        if order.customer_id != current_user.customer_profile.customer_id:
            flash('Unauthorized.', 'danger')
            return redirect(url_for('customer.home'))

    pdf_buffer = generate_invoice_pdf(order)
    inv_name = order.bill.invoice_number if order.bill else f"Invoice_{order.order_number}"
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"{inv_name}.pdf",
        mimetype='application/pdf'
    )
