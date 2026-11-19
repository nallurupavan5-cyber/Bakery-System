from datetime import datetime
from decimal import Decimal
from extensions import db


class Ingredient(db.Model):
    __tablename__ = 'ingredients'

    ingredient_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False, unique=True, index=True)
    quantity_available = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    unit = db.Column(db.String(30), nullable=False, default='kg')
    reorder_level = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('10.00'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.supplier_id', ondelete='SET NULL'), nullable=True)
    cost = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    supplier = db.relationship('Supplier', back_populates='ingredients')
    transactions = db.relationship('InventoryTransaction', back_populates='ingredient', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def is_low_stock(self):
        curr = self.quantity_available or Decimal('0.00')
        reorder = self.reorder_level or Decimal('0.00')
        return curr <= reorder

    @property
    def quantity_float(self):
        return float(self.quantity_available or 0.0)

    @property
    def reorder_float(self):
        return float(self.reorder_level or 0.0)

    def __repr__(self):
        return f"<Ingredient {self.name}: {self.quantity_available} {self.unit}>"


class InventoryTransaction(db.Model):
    __tablename__ = 'inventory_transactions'

    transaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.ingredient_id', ondelete='CASCADE'), nullable=False)
    transaction_type = db.Column(db.String(30), nullable=False)  # 'Stock In', 'Stock Out', 'Adjustment'
    quantity = db.Column(db.Numeric(10, 2), nullable=False)
    previous_quantity = db.Column(db.Numeric(10, 2), nullable=False)
    new_quantity = db.Column(db.Numeric(10, 2), nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    ingredient = db.relationship('Ingredient', back_populates='transactions')
    user = db.relationship('User', back_populates='inventory_actions')

    def __repr__(self):
        return f"<InventoryTransaction {self.transaction_type} {self.quantity} for Ing#{self.ingredient_id}>"
