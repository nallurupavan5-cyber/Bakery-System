from decimal import Decimal
from datetime import datetime
from extensions import db
from models.inventory import Ingredient, InventoryTransaction


class InventoryService:
    @staticmethod
    def get_low_stock_items():
        """Returns all ingredients where quantity_available <= reorder_level."""
        return Ingredient.query.filter(Ingredient.quantity_available <= Ingredient.reorder_level).all()

    @staticmethod
    def record_stock_in(ingredient_id, quantity, user_id=None, reason="Stock In"):
        quantity = Decimal(str(quantity))
        if quantity <= Decimal('0.00'):
            raise ValueError("Stock In quantity must be strictly greater than zero.")

        ingredient = Ingredient.query.get_or_404(ingredient_id)
        prev_qty = ingredient.quantity_available or Decimal('0.00')
        new_qty = prev_qty + quantity

        ingredient.quantity_available = new_qty
        ingredient.last_updated = datetime.utcnow()

        txn = InventoryTransaction(
            ingredient_id=ingredient.ingredient_id,
            transaction_type='Stock In',
            quantity=quantity,
            previous_quantity=prev_qty,
            new_quantity=new_qty,
            reason=reason,
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        db.session.add(txn)
        db.session.commit()
        return ingredient, txn

    @staticmethod
    def record_stock_out(ingredient_id, quantity, user_id=None, reason="Stock Out"):
        quantity = Decimal(str(quantity))
        if quantity <= Decimal('0.00'):
            raise ValueError("Stock Out quantity must be strictly greater than zero.")

        ingredient = Ingredient.query.get_or_404(ingredient_id)
        prev_qty = ingredient.quantity_available or Decimal('0.00')

        if prev_qty < quantity:
            raise ValueError(
                f"Insufficient stock for '{ingredient.name}'. Available: {prev_qty} {ingredient.unit}, requested: {quantity} {ingredient.unit}."
            )

        new_qty = prev_qty - quantity
        ingredient.quantity_available = new_qty
        ingredient.last_updated = datetime.utcnow()

        txn = InventoryTransaction(
            ingredient_id=ingredient.ingredient_id,
            transaction_type='Stock Out',
            quantity=quantity,
            previous_quantity=prev_qty,
            new_quantity=new_qty,
            reason=reason,
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        db.session.add(txn)
        db.session.commit()
        return ingredient, txn

    @staticmethod
    def adjust_stock(ingredient_id, new_quantity, user_id=None, reason="Inventory Audit / Stock Adjustment"):
        new_quantity = Decimal(str(new_quantity))
        if new_quantity < Decimal('0.00'):
            raise ValueError("Stock quantity cannot be negative.")

        ingredient = Ingredient.query.get_or_404(ingredient_id)
        prev_qty = ingredient.quantity_available or Decimal('0.00')
        diff = new_quantity - prev_qty

        ingredient.quantity_available = new_quantity
        ingredient.last_updated = datetime.utcnow()

        txn = InventoryTransaction(
            ingredient_id=ingredient.ingredient_id,
            transaction_type='Adjustment',
            quantity=abs(diff),
            previous_quantity=prev_qty,
            new_quantity=new_quantity,
            reason=f"{reason} (Adjustment: {diff:+.2f} {ingredient.unit})",
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        db.session.add(txn)
        db.session.commit()
        return ingredient, txn
