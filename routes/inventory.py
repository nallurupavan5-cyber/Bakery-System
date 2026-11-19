from decimal import Decimal
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from extensions import db
from models.inventory import Ingredient, InventoryTransaction
from models.supplier import Supplier
from services.inventory_service import InventoryService
from utils.decorators import role_required, ROLE_STORE_KEEPER, ROLE_MANAGER, ROLE_ADMIN

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')


@inventory_bp.route('/')
@inventory_bp.route('/dashboard')
@role_required(ROLE_STORE_KEEPER, ROLE_MANAGER, ROLE_ADMIN)
def dashboard():
    search_query = request.args.get('search', '').strip()
    low_stock_only = request.args.get('low_stock') == '1'

    query = Ingredient.query
    if search_query:
        query = query.filter(Ingredient.name.ilike(f"%{search_query}%"))
    if low_stock_only:
        query = query.filter(Ingredient.quantity_available <= Ingredient.reorder_level)

    ingredients = query.order_by(Ingredient.name.asc()).all()
    suppliers = Supplier.query.filter_by(status='Active').all()

    total_items = Ingredient.query.count()
    low_stock_items = [i for i in ingredients if i.is_low_stock]
    low_stock_count = len(low_stock_items)

    recent_txns = InventoryTransaction.query.order_by(InventoryTransaction.created_at.desc()).limit(8).all()

    return render_template(
        'inventory/dashboard.html',
        ingredients=ingredients,
        suppliers=suppliers,
        total_items=total_items,
        low_stock_count=low_stock_count,
        low_stock_items=low_stock_items,
        recent_txns=recent_txns,
        search_query=search_query,
        low_stock_only=low_stock_only
    )


@inventory_bp.route('/ingredient/add', methods=['POST'])
@role_required(ROLE_STORE_KEEPER, ROLE_MANAGER, ROLE_ADMIN)
def add_ingredient():
    name = request.form.get('name', '').strip()
    quantity = request.form.get('quantity', '0')
    unit = request.form.get('unit', 'kg').strip()
    reorder_level = request.form.get('reorder_level', '10')
    supplier_id = request.form.get('supplier_id')
    cost = request.form.get('cost', '0')

    if not name:
        flash('Ingredient name is required.', 'danger')
        return redirect(url_for('inventory.dashboard'))

    if Ingredient.query.filter_by(name=name).first():
        flash(f"An ingredient named '{name}' already exists.", 'danger')
        return redirect(url_for('inventory.dashboard'))

    try:
        qty_dec = Decimal(str(quantity))
        reorder_dec = Decimal(str(reorder_level))
        cost_dec = Decimal(str(cost))
        sup_id = int(supplier_id) if supplier_id and supplier_id.isdigit() else None

        ing = Ingredient(
            name=name,
            quantity_available=qty_dec,
            unit=unit,
            reorder_level=reorder_dec,
            supplier_id=sup_id,
            cost=cost_dec
        )
        db.session.add(ing)
        db.session.flush()

        if qty_dec > Decimal('0.00'):
            txn = InventoryTransaction(
                ingredient_id=ing.ingredient_id,
                transaction_type='Stock In',
                quantity=qty_dec,
                previous_quantity=Decimal('0.00'),
                new_quantity=qty_dec,
                reason='Initial ingredient creation',
                user_id=current_user.user_id,
                created_at=datetime.utcnow()
            )
            db.session.add(txn)

        db.session.commit()
        flash(f"Ingredient '{name}' added successfully.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to add ingredient: {str(e)}", 'danger')

    return redirect(url_for('inventory.dashboard'))


@inventory_bp.route('/ingredient/<int:ingredient_id>/edit', methods=['POST'])
@role_required(ROLE_STORE_KEEPER, ROLE_MANAGER, ROLE_ADMIN)
def edit_ingredient(ingredient_id):
    ing = Ingredient.query.get_or_404(ingredient_id)
    name = request.form.get('name', '').strip()
    unit = request.form.get('unit', 'kg').strip()
    reorder_level = request.form.get('reorder_level', '10')
    supplier_id = request.form.get('supplier_id')
    cost = request.form.get('cost', '0')

    if not name:
        flash('Ingredient name is required.', 'danger')
        return redirect(url_for('inventory.dashboard'))

    try:
        ing.name = name
        ing.unit = unit
        ing.reorder_level = Decimal(str(reorder_level))
        ing.supplier_id = int(supplier_id) if supplier_id and supplier_id.isdigit() else None
        ing.cost = Decimal(str(cost))
        ing.last_updated = datetime.utcnow()
        db.session.commit()
        flash(f"Ingredient '{name}' updated successfully.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to update ingredient: {str(e)}", 'danger')

    return redirect(url_for('inventory.dashboard'))


