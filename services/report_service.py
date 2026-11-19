from datetime import datetime, timedelta, date
from decimal import Decimal
import io
import csv
from sqlalchemy import func, desc
from extensions import db
from models.order import Order, OrderItem
from models.product import Product, Category
from models.user import Customer, User
from models.inventory import Ingredient
from models.custom_cake import CustomCakeOrder


class ReportService:
    @staticmethod
    def get_dashboard_summary():
        now = datetime.utcnow()
        today_start = datetime(now.year, now.month, now.day)
        week_start = today_start - timedelta(days=6)
        month_start = datetime(now.year, now.month, 1)

        # Sales calculations (exclude Cancelled)
        sales_query = db.session.query(func.coalesce(func.sum(Order.total_amount), 0)).filter(
            Order.status != 'Cancelled',
            Order.payment_status == 'Paid'
        )

        today_sales = float(sales_query.filter(Order.order_date >= today_start).scalar() or 0.0)
        weekly_sales = float(sales_query.filter(Order.order_date >= week_start).scalar() or 0.0)
        monthly_sales = float(sales_query.filter(Order.order_date >= month_start).scalar() or 0.0)

        # Order counts
        today_orders = Order.query.filter(Order.order_date >= today_start).count()
        pending_orders = Order.query.filter(Order.status.in_(['Pending', 'Confirmed', 'Preparing'])).count()
        completed_orders = Order.query.filter(Order.status == 'Delivered').count()

        # Inventory & Catalog
        low_stock_count = Ingredient.query.filter(Ingredient.quantity_available <= Ingredient.reorder_level).count()
        total_products = Product.query.count()
        total_customers = Customer.query.count()

        return {
            'today_sales': today_sales,
            'weekly_sales': weekly_sales,
            'monthly_sales': monthly_sales,
            'today_orders': today_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'low_stock_count': low_stock_count,
            'total_products': total_products,
            'total_customers': total_customers
        }

    @staticmethod
    def get_sales_charts_data():
        now = datetime.utcnow()

        # 1. Daily Sales Chart (Last 7 Days)
        daily_labels = []
        daily_data = []
        for i in range(6, -1, -1):
            day_dt = now - timedelta(days=i)
            day_start = datetime(day_dt.year, day_dt.month, day_dt.day)
            day_end = day_start + timedelta(days=1)
            sales = db.session.query(func.coalesce(func.sum(Order.total_amount), 0)).filter(
                Order.order_date >= day_start,
                Order.order_date < day_end,
                Order.status != 'Cancelled'
            ).scalar() or 0.0
            daily_labels.append(day_start.strftime('%a, %b %d'))
            daily_data.append(float(sales))

        # 2. Weekly Sales Chart (Last 4 Weeks)
        weekly_labels = []
        weekly_data = []
        for w in range(3, -1, -1):
            w_start = now - timedelta(days=(w + 1) * 7)
            w_end = now - timedelta(days=w * 7)
            sales = db.session.query(func.coalesce(func.sum(Order.total_amount), 0)).filter(
                Order.order_date >= w_start,
                Order.order_date < w_end,
                Order.status != 'Cancelled'
            ).scalar() or 0.0
            weekly_labels.append(f"Week {4 - w} ({w_start.strftime('%b %d')})")
            weekly_data.append(float(sales))

        # 3. Monthly Sales Chart (Last 6 Months)
        monthly_labels = []
        monthly_data = []
        for m in range(5, -1, -1):
            # Calculate target year and month
            target_month = (now.month - m - 1) % 12 + 1
            target_year = now.year + ((now.month - m - 1) // 12)
            m_start = datetime(target_year, target_month, 1)
            if target_month == 12:
                m_end = datetime(target_year + 1, 1, 1)
            else:
                m_end = datetime(target_year, target_month + 1, 1)

            sales = db.session.query(func.coalesce(func.sum(Order.total_amount), 0)).filter(
                Order.order_date >= m_start,
                Order.order_date < m_end,
                Order.status != 'Cancelled'
            ).scalar() or 0.0
            monthly_labels.append(m_start.strftime('%b %Y'))
            monthly_data.append(float(sales))

        # 4. Orders by Status
        status_results = db.session.query(
            Order.status,
            func.count(Order.order_id)
        ).group_by(Order.status).all()
        status_dict = dict(status_results)
        status_keys = ['Pending', 'Confirmed', 'Preparing', 'Ready', 'Delivered', 'Cancelled']
        status_data = [status_dict.get(st, 0) for st in status_keys]

        # 5. Top Selling Products
        top_prods = db.session.query(
            OrderItem.item_name,
            func.sum(OrderItem.quantity).label('total_qty')
        ).join(Order, Order.order_id == OrderItem.order_id)\
         .filter(Order.status != 'Cancelled')\
         .group_by(OrderItem.item_name)\
         .order_by(desc('total_qty'))\
         .limit(6).all()
        top_prod_labels = [p[0] for p in top_prods]
        top_prod_data = [int(p[1]) for p in top_prods]

        # 6. Sales by Category
        cat_sales = db.session.query(
            Category.name,
            func.coalesce(func.sum(OrderItem.subtotal), 0).label('cat_total')
        ).select_from(Category)\
         .outerjoin(Product, Product.category_id == Category.category_id)\
         .outerjoin(OrderItem, OrderItem.product_id == Product.product_id)\
         .group_by(Category.name).all()
        cat_labels = [c[0] for c in cat_sales]
        cat_data = [float(c[1]) for c in cat_sales]

        # 7. Low Stock / Inventory Chart
        ingredients = Ingredient.query.order_by(Ingredient.quantity_available.asc()).limit(8).all()
        ing_labels = [ing.name for ing in ingredients]
        ing_stock = [ing.quantity_float for ing in ingredients]
        ing_reorder = [ing.reorder_float for ing in ingredients]

        return {
            'daily': {'labels': daily_labels, 'data': daily_data},
            'weekly': {'labels': weekly_labels, 'data': weekly_data},
            'monthly': {'labels': monthly_labels, 'data': monthly_data},
            'status': {'labels': status_keys, 'data': status_data},
            'top_products': {'labels': top_prod_labels, 'data': top_prod_data},
            'categories': {'labels': cat_labels, 'data': cat_data},
            'inventory': {'labels': ing_labels, 'stock': ing_stock, 'reorder': ing_reorder}
        }

    @staticmethod
    def generate_csv_report(report_type, start_date=None, end_date=None):
        output = io.StringIO()
        writer = csv.writer(output)

        if report_type == 'sales' or report_type == 'daily_sales' or report_type == 'monthly_sales':
            writer.writerow(['Order ID', 'Order Number', 'Date', 'Type', 'Customer', 'Status', 'Subtotal ($)', 'Discount ($)', 'Tax ($)', 'Total ($)', 'Payment Mode', 'Payment Status'])
            query = Order.query
            if start_date:
                query = query.filter(Order.order_date >= start_date)
            if end_date:
                query = query.filter(Order.order_date <= end_date)
            orders = query.order_by(Order.order_date.desc()).all()
            for o in orders:
                cname = o.customer.name if o.customer else 'Walk-in'
                writer.writerow([
                    o.order_id, o.order_number, o.order_date.strftime('%Y-%m-%d %H:%M'),
                    o.order_type, cname, o.status,
                    f"{o.subtotal:.2f}", f"{o.discount:.2f}", f"{o.tax:.2f}", f"{o.total_amount:.2f}",
                    o.payment_mode, o.payment_status
                ])

        elif report_type == 'products':
            writer.writerow(['Product ID', 'Name', 'Category', 'Price ($)', 'Available', 'Total Sold (Qty)', 'Total Revenue ($)'])
            products = Product.query.all()
            for p in products:
                total_qty = db.session.query(func.coalesce(func.sum(OrderItem.quantity), 0)).filter(OrderItem.product_id == p.product_id).scalar() or 0
                total_rev = db.session.query(func.coalesce(func.sum(OrderItem.subtotal), 0)).filter(OrderItem.product_id == p.product_id).scalar() or 0.0
                writer.writerow([
                    p.product_id, p.name, p.category.name if p.category else 'N/A',
                    f"{p.price:.2f}", 'Yes' if p.availability else 'No',
                    int(total_qty), f"{float(total_rev):.2f}"
                ])

        elif report_type == 'inventory' or report_type == 'low_stock':
            writer.writerow(['Ingredient ID', 'Name', 'Quantity Available', 'Unit', 'Reorder Level', 'Supplier', 'Cost Per Unit ($)', 'Status', 'Last Updated'])
            query = Ingredient.query
            if report_type == 'low_stock':
                query = query.filter(Ingredient.quantity_available <= Ingredient.reorder_level)
            ingredients = query.all()
            for ing in ingredients:
                status_str = 'LOW STOCK' if ing.is_low_stock else 'Normal'
                sname = ing.supplier.name if ing.supplier else 'None'
                writer.writerow([
                    ing.ingredient_id, ing.name, f"{ing.quantity_available:.2f}", ing.unit,
                    f"{ing.reorder_level:.2f}", sname, f"{ing.cost:.2f}",
                    status_str, ing.last_updated.strftime('%Y-%m-%d %H:%M') if ing.last_updated else ''
                ])

        elif report_type == 'orders':
            writer.writerow(['Order Number', 'Date', 'Type', 'Customer Phone', 'Status', 'Items Summary', 'Total Amount ($)'])
            orders = Order.query.order_by(Order.order_date.desc()).all()
            for o in orders:
                items_summary = "; ".join([f"{it.item_name} x{it.quantity}" for it in o.items])
                phone = o.customer.phone if o.customer else 'N/A'
                writer.writerow([
                    o.order_number, o.order_date.strftime('%Y-%m-%d %H:%M'),
                    o.order_type, phone, o.status, items_summary, f"{o.total_amount:.2f}"
                ])

        return output.getvalue()
