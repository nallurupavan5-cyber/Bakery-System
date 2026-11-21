from datetime import datetime
from extensions import db


class Supplier(db.Model):
    __tablename__ = 'suppliers'

    supplier_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.Text, nullable=True)
    items_supplied = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Active', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    ingredients = db.relationship(
        'Ingredient', back_populates='supplier', lazy='dynamic'
    )

    def __repr__(self):
        return f'<Supplier {self.name}>'