@inventory_bp.route('/ingredient/<int:ingredient_id>/delete', methods=['POST'])
@role_required(ROLE_STORE_KEEPER, ROLE_MANAGER, ROLE_ADMIN)
def delete_ingredient(ingredient_id):
    ing = Ingredient.query.get_or_404(ingredient_id)
    name = ing.name
    try:
        db.session.delete(ing)
        db.session.commit()
        flash(f"Ingredient '{name}' deleted.", 'info')
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to delete ingredient: {str(e)}", 'danger')

    return redirect(url_for('inventory.dashboard'))


@inventory_bp.route('/stock-action', methods=['POST'])
@role_required(ROLE_STORE_KEEPER, ROLE_MANAGER, ROLE_ADMIN)
def stock_action():
    ingredient_id = int(request.form.get('ingredient_id'))
    action = request.form.get('action')  # 'in', 'out', 'adjust'
    quantity = request.form.get('quantity')
    reason = request.form.get('reason', '').strip()

    try:
        if action == 'in':
            InventoryService.record_stock_in(ingredient_id, quantity, user_id=current_user.user_id, reason=reason or 'Stock In')
            flash('Stock In recorded successfully.', 'success')
        elif action == 'out':
            InventoryService.record_stock_out(ingredient_id, quantity, user_id=current_user.user_id, reason=reason or 'Stock Out')
            flash('Stock Out recorded successfully.', 'success')
        elif action == 'adjust':
            InventoryService.adjust_stock(ingredient_id, quantity, user_id=current_user.user_id, reason=reason or 'Audit Adjustment')
            flash('Stock adjustment recorded successfully.', 'success')
    except ValueError as ve:
        flash(str(ve), 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f"Error processing transaction: {str(e)}", 'danger')

    return redirect(url_for('inventory.dashboard'))


@inventory_bp.route('/transactions')
@role_required(ROLE_STORE_KEEPER, ROLE_MANAGER, ROLE_ADMIN)
def transactions():
    ingredient_id = request.args.get('ingredient_id')
    txn_type = request.args.get('type')
    query = InventoryTransaction.query

    if ingredient_id and ingredient_id.isdigit():
        query = query.filter(InventoryTransaction.ingredient_id == int(ingredient_id))
    if txn_type:
        query = query.filter(InventoryTransaction.transaction_type == txn_type)

    transactions = query.order_by(InventoryTransaction.created_at.desc()).all()
    ingredients = Ingredient.query.order_by(Ingredient.name.asc()).all()

    return render_template(
        'inventory/stock_movement.html',
        transactions=transactions,
        ingredients=ingredients,
        selected_ingredient=int(ingredient_id) if ingredient_id and ingredient_id.isdigit() else None,
        selected_type=txn_type
    )


@inventory_bp.route('/suppliers', methods=['GET', 'POST'])
@role_required(ROLE_STORE_KEEPER, ROLE_MANAGER, ROLE_ADMIN)
def suppliers():
    if request.method == 'POST':
        action = request.form.get('action', 'add')

        if action == 'add':
            name = request.form.get('name', '').strip()
            phone = request.form.get('phone', '').strip()
            email = request.form.get('email', '').strip()
            address = request.form.get('address', '').strip()
            items_supplied = request.form.get('items_supplied', '').strip()

            if not name or not phone:
                flash('Supplier name and phone are required.', 'danger')
                return redirect(url_for('inventory.suppliers'))

            sup = Supplier(name=name, phone=phone, email=email or None, address=address or None, items_supplied=items_supplied or None)
            db.session.add(sup)
            db.session.commit()
            flash(f"Supplier '{name}' registered successfully.", 'success')

        elif action == 'edit':
            sup_id = int(request.form.get('supplier_id'))
            sup = Supplier.query.get_or_404(sup_id)
            sup.name = request.form.get('name', '').strip()
            sup.phone = request.form.get('phone', '').strip()
            sup.email = request.form.get('email', '').strip() or None
            sup.address = request.form.get('address', '').strip() or None
            sup.items_supplied = request.form.get('items_supplied', '').strip() or None
            sup.status = request.form.get('status', 'Active')
            db.session.commit()
            flash(f"Supplier '{sup.name}' updated.", 'success')

        elif action == 'delete':
            sup_id = int(request.form.get('supplier_id'))
            sup = Supplier.query.get_or_404(sup_id)
            name = sup.name
            db.session.delete(sup)
            db.session.commit()
            flash(f"Supplier '{name}' deleted.", 'info')

        return redirect(url_for('inventory.suppliers'))

    search = request.args.get('search', '').strip()
    query = Supplier.query
    if search:
        query = query.filter(Supplier.name.ilike(f"%{search}%") | Supplier.items_supplied.ilike(f"%{search}%"))

    suppliers_list = query.order_by(Supplier.name.asc()).all()
    return render_template('inventory/suppliers.html', suppliers=suppliers_list, search=search)


@inventory_bp.route('/alerts')
@role_required(ROLE_STORE_KEEPER, ROLE_MANAGER, ROLE_ADMIN)
def alerts():
    low_stock_items = InventoryService.get_low_stock_items()
    return render_template('inventory/alerts.html', low_stock_items=low_stock_items)
