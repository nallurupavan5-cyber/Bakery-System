import pytest
from decimal import Decimal
from models.inventory import Ingredient
from services.inventory_service import InventoryService


def test_stock_in(app):
    with app.app_context():
        ing = Ingredient.query.filter_by(name='Flour').first()
        initial_stock = ing.quantity_available

        InventoryService.record_stock_in(ing.ingredient_id, 25.0, reason='Weekly shipment')
        
        updated_ing = Ingredient.query.get(ing.ingredient_id)
        assert updated_ing.quantity_available == initial_stock + Decimal('25.00')


def test_stock_out(app):
    with app.app_context():
        ing = Ingredient.query.filter_by(name='Flour').first()
        initial_stock = ing.quantity_available

        InventoryService.record_stock_out(ing.ingredient_id, 10.0, reason='Bread production')

        updated_ing = Ingredient.query.get(ing.ingredient_id)
        assert updated_ing.quantity_available == initial_stock - Decimal('10.00')


def test_negative_stock_prevention(app):
    with app.app_context():
        ing = Ingredient.query.filter_by(name='Butter').first()
        # Butter has 5.0 kg available. Trying to take out 20.0 kg must raise ValueError!
        with pytest.raises(ValueError) as excinfo:
            InventoryService.record_stock_out(ing.ingredient_id, 20.0, reason='Oversized batch')

        assert 'Insufficient stock' in str(excinfo.value)
        # Verify stock remained unchanged
        refreshed = Ingredient.query.get(ing.ingredient_id)
        assert refreshed.quantity_available == Decimal('5.00')


def test_low_stock_detection(app):
    with app.app_context():
        low_items = InventoryService.get_low_stock_items()
        low_names = [i.name for i in low_items]
        # Butter has 5.00 kg with reorder level 10.00 kg -> Must be flagged low stock!
        assert 'Butter' in low_names
        # Flour has 50.00 kg with reorder level 20.00 kg -> Must NOT be in low items
        assert 'Flour' not in low_names
