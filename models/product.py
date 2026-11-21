
from datetime import datetime
from decimal import Decimal
from extensions import db


class Category(db.Model):
    __tablename__ = 'categories'

    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    products = db.relationship(
        'Product',
        back_populates='category',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    __tablename__ = 'products'

    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(
        db.Integer,
        db.ForeignKey('categories.category_id', ondelete='RESTRICT'),
        nullable=False
    )
    name = db.Column(db.String(120), nullable=False, index=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)
    availability = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    category = db.relationship('Category', back_populates='products')
    order_items = db.relationship(
        'OrderItem',
        back_populates='product',
        lazy='dynamic'
    )

    @property
    def price_float(self):
        return float(self.price or 0.0)

    def __repr__(self):
        return f'<Product {self.name} - ${self.price}>'
