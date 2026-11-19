from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, Response, redirect, url_for, flash
from extensions import db
from models.order import Order
from models.inventory import Ingredient
from models.product import Product
from models.user import Customer, Staff
from services.report_service import ReportService
from utils.decorators import role_required, ROLE_MANAGER, ROLE_ADMIN

manager_bp = Blueprint('manager', __name__, url_prefix='/manager')


@manager_bp.route('/')
@manager_bp.route('/dashboard')
@role_required(ROLE_MANAGER, ROLE_ADMIN)
def dashboard():
    summary = ReportService.get_dashboard_summary()
    charts_data = ReportService.get_sales_charts_data()
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(8).all()
    low_stock_items = Ingredient.query.filter(Ingredient.quantity_available <= Ingredient.reorder_level).all()

    return render_template(
        'manager/dashboard.html',
        summary=summary,
        charts_data=charts_data,
        recent_orders=recent_orders,
        low_stock_items=low_stock_items
    )


@manager_bp.route('/reports')
@role_required(ROLE_MANAGER, ROLE_ADMIN)
def reports():
    report_type = request.args.get('report_type', 'sales')
    date_filter = request.args.get('date_filter', 'this_month')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    now = datetime.utcnow()
    start_date = None
    end_date = None

    if date_filter == 'today':
        start_date = datetime(now.year, now.month, now.day)
        end_date = start_date + timedelta(days=1)
    elif date_filter == 'yesterday':
        end_date = datetime(now.year, now.month, now.day)
        start_date = end_date - timedelta(days=1)
    elif date_filter == 'this_week':
        start_date = datetime(now.year, now.month, now.day) - timedelta(days=6)
        end_date = now
    elif date_filter == 'this_month':
        start_date = datetime(now.year, now.month, 1)
        end_date = now
    elif date_filter == 'custom' and start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)
        except ValueError:
            start_date = None
            end_date = None

    # Fetch data based on report_type
    orders_data = []
    products_data = []
    inventory_data = []

    if report_type in ('sales', 'orders', 'daily_sales', 'monthly_sales', 'payment'):
        query = Order.query
        if start_date:
            query = query.filter(Order.order_date >= start_date)
        if end_date:
            query = query.filter(Order.order_date <= end_date)
        orders_data = query.order_by(Order.order_date.desc()).all()

    elif report_type == 'products':
        products_data = Product.query.order_by(Product.name.asc()).all()

    elif report_type in ('inventory', 'low_stock'):
        query = Ingredient.query
        if report_type == 'low_stock':
            query = query.filter(Ingredient.quantity_available <= Ingredient.reorder_level)
        inventory_data = query.order_by(Ingredient.name.asc()).all()

    return render_template(
        'manager/reports.html',
        report_type=report_type,
        date_filter=date_filter,
        start_date=start_date_str or '',
        end_date=end_date_str or '',
        orders=orders_data,
        products=products_data,
        inventory=inventory_data
    )


@manager_bp.route('/reports/export/csv')
@role_required(ROLE_MANAGER, ROLE_ADMIN)
def export_csv():
    report_type = request.args.get('report_type', 'sales')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    start_date = None
    end_date = None
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except ValueError:
            pass
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)
        except ValueError:
            pass

    csv_content = ReportService.generate_csv_report(report_type, start_date, end_date)
    filename = f"bakery_report_{report_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.csv"

    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )
