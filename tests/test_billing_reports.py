from decimal import Decimal
from services.billing_service import BillingService
from services.report_service import ReportService


def test_billing_calculation_exactness():
    # 2 items: 2 x $28.50 ($57.00), 3 x $3.50 ($10.50) -> subtotal $67.50
    items = [
        {'quantity': 2, 'price': Decimal('28.50')},
        {'quantity': 3, 'price': Decimal('3.50')}
    ]

    # Test without discount, 5% tax
    calc = BillingService.calculate_totals(items, discount_percent=0.0, tax_percent=5.0)
    assert calc['subtotal'] == Decimal('67.50')
    assert calc['discount'] == Decimal('0.00')
    # 67.50 * 0.05 = 3.375 -> rounded to 3.38
    assert calc['tax'] == Decimal('3.38')
    assert calc['total_amount'] == Decimal('70.88')

    # Test with 10% discount and 5% tax
    calc_disc = BillingService.calculate_totals(items, discount_percent=10.0, tax_percent=5.0)
    # Discount: 67.50 * 0.10 = 6.75
    assert calc_disc['discount'] == Decimal('6.75')
    # Taxable: 67.50 - 6.75 = 60.75
    # Tax: 60.75 * 0.05 = 3.0375 -> 3.04
    assert calc_disc['tax'] == Decimal('3.04')
    # Total: 60.75 + 3.04 = 63.79
    assert calc_disc['total_amount'] == Decimal('63.79')


def test_billing_negative_discount_capping():
    # Attempting to give a $100 discount on a $50 purchase should be capped at $50
    items = [{'quantity': 1, 'price': Decimal('50.00')}]
    calc = BillingService.calculate_totals(items, discount_amount=100.0, tax_percent=5.0)
    assert calc['subtotal'] == Decimal('50.00')
    assert calc['discount'] == Decimal('50.00')
    assert calc['tax'] == Decimal('0.00')
    assert calc['total_amount'] == Decimal('0.00')


def test_dashboard_summary_and_csv_generation(app):
    with app.app_context():
        summary = ReportService.get_dashboard_summary()
        assert 'today_sales' in summary
        assert 'total_products' in summary
        assert summary['total_products'] >= 1

        # Test CSV generator
        csv_sales = ReportService.generate_csv_report('sales')
        assert 'Order Number' in csv_sales

        csv_inventory = ReportService.generate_csv_report('inventory')
        assert 'Ingredient ID' in csv_inventory
        assert 'Flour' in csv_inventory
