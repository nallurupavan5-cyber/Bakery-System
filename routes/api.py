from decimal import Decimal
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.product import Product
from models.inventory import Ingredient
from services.billing_service import BillingService
from services.report_service import ReportService
from services.inventory_service import InventoryService

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/products/search')
def search_products():
    q = request.args.get('q', '').strip()
    category_id = request.args.get('category_id')

    query = Product.query.filter_by(availability=True)
    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))
    if category_id and category_id.isdigit():
        query = query.filter_by(category_id=int(category_id))

    products = query.order_by(Product.name.asc()).limit(30).all()

    return jsonify({
        'products': [
            {
                'id': p.product_id,
                'name': p.name,
                'category': p.category.name if p.category else '',
                'price': float(p.price),
                'image': p.image or '',
                'available': p.availability
            }
            for p in products
        ]
    })


@api_bp.route('/billing/calculate', methods=['POST'])
def calculate_billing():
    data = request.get_json(silent=True) or {}
    items = data.get('items', [])
    discount_amount = float(data.get('discount_amount', 0.0))
    discount_percent = float(data.get('discount_percent', 0.0))
    tax_percent = float(data.get('tax_percent', 5.0))

    try:
        totals = BillingService.calculate_totals(
            items,
            discount_percent=discount_percent,
            discount_amount=discount_amount,
            tax_percent=tax_percent
        )
        return jsonify({
            'success': True,
            'subtotal': float(totals['subtotal']),
            'discount': float(totals['discount']),
            'tax': float(totals['tax']),
            'total': float(totals['total_amount'])
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@api_bp.route('/charts/data')
@login_required
def charts_data():
    if current_user.role not in ('Administrator', 'Manager'):
        return jsonify({'error': 'Unauthorized'}), 403

    data = ReportService.get_sales_charts_data()
    return jsonify(data)


@api_bp.route('/inventory/low-stock-count')
@login_required
def low_stock_count():
    count = Ingredient.query.filter(Ingredient.quantity_available <= Ingredient.reorder_level).count()
    return jsonify({'count': count})
