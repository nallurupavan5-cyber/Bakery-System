from datetime import datetime
from decimal import Decimal
import random
from extensions import db
from models.order import Order, OrderItem
from models.custom_cake import CustomCakeOrder
from models.product import Product
from services.billing_service import BillingService


class OrderService:
    @staticmethod
    def generate_order_number():
        today_str = datetime.utcnow().strftime('%Y%m%d')
        rand_suffix = random.randint(100, 999)
        return f"ORD-{today_str}-{rand_suffix}"

    @classmethod
    def create_order(cls, customer_id, items_data, order_type='Online Order',
                     payment_mode='Cash', payment_status='Pending',
                     discount_percent=0.0, discount_amount=0.0, tax_percent=None,
                     special_instructions=None, created_by_user_id=None):
        """
        items_data: list of dicts: [{'product_id': 1, 'quantity': 2, 'price': Decimal('28.50')}, ...]
        """
        if not items_data:
            raise ValueError("An order must contain at least one item.")

        # Validate and prepare items
        prepared_items = []
        for item in items_data:
            prod_id = item.get('product_id')
            qty = int(item.get('quantity', 1))
            if qty <= 0:
                raise ValueError("Item quantity must be at least 1.")

            if prod_id:
                product = Product.query.get(prod_id)
                if not product:
                    raise ValueError(f"Product ID {prod_id} does not exist.")
                if not product.availability:
                    raise ValueError(f"Product '{product.name}' is currently unavailable.")
                price = product.price
                name = product.name
            else:
                price = Decimal(str(item.get('price', '0.00')))
                name = item.get('name', 'Custom Item')

            prepared_items.append({
                'product_id': prod_id,
                'name': name,
                'quantity': qty,
                'price': price,
                'subtotal': price * qty
            })

        # Calculate totals
        totals = BillingService.calculate_totals(
            prepared_items,
            discount_percent=discount_percent,
            discount_amount=discount_amount,
            tax_percent=tax_percent
        )

        order_num = cls.generate_order_number()
        while Order.query.filter_by(order_number=order_num).first():
            order_num = cls.generate_order_number()

        # Initial status
        initial_status = 'Pending'
        if order_type == 'Walk-in Order' and payment_status == 'Paid':
            initial_status = 'Confirmed'

        order = Order(
            order_number=order_num,
            customer_id=customer_id,
            order_date=datetime.utcnow(),
            order_type=order_type,
            status=initial_status,
            subtotal=totals['subtotal'],
            discount=totals['discount'],
            tax=totals['tax'],
            total_amount=totals['total_amount'],
            payment_mode=payment_mode,
            payment_status=payment_status,
            special_instructions=special_instructions,
            created_by_user_id=created_by_user_id
        )
        db.session.add(order)
        db.session.flush()

        # Add Order Items
        for item in prepared_items:
            order_item = OrderItem(
                order_id=order.order_id,
                product_id=item['product_id'],
                item_name=item['name'],
                quantity=item['quantity'],
                price=item['price'],
                subtotal=item['subtotal']
            )
            db.session.add(order_item)

        # Generate Bill/Invoice if Paid or Walk-in
        BillingService.create_bill_for_order(order)

        db.session.commit()
        return order

    @staticmethod
    def update_order_status(order_id, new_status):
        valid_statuses = ['Pending', 'Confirmed', 'Preparing', 'Ready', 'Delivered', 'Cancelled']
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status '{new_status}'. Allowed: {', '.join(valid_statuses)}")

        order = Order.query.get_or_404(order_id)
        order.status = new_status

        # If delivered or paid, sync payment status if needed
        if new_status == 'Delivered' and order.payment_status != 'Paid':
            order.payment_status = 'Paid'

        # Ensure bill reflects current order
        BillingService.create_bill_for_order(order)
        db.session.commit()
        return order

    @staticmethod
    def create_custom_cake_order(customer_id, cake_type, flavour, size, quantity,
                                 required_date, required_time=None, design_notes=None,
                                 special_instructions=None, image_path=None, estimated_price=0.0):
        if quantity <= 0:
            raise ValueError("Quantity must be at least 1.")

        cake_order = CustomCakeOrder(
            customer_id=customer_id,
            cake_type=cake_type,
            flavour=flavour,
            size=size,
            quantity=quantity,
            required_date=required_date,
            required_time=required_time,
            design_notes=design_notes,
            special_instructions=special_instructions,
            image_path=image_path,
            estimated_price=Decimal(str(estimated_price or 0.0)),
            status='Pending',
            created_at=datetime.utcnow()
        )
        db.session.add(cake_order)
        db.session.commit()
        return cake_order

    @staticmethod
    def update_custom_cake_status(custom_order_id, new_status):
        valid_statuses = ['Pending', 'Confirmed', 'Preparing', 'Ready', 'Delivered', 'Cancelled']
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status '{new_status}'. Allowed: {', '.join(valid_statuses)}")

        custom_order = CustomCakeOrder.query.get_or_404(custom_order_id)
        custom_order.status = new_status
        db.session.commit()
        return custom_order
