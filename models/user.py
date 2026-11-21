
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default='Customer')
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    customer_profile = db.relationship(
        'Customer', back_populates='user',
        uselist=False, cascade='all, delete-orphan'
    )
    staff_profile = db.relationship(
        'Staff', back_populates='user',
        uselist=False, cascade='all, delete-orphan'
    )
    inventory_actions = db.relationship(
        'InventoryTransaction', back_populates='user', lazy='dynamic'
    )
    orders_created = db.relationship(
        'Order', back_populates='creator',
        foreign_keys='Order.created_by_user_id', lazy='dynamic'
    )

    def get_id(self):
        return str(self.user_id)

    @property
    def is_active(self):
        return self.active

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, *roles):
        return self.role in roles

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Customer(db.Model):
    __tablename__ = 'customers'

    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'),
        nullable=True
    )
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', back_populates='customer_profile')
    orders = db.relationship(
        'Order', back_populates='customer',
        lazy='dynamic', cascade='all, delete-orphan'
    )
    custom_cake_orders = db.relationship(
        'CustomCakeOrder', back_populates='customer',
        lazy='dynamic', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Customer {self.name} - {self.phone}>'


class Staff(db.Model):
    __tablename__ = 'staff'

    staff_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False
    )
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', back_populates='staff_profile')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

        if self.user:
            self.user.set_password(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Staff {self.name} ({self.role})>'
