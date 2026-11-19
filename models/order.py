from datetime import datetime
from decimal import Decimal
from extensions import db


class Order(db.Model):
    __tablename__ = 'orders'

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_number = db.Column(db.String(40), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id', ondelete='SET NULL'), nullable=True)
    order_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    order_type = db.Column(db.String(30), nullable=False, default='Online Order')  # 'Online Order', 'Walk-in Order', 'Custom Cake Order'
    status = db.Column(db.String(30), nullable=False, default='Pending', index=True)  # 'Pending', 'Confirmed', 'Preparing', 'Ready', 'Delivered', 'Cancelled'
    
    subtotal = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    discount = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    tax = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    
    payment_mode = db.Column(db.String(30), nullable=False, default='Cash')  # 'Cash', 'Card', 'UPI'
    payment_status = db.Column(db.String(30), nullable=False, default='Pending')  # 'Paid', 'Pending', 'Partially Paid'
    special_instructions = db.Column(db.Text, nullable=True)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)

    # Relationships
    customer = db.relationship('Customer', back_populates='orders')
    items = db.relationship('OrderItem', back_populates='order', cascade='all, delete-orphan', lazy='joined')
    bill = db.relationship('Bill', back_populates='order', uselist=False, cascade='all, delete-orphan')
    custom_cake_order = db.relationship('CustomCakeOrder', back_populates='order', uselist=False)
    creator = db.relationship('User', back_populates='orders_created', foreign_keys=[created_by_user_id])

    @property
    def total_float(self):
        return float(self.total_amount or 0.0)

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items)

    def __repr__(self):
        return f"<Order {self.order_number} ({self.status}) - ${self.total_amount}>"


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id', ondelete='SET NULL'), nullable=True)
    item_name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    subtotal = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.00'))

    # Relationships
    order = db.relationship('Order', back_populates='items')
    product = db.relationship('Product', back_populates='order_items')

    def __repr__(self):
        return f"<OrderItem {self.item_name} x {self.quantity} (${self.subtotal})>"


class Bill(db.Model):
    __tablename__ = 'bills'

    bill_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id', ondelete='CASCADE'), nullable=False, unique=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    discount = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    tax = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    total = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    payment_mode = db.Column(db.String(30), nullable=False, default='Cash')
    payment_status = db.Column(db.String(30), nullable=False, default='Paid')
    bill_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    order = db.relationship('Order', back_populates='bill')

    def __repr__(self):
        return f"<Bill {self.invoice_number} for Order#{self.order_id} - ${self.total}>"
