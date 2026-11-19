import sys
import os
from decimal import Decimal
from datetime import datetime, timedelta

# Ensure parent directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from models.user import User, Customer, Staff
from models.product import Category, Product
from models.supplier import Supplier
from models.inventory import Ingredient, InventoryTransaction
from models.order import Order, OrderItem, Bill
from models.custom_cake import CustomCakeOrder
from models.settings import SystemSetting


def seed_database(app=None):
    if app is None:
        app = create_app()

    with app.app_context():
        # Create all tables first
        db.create_all()

        # Check if users already exist
        if User.query.filter_by(username='admin').first():
            print("Database already contains seed data. Skipping seeding.")
            return

        print("Seeding database with realistic bakery data...")

        # 1. System Settings
        settings_data = [
            ('bakery_name', 'Sweet Delights Artisan Bakery', 'Official bakery name'),
            ('bakery_tagline', 'Freshly Baked, Made With Love', 'Bakery motto'),
            ('bakery_phone', '+1 (555) 234-5678', 'Customer support phone'),
            ('bakery_email', 'contact@sweetdelightsbakery.com', 'Official email'),
            ('bakery_address', '124 Sugarloaf Lane, Flour District, Suite 100', 'Bakery physical address'),
            ('currency_symbol', '$', 'Currency symbol for display'),
            ('default_tax_percent', '5.0', 'Sales tax percentage'),
            ('default_discount_percent', '0.0', 'Default discount percentage'),
        ]
        for key, val, desc in settings_data:
            SystemSetting.set_value(key, val, desc)

        # 2. Users & Staff / Customer Profiles
        users_info = [
            ('admin', 'admin123', 'Administrator', 'Arthur Pendelton', '+1 555-0101'),
            ('manager', 'manager123', 'Manager', 'Margaret Vance', '+1 555-0102'),
            ('cashier', 'cashier123', 'Cashier', 'Claire Davis', '+1 555-0103'),
            ('baker', 'baker123', 'Baker', 'Benjamin Baker', '+1 555-0104'),
            ('store', 'store123', 'Store Keeper', 'Samuel Torres', '+1 555-0105'),
        ]

        staff_users = {}
        for username, password, role, full_name, phone in users_info:
            user = User(username=username, role=role, active=True)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            staff = Staff(
                user_id=user.user_id,
                name=full_name,
                role=role,
                phone=phone,
                username=username,
                password_hash=user.password_hash
            )
            db.session.add(staff)
            staff_users[username] = user

        # Customer User
        cust_user = User(username='customer', role='Customer', active=True)
        cust_user.set_password('customer123')
        db.session.add(cust_user)
        db.session.flush()

        customer_profile = Customer(
            user_id=cust_user.user_id,
            name='Emily Watson',
            phone='+1 555-0199',
            email='emily.watson@example.com',
            address='742 Evergreen Terrace, Springfield'
        )
        db.session.add(customer_profile)

        # Additional Sample Walk-in Customers
        walkin_cust = Customer(
            user_id=None,
            name='Walk-in Customer',
            phone='+1 000-0000',
            email='walkin@bakery.local',
            address='In-Store Counter'
        )
        db.session.add(walkin_cust)

        cust2 = Customer(
            user_id=None,
            name='David Miller',
            phone='+1 555-0214',
            email='david.miller@example.com',
            address='12 Maple Street, Apt 4B'
        )
        db.session.add(cust2)
        db.session.flush()

        # 3. Categories
        categories_data = [
            ('Cakes', 'Exquisite handcrafted celebration cakes, layer cakes, and signature cheesecakes.', 'category_cakes.jpg'),
            ('Breads', 'Artisan sourdough, crusty baguettes, and fresh aromatic oven-baked loaves.', 'category_breads.jpg'),
            ('Pastries', 'Flaky golden French croissants, Danishes, tarts, and creamy sweet pastries.', 'category_pastries.jpg'),
            ('Cookies', 'Crunchy, chewy, butter-rich gourmet cookies baked fresh throughout the day.', 'category_cookies.jpg'),
        ]

        cat_map = {}
        for cname, cdesc, cimg in categories_data:
            cat = Category(name=cname, description=cdesc, image=cimg, is_active=True)
            db.session.add(cat)
            db.session.flush()
            cat_map[cname] = cat

        # 4. Products
        products_data = [
            # Cakes
            ('Chocolate Truffle Cake', 'Cakes', Decimal('28.50'),
             'Decadent dark Belgian chocolate sponge layered with rich silky ganache and chocolate curls.', 'cake_chocolate_truffle.jpg', True),
            ('Black Forest Cake', 'Cakes', Decimal('26.00'),
             'Classic German torte with whipped cream, sour cherries, dark chocolate shavings, and kirsch aroma.', 'cake_black_forest.jpg', True),
            ('Red Velvet Cake', 'Cakes', Decimal('29.00'),
             'Velvety crimson sponge paired with tangy cream cheese frosting and a delicate crumb coating.', 'cake_red_velvet.jpg', True),
            ('Vanilla Cake', 'Cakes', Decimal('24.00'),
             'Soft Madagascar vanilla bean sponge covered in smooth, whipped vanilla buttercream.', 'cake_vanilla.jpg', True),
            # Breads
            ('Butter Croissant', 'Pastries', Decimal('3.75'),
             'Traditional French laminated pastry with 81 golden flaky layers and rich European butter.', 'pastry_croissant.jpg', True),
            ('Garlic Bread', 'Breads', Decimal('5.50'),
             'Crusty artisan loaf baked with roasted garlic herb butter, parsley, and melted parmesan.', 'bread_garlic.jpg', True),
            # Pastries
            ('Chocolate Pastry', 'Pastries', Decimal('4.25'),
             'Individual layered chocolate mousse slice topped with dark chocolate glaze and hazelnut dust.', 'pastry_chocolate.jpg', True),
            ('Fruit Pastry', 'Pastries', Decimal('4.75'),
             'Crispy puff pastry tart filled with vanilla diplomat cream and topped with glazed fresh berries.', 'pastry_fruit.jpg', True),
            # Cookies
            ('Chocolate Chip Cookies', 'Cookies', Decimal('2.50'),
             'Chewy bakery classic loaded with semi-sweet Belgian chocolate chunks and sea salt flakes.', 'cookie_chocochip.jpg', True),
            ('Oat Cookies', 'Cookies', Decimal('2.25'),
             'Hearty rolled oats with cinnamon, brown sugar, golden honey, and plump sun-dried raisins.', 'cookie_oat.jpg', True),
        ]

        prod_map = {}
        for pname, cname, price, desc, img, avail in products_data:
            p = Product(
                category_id=cat_map[cname].category_id,
                name=pname,
                price=price,
                description=desc,
                image=img,
                availability=avail
            )
            db.session.add(p)
            db.session.flush()
            prod_map[pname] = p

        # 5. Suppliers
        suppliers_data = [
            ('Golden Grain Mills', '+1 555-8811', 'orders@goldengrain.com', '45 Mill Creek Road, Kansas City, MO', 'Flour, Whole Wheat, Dry Yeast'),
            ('Sweet Valley Sugars', '+1 555-8822', 'sales@sweetvalley.com', '120 Cane Ridge Parkway, Savannah, GA', 'Cane Sugar, Brown Sugar, Icing Powder'),
            ('Alpine Dairy Co.', '+1 555-8833', 'supply@alpinedairy.com', '88 Meadowlands Highway, Madison, WI', 'European Butter, Heavy Cream, Whole Milk'),
            ('Cocoa Craft Imports', '+1 555-8844', 'trade@cocoacraft.com', '14 Port Terminal Blvd, Miami, FL', 'Belgian Dark Chocolate, Dutch Cocoa Powder'),
            ('EcoPack Solutions', '+1 555-8855', 'sales@ecopack.com', '700 Industrial Blvd, Chicago, IL', 'Cake Boxes, Pastry Bags, Ribbons'),
        ]

        sup_map = {}
        for sname, sphone, semail, saddr, sitems in suppliers_data:
            sup = Supplier(name=sname, phone=sphone, email=semail, address=saddr, items_supplied=sitems, status='Active')
            db.session.add(sup)
            db.session.flush()
            sup_map[sname] = sup

        # 6. Raw Material Ingredients
        ingredients_data = [
            ('Flour', Decimal('150.00'), 'kg', Decimal('40.00'), 'Golden Grain Mills', Decimal('1.20')),
            ('Sugar', Decimal('95.00'), 'kg', Decimal('25.00'), 'Sweet Valley Sugars', Decimal('1.50')),
            ('Butter', Decimal('8.50'), 'kg', Decimal('15.00'), 'Alpine Dairy Co.', Decimal('7.20')),  # Low stock!
            ('Eggs', Decimal('360.00'), 'pcs', Decimal('100.00'), 'Alpine Dairy Co.', Decimal('0.25')),
            ('Milk', Decimal('45.00'), 'l', Decimal('20.00'), 'Alpine Dairy Co.', Decimal('1.10')),
            ('Chocolate', Decimal('5.00'), 'kg', Decimal('10.00'), 'Cocoa Craft Imports', Decimal('14.50')), # Low stock!
            ('Cream', Decimal('18.00'), 'l', Decimal('15.00'), 'Alpine Dairy Co.', Decimal('4.80')),
            ('Yeast', Decimal('12.00'), 'kg', Decimal('5.00'), 'Golden Grain Mills', Decimal('6.00')),
            ('Cocoa Powder', Decimal('15.00'), 'kg', Decimal('8.00'), 'Cocoa Craft Imports', Decimal('9.50')),
            ('Vanilla Extract', Decimal('4.00'), 'l', Decimal('2.00'), 'Cocoa Craft Imports', Decimal('28.00')),
            ('Packaging Boxes', Decimal('200.00'), 'pcs', Decimal('50.00'), 'EcoPack Solutions', Decimal('0.85')),
        ]

        store_user_id = staff_users['store'].user_id
        for iname, qty, unit, reorder, sname, cost in ingredients_data:
            sup = sup_map.get(sname)
            ing = Ingredient(
                name=iname,
                quantity_available=qty,
                unit=unit,
                reorder_level=reorder,
                supplier_id=sup.supplier_id if sup else None,
                cost=cost,
                last_updated=datetime.utcnow()
            )
            db.session.add(ing)
            db.session.flush()

            # Initial Stock In transaction
            txn = InventoryTransaction(
                ingredient_id=ing.ingredient_id,
                transaction_type='Stock In',
                quantity=qty,
                previous_quantity=Decimal('0.00'),
                new_quantity=qty,
                reason='Initial warehouse stock setup',
                user_id=store_user_id,
                created_at=datetime.utcnow() - timedelta(days=2)
            )
            db.session.add(txn)

        # 7. Sample Orders & Invoices
        # Order 1: Delivered Online Order for Customer Emily
        order1 = Order(
            order_number='ORD-20261118-001',
            customer_id=customer_profile.customer_id,
            order_date=datetime.utcnow() - timedelta(days=1),
            order_type='Online Order',
            status='Delivered',
            subtotal=Decimal('32.25'),
            discount=Decimal('0.00'),
            tax=Decimal('1.61'),
            total_amount=Decimal('33.86'),
            payment_mode='Card',
            payment_status='Paid',
            special_instructions='Please include napkins and celebratory candles.'
        )
        db.session.add(order1)
        db.session.flush()

        item1_1 = OrderItem(
            order_id=order1.order_id,
            product_id=prod_map['Chocolate Truffle Cake'].product_id,
            item_name='Chocolate Truffle Cake',
            quantity=1,
            price=Decimal('28.50'),
            subtotal=Decimal('28.50')
        )
        item1_2 = OrderItem(
            order_id=order1.order_id,
            product_id=prod_map['Butter Croissant'].product_id,
            item_name='Butter Croissant',
            quantity=1,
            price=Decimal('3.75'),
            subtotal=Decimal('3.75')
        )
        db.session.add_all([item1_1, item1_2])

        bill1 = Bill(
            order_id=order1.order_id,
            invoice_number='INV-20261118-0001',
            subtotal=order1.subtotal,
            discount=order1.discount,
            tax=order1.tax,
            total=order1.total_amount,
            payment_mode='Card',
            payment_status='Paid',
            bill_date=order1.order_date
        )
        db.session.add(bill1)

        # Order 2: Preparing Order for Cashier Walk-in
        order2 = Order(
            order_number='ORD-20261119-002',
            customer_id=walkin_cust.customer_id,
            order_date=datetime.utcnow() - timedelta(hours=2),
            order_type='Walk-in Order',
            status='Preparing',
            subtotal=Decimal('18.50'),
            discount=Decimal('1.50'),
            tax=Decimal('0.85'),
            total_amount=Decimal('17.85'),
            payment_mode='UPI',
            payment_status='Paid',
            special_instructions='Pack pastry slices separately with divider.',
            created_by_user_id=staff_users['cashier'].user_id
        )
        db.session.add(order2)
        db.session.flush()

        item2_1 = OrderItem(
            order_id=order2.order_id,
            product_id=prod_map['Garlic Bread'].product_id,
            item_name='Garlic Bread',
            quantity=2,
            price=Decimal('5.50'),
            subtotal=Decimal('11.00')
        )
        item2_2 = OrderItem(
            order_id=order2.order_id,
            product_id=prod_map['Chocolate Pastry'].product_id,
            item_name='Chocolate Pastry',
            quantity=1,
            price=Decimal('4.25'),
            subtotal=Decimal('4.25')
        )
        item2_3 = OrderItem(
            order_id=order2.order_id,
            product_id=prod_map['Fruit Pastry'].product_id,
            item_name='Fruit Pastry',
            quantity=1,
            price=Decimal('3.25'),
            subtotal=Decimal('3.25')
        )
        db.session.add_all([item2_1, item2_2, item2_3])

        bill2 = Bill(
            order_id=order2.order_id,
            invoice_number='INV-20261119-0002',
            subtotal=order2.subtotal,
            discount=order2.discount,
            tax=order2.tax,
            total=order2.total_amount,
            payment_mode='UPI',
            payment_status='Paid',
            bill_date=order2.order_date
        )
        db.session.add(bill2)

        # Order 3: Pending Online Order for Customer David
        order3 = Order(
            order_number='ORD-20261119-003',
            customer_id=cust2.customer_id,
            order_date=datetime.utcnow() - timedelta(minutes=45),
            order_type='Online Order',
            status='Pending',
            subtotal=Decimal('34.00'),
            discount=Decimal('0.00'),
            tax=Decimal('1.70'),
            total_amount=Decimal('35.70'),
            payment_mode='Cash',
            payment_status='Pending',
            special_instructions='Ring bell upon arrival.'
        )
        db.session.add(order3)
        db.session.flush()

        item3_1 = OrderItem(
            order_id=order3.order_id,
            product_id=prod_map['Red Velvet Cake'].product_id,
            item_name='Red Velvet Cake',
            quantity=1,
            price=Decimal('29.00'),
            subtotal=Decimal('29.00')
        )
        item3_2 = OrderItem(
            order_id=order3.order_id,
            product_id=prod_map['Chocolate Chip Cookies'].product_id,
            item_name='Chocolate Chip Cookies',
            quantity=2,
            price=Decimal('2.50'),
            subtotal=Decimal('5.00')
        )
        db.session.add_all([item3_1, item3_2])

        # 8. Custom Cake Orders
        custom_cake1 = CustomCakeOrder(
            customer_id=customer_profile.customer_id,
            cake_type='Tiered Birthday Cake',
            flavour='Chocolate Truffle & Raspberry',
            size='2.5 kg',
            quantity=1,
            required_date=(datetime.utcnow() + timedelta(days=3)).date(),
            required_time='3:00 PM',
            design_notes='Golden glitter drip with pastel pink roses on top and a golden "Happy 25th Birthday Sarah" cake topper.',
            special_instructions='Eggless preparation required. Please keep refrigerating till pickup.',
            estimated_price=Decimal('85.00'),
            status='Preparing'
        )
        db.session.add(custom_cake1)

        custom_cake2 = CustomCakeOrder(
            customer_id=cust2.customer_id,
            cake_type='Wedding Fondant Cake',
            flavour='Vanilla Bean & Salted Caramel',
            size='5.0 kg',
            quantity=1,
            required_date=(datetime.utcnow() + timedelta(days=7)).date(),
            required_time='11:00 AM',
            design_notes='Three-tier minimalist white textured buttercream with cascading fresh eucalyptus and edible gold leaf.',
            special_instructions='Carefully pack in reinforced delivery crate.',
            estimated_price=Decimal('175.00'),
            status='Confirmed'
        )
        db.session.add(custom_cake2)

        db.session.commit()
        print("Database seeded successfully with all roles, products, inventory, orders, and demo accounts!")


if __name__ == '__main__':
    seed_database()
