from datetime import datetime
from decimal import Decimal
from extensions import db


class CustomCakeOrder(db.Model):
    __tablename__ = 'custom_cake_orders'

    custom_order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id', ondelete='CASCADE'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id', ondelete='SET NULL'), nullable=True)

    cake_type = db.Column(db.String(80), nullable=False)
    flavour = db.Column(db.String(80), nullable=False)
    size = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    required_date = db.Column(db.Date, nullable=False)
    required_time = db.Column(db.String(30), nullable=True)

    design_notes = db.Column(db.Text, nullable=True)
    special_instructions = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(255), nullable=True)

    estimated_price = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    status = db.Column(db.String(30), nullable=False, default='Pending', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    customer = db.relationship('Customer', back_populates='custom_cake_orders')
    order = db.relationship('Order', back_populates='custom_cake_order')

    def __repr__(self):
        return f'<CustomCakeOrder #{self.custom_order_id} ({self.cake_type} - {self.flavour})>'
