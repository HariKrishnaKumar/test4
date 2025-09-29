# helpers/cart_helper.py
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Dict, List, Optional, Any
from models.cart import Cart, CartItem, CartItemModifier
from models.user import User
from models.conversation import Session
import httpx
import os


class CartHelper:
    """Helper class for cart database operations"""

    @staticmethod
    def validate_user(db: Session, customer_id) -> bool:
        """Validate if user exists (verification check optional)"""
        # Handle both string and integer customer_id
        try:
            # Try to convert to int first
            if isinstance(customer_id, str):
                customer_id = int(customer_id)

            user = db.query(User).filter(User.id == customer_id).first()
            if user:
                print(f"✅ User found: ID={user.id}, verified={user.is_verified}, name={user.name}")
                # Return True if user exists (regardless of verification status)
                # Change this to 'return user.is_verified' if you want to require verification
                return True
            else:
                print(f"❌ User not found with ID: {customer_id}")
                return False
        except (ValueError, TypeError) as e:
            print(f"❌ Invalid customer_id format: {customer_id}, error: {e}")
            return False

    @staticmethod
    def validate_session_id(session_id: str) -> bool:
        """Validate session ID format (basic validation)"""
        if not session_id:
            return False
        # Basic validation: should be non-empty string, reasonable length
        return isinstance(session_id, str) and len(session_id.strip()) > 0 and len(session_id) <= 128

    @staticmethod
    def get_user_id_from_session(db: Session, session_id: str) -> Optional[int]:
        """Get user ID from session ID"""
        try:
            session = db.query(Session).filter(Session.id == session_id).first()
            if session and session.user_id:
                # Convert string user_id to int
                return int(session.user_id)
            return None
        except (ValueError, TypeError) as e:
            print(f"❌ Error converting session user_id to int: {e}")
            return None

    @staticmethod
    def create_cart(
        db: Session,
        merchant_id: str,
        customer_id: int = None,
        session_id: str = None
    ) -> Cart:
        """Create a new empty cart"""
        cart = Cart(
            clover_merchant_id=merchant_id,
            customer_id=customer_id,
            session_id=session_id,
            status="active"
        )
        db.add(cart)
        db.commit()
        db.refresh(cart)
        return cart

    @staticmethod
    def get_cart_by_id(db: Session, cart_id: int) -> Optional[Cart]:
        """Get cart by ID with items and modifiers"""
        return db.query(Cart).filter(Cart.id == cart_id).first()

    @staticmethod
    def get_active_cart_by_session(db: Session, session_id: str) -> Optional[Cart]:
        """Get active cart by session ID"""
        return db.query(Cart).filter(
            Cart.session_id == session_id,
            Cart.status == "active"
        ).first()

    @staticmethod
    def add_item_to_cart(
        db: Session,
        cart_id: int,
        clover_item_id: str,
        name: str,
        price: float,
        quantity: int = 1,
        notes: str = None
    ) -> CartItem:
        """Add an item to cart"""
        # Check if item already exists in cart
        existing_item = db.query(CartItem).filter(
            CartItem.cart_id == cart_id,
            CartItem.clover_item_id == clover_item_id
        ).first()

        if existing_item:
            # Update quantity and totals
            existing_item.quantity += quantity
            existing_item.line_total = existing_item.price * existing_item.quantity
            existing_item.updated_at = datetime.now()
            db.commit()
            db.refresh(existing_item)
            CartHelper._update_cart_totals(db, cart_id)
            return existing_item
        else:
            # Create new item
            cart_item = CartItem(
                cart_id=cart_id,
                clover_item_id=clover_item_id,
                name=name,
                price=price,
                quantity=quantity,
                line_total=price * quantity,
                notes=notes
            )
            db.add(cart_item)
            db.commit()
            db.refresh(cart_item)
            CartHelper._update_cart_totals(db, cart_id)
            return cart_item

    @staticmethod
    def update_item_quantity(
        db: Session,
        cart_item_id: int,
        quantity: int
    ) -> Optional[CartItem]:
        """Update cart item quantity"""
        cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
        if not cart_item:
            return None

        if quantity <= 0:
            # Remove item if quantity is 0 or negative
            cart_id = cart_item.cart_id
            db.delete(cart_item)
            db.commit()
            CartHelper._update_cart_totals(db, cart_id)
            return None

        cart_item.quantity = quantity
        cart_item.line_total = cart_item.price * quantity
        cart_item.updated_at = datetime.now()
        db.commit()
        db.refresh(cart_item)
        CartHelper._update_cart_totals(db, cart_item.cart_id)
        return cart_item

    @staticmethod
    def remove_item_from_cart(db: Session, cart_item_id: int) -> bool:
        """Remove an item from cart"""
        cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
        if not cart_item:
            return False

        cart_id = cart_item.cart_id
        db.delete(cart_item)
        db.commit()
        CartHelper._update_cart_totals(db, cart_id)
        return True

    @staticmethod
    def add_modifier_to_item(
        db: Session,
        cart_item_id: int,
        clover_modifier_id: str,
        clover_modifier_group_id: str,
        name: str,
        price: float = 0.0
    ) -> CartItemModifier:
        """Add a modifier to a cart item"""
        modifier = CartItemModifier(
            cart_item_id=cart_item_id,
            clover_modifier_id=clover_modifier_id,
            clover_modifier_group_id=clover_modifier_group_id,
            name=name,
            price=price
        )
        db.add(modifier)
        db.commit()
        db.refresh(modifier)

        # Update cart totals
        cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
        if cart_item:
            CartHelper._update_cart_totals(db, cart_item.cart_id)

        return modifier

    @staticmethod
    def clear_cart(db: Session, cart_id: int) -> bool:
        """Clear all items from cart"""
        cart = db.query(Cart).filter(Cart.id == cart_id).first()
        if not cart:
            return False

        # Delete all items (modifiers will be deleted via cascade)
        db.query(CartItem).filter(CartItem.id == cart_id).delete()
        db.commit()
        CartHelper._update_cart_totals(db, cart_id)
        return True

    @staticmethod
    def _update_cart_totals(db: Session, cart_id: int):
        """Update cart totals based on items and modifiers"""
        cart = db.query(Cart).filter(Cart.id == cart_id).first()
        if not cart:
            return

        # Calculate subtotal from items
        subtotal = 0.0
        for item in cart.items:
            item_total = item.line_total
            # Add modifier costs
            modifier_total = sum(mod.price for mod in item.modifiers)
            item_total += (modifier_total * item.quantity)
            subtotal += item_total

        # For now, set tax and discount to 0 (can be enhanced later)
        tax_amount = 0.0
        discount_amount = 0.0
        total_amount = subtotal + tax_amount - discount_amount

        # Update cart
        cart.subtotal = subtotal
        cart.total_amount = total_amount
        cart.updated_at = datetime.now()

        db.commit()

    @staticmethod
    def get_cart_summary(db: Session, cart_id: int) -> Optional[Dict]:
        """Get cart summary with all details"""
        cart = db.query(Cart).filter(Cart.id == cart_id).first()
        if not cart:
            return None

        items = []
        for item in cart.items:
            modifiers = [
                {
                    "id": mod.id,
                    "clover_modifier_id": mod.clover_modifier_id,
                    "clover_modifier_group_id": mod.clover_modifier_group_id,
                    "name": mod.name,
                    "price": mod.price
                }
                for mod in item.modifiers
            ]

            items.append({
                "id": item.id,
                "clover_item_id": item.clover_item_id,
                "name": item.name,
                "price": item.price,
                "quantity": item.quantity,
                "line_total": item.line_total,
                "notes": item.notes,
                "modifiers": modifiers
            })

        return {
            "cart_id": cart.id,
            "merchant_id": cart.clover_merchant_id,
            "customer_id": cart.customer_id,
            "session_id": cart.session_id,
            "status": cart.status,
            "subtotal": cart.subtotal,
            "total_amount": cart.total_amount,
            "items": items,
            "created_at": cart.created_at.isoformat() if cart.created_at else None,
            "updated_at": cart.updated_at.isoformat() if cart.updated_at else None
        }

    @staticmethod
    def get_carts_by_customer(db: Session, customer_id: int) -> List[Dict]:
        """Get all carts for a specific customer"""
        carts = db.query(Cart).filter(
            Cart.customer_id == customer_id
        ).order_by(Cart.created_at.desc()).all()

        cart_summaries = []
        for cart in carts:
            summary = CartHelper.get_cart_summary(db, cart.id)
            if summary:
                cart_summaries.append(summary)

        return cart_summaries
