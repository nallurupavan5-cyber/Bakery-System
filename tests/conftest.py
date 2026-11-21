import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from decimal import Decimal
from datetime import datetime
from config import TestConfig
from app import create_app
from extensions import db
from models.user import User, Customer, Staff
from models.product import Category, Product
from models.supplier import Supplier
from models.inventory import Ingredient, InventoryTransaction
from models.order import Order, OrderItem, Bill
from models.settings import SystemSetting


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()

        # System settings
        SystemSetting.set_value('default_tax_percent', '5.0')
        SystemSetting.set_value('currency_symbol', '$')

        # Roles demo accounts
        roles = [
            ('admin', 'admin123', 'Administrator'),
            ('manager', 'manager123', 'Manager'),
            ('cashier', 'cashier123', 'Cashier'),
            ('baker', 'baker123', 'Baker'),
            ('store', 'store123', 'Store Keeper'),
            ('customer', 'customer123', 'Customer')
        ]

        for uname, pwd, role in roles:
            u = User(username=uname, role=role, active=True)
            u.set_password(pwd)
            db.session.add(u)
            db.session.flush()

            if role == 'Customer':
                c = Customer(user_id=u.user_id, name='Test Customer', phone='+1 555-0100', email='test@cust.com')
                db.session.add(c)
            else:
                s = Staff(user_id=u.user_id, name=f'Staff {role}', role=role, phone='+1 555-0101', username=uname, password_hash=u.password_hash)
                db.session.add(s)

        # Sample category & product
        cat = Category(name='Cakes', description='Delicious cakes')
        db.session.add(cat)
        db.session.flush()

        prod = Product(
            category_id=cat.category_id,
            name='Chocolate Truffle Cake',
            price=Decimal('28.50'),
            description='Dark chocolate truffle',
            availability=True
        )
        db.session.add(prod)

        # Sample ingredient
        ing = Ingredient(
            name='Flour',
            quantity_available=Decimal('50.00'),
            unit='kg',
            reorder_level=Decimal('20.00'),
            cost=Decimal('1.20')
        )
        db.session.add(ing)

        # Low stock ingredient
        low_ing = Ingredient(
            name='Butter',
            quantity_available=Decimal('5.00'),
            unit='kg',
            reorder_level=Decimal('10.00'),
            cost=Decimal('7.00')
        )
        db.session.add(low_ing)

        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username='customer', password='customer123'):
        return self._client.post('/auth/login', data={'username': username, 'password': password}, follow_redirects=True)

    def logout(self):
        return self._client.get('/auth/logout', follow_redirects=True)


@pytest.fixture
def auth(client):
    return AuthActions(client)
