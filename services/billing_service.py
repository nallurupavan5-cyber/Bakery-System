from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import random
from extensions import db
from models.order import Order, Bill
from models.settings import SystemSetting


def round_decimal(value):
    if not isinstance(value, Decimal):
        value = Decimal(str(value or 0))
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class BillingService:
    @staticmethod
    def calculate_totals(items, discount_percent=0.0, discount_amount=0.0, tax_percent=None):
        """
        Decimal-safe calculation:
        subtotal = sum(item.quantity * item.price)
        discount = discount_amount or (subtotal * discount_percent / 100)
        tax = (subtotal - discount) * tax_percent / 100
        grand_total = subtotal - discount + tax (never negative)
        """
        subtotal = Decimal('0.00')
        for item in items:
            qty = Decimal(str(item.get('quantity', 1)))
            price = Decimal(str(item.get('price', 0.0)))
            subtotal += qty * price

        subtotal = round_decimal(subtotal)

        # Tax percentage resolution
        if tax_percent is None:
            tax_str = SystemSetting.get_value('default_tax_percent', '5.0')
            tax_percent = Decimal(str(tax_str))
        else:
            tax_percent = Decimal(str(tax_percent))

        # Discount calculation
        disc_amt = Decimal(str(discount_amount or 0.0))
        if disc_amt > Decimal('0.00'):
            discount = disc_amt
        else:
            disc_pct = Decimal(str(discount_percent or 0.0))
            discount = subtotal * (disc_pct / Decimal('100.0'))

        discount = round_decimal(min(discount, subtotal))  # Prevent discount exceeding subtotal
        taxable_amount = max(Decimal('0.00'), subtotal - discount)
        tax = round_decimal(taxable_amount * (tax_percent / Decimal('100.0')))
        grand_total = max(Decimal('0.00'), subtotal - discount + tax)

        return {
            'subtotal': subtotal,
            'discount': discount,
            'tax': tax,
            'tax_percent': tax_percent,
            'total_amount': grand_total
        }

    @staticmethod
    def generate_invoice_number():
        today_str = datetime.utcnow().strftime('%Y%m%d')
        rand_num = random.randint(1000, 9999)
        return f"INV-{today_str}-{rand_num}"

    @classmethod
    def create_bill_for_order(cls, order):
        """Generates or updates a Bill record for an order."""
        if order.bill:
            bill = order.bill
        else:
            inv_num = cls.generate_invoice_number()
            # Ensure unique invoice number
            while Bill.query.filter_by(invoice_number=inv_num).first():
                inv_num = cls.generate_invoice_number()

            bill = Bill(
                order_id=order.order_id,
                invoice_number=inv_num,
                subtotal=order.subtotal,
                discount=order.discount,
                tax=order.tax,
                total=order.total_amount,
                payment_mode=order.payment_mode,
                payment_status=order.payment_status,
                bill_date=datetime.utcnow()
            )
            db.session.add(bill)
            db.session.commit()
            return bill

        bill.subtotal = order.subtotal
        bill.discount = order.discount
        bill.tax = order.tax
        bill.total = order.total_amount
        bill.payment_mode = order.payment_mode
        bill.payment_status = order.payment_status
        db.session.commit()
        return bill
