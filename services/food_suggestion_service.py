# food_suggestion_service.py
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
import random

class FoodSuggestionService:
    """Service for suggesting food items based on dietary preferences"""

    def __init__(self, db: Session):
        self.db = db

    def get_suggestions_by_dietary_preference(
        self,
        dietary_preference: str,
        limit: int = 5
    ) -> List[Dict[str, str]]:
        """
        Get food suggestions based on dietary preference

        Args:
            dietary_preference: 'veg', 'non-veg', or 'vegan'
            limit: Maximum number of suggestions to return

        Returns:
            List of food suggestions with item details
        """

        # Map dietary preferences to database values
        diet_mapping = {
            'veg': 'vegetarian',
            'non-veg': 'non-vegetarian',
            'vegan': 'vegan'
        }

        diet_value = diet_mapping.get(dietary_preference.lower(), 'vegetarian')

        try:
            # Try to get suggestions from order items first
            suggestions = self._get_suggestions_from_orders(diet_value, limit)

            # If not enough suggestions from orders, get from cart items
            if len(suggestions) < limit:
                cart_suggestions = self._get_suggestions_from_cart(diet_value, limit - len(suggestions))
                suggestions.extend(cart_suggestions)

            # If still not enough, get from any available items
            if len(suggestions) < limit:
                general_suggestions = self._get_general_suggestions(diet_value, limit - len(suggestions))
                suggestions.extend(general_suggestions)

            return suggestions[:limit]

        except Exception as e:
            print(f"Error getting food suggestions: {str(e)}")
            return self._get_fallback_suggestions(dietary_preference)

    def _get_suggestions_from_orders(self, diet_value: str, limit: int) -> List[Dict[str, str]]:
        """Get suggestions from order items table"""
        try:
            query = text("""
                SELECT DISTINCT item_name, item_description, price, category
                FROM order_items
                WHERE LOWER(dietary_type) = LOWER(:diet_value)
                AND item_name IS NOT NULL
                ORDER BY RANDOM()
                LIMIT :limit
            """)

            result = self.db.execute(query, {"diet_value": diet_value, "limit": limit})
            suggestions = []

            for row in result:
                suggestions.append({
                    "item_name": row[0] or "Unknown Item",
                    "description": row[1] or "Delicious food item",
                    "price": f"${row[2]}" if row[2] else "Price on request",
                    "category": row[3] or "Food",
                    "source": "Popular Orders"
                })

            return suggestions

        except Exception as e:
            print(f"Error getting suggestions from orders: {str(e)}")
            return []

    def _get_suggestions_from_cart(self, diet_value: str, limit: int) -> List[Dict[str, str]]:
        """Get suggestions from cart items table"""
        try:
            query = text("""
                SELECT DISTINCT item_name, item_description, price, category
                FROM cart_items
                WHERE LOWER(dietary_type) = LOWER(:diet_value)
                AND item_name IS NOT NULL
                ORDER BY RANDOM()
                LIMIT :limit
            """)

            result = self.db.execute(query, {"diet_value": diet_value, "limit": limit})
            suggestions = []

            for row in result:
                suggestions.append({
                    "item_name": row[0] or "Unknown Item",
                    "description": row[1] or "Delicious food item",
                    "price": f"${row[2]}" if row[2] else "Price on request",
                    "category": row[3] or "Food",
                    "source": "Cart Items"
                })

            return suggestions

        except Exception as e:
            print(f"Error getting suggestions from cart: {str(e)}")
            return []

    def _get_general_suggestions(self, diet_value: str, limit: int) -> List[Dict[str, str]]:
        """Get general suggestions when specific tables don't have enough data"""
        try:
            # Try to get from any table that might have food items
            query = text("""
                SELECT DISTINCT item_name, item_description, price, category
                FROM (
                    SELECT item_name, item_description, price, category, dietary_type
                    FROM order_items
                    UNION ALL
                    SELECT item_name, item_description, price, category, dietary_type
                    FROM cart_items
                ) AS all_items
                WHERE LOWER(dietary_type) = LOWER(:diet_value)
                AND item_name IS NOT NULL
                ORDER BY RANDOM()
                LIMIT :limit
            """)

            result = self.db.execute(query, {"diet_value": diet_value, "limit": limit})
            suggestions = []

            for row in result:
                suggestions.append({
                    "item_name": row[0] or "Unknown Item",
                    "description": row[1] or "Delicious food item",
                    "price": f"${row[2]}" if row[2] else "Price on request",
                    "category": row[3] or "Food",
                    "source": "General"
                })

            return suggestions

        except Exception as e:
            print(f"Error getting general suggestions: {str(e)}")
            return []

    def _get_fallback_suggestions(self, dietary_preference: str) -> List[Dict[str, str]]:
        """Fallback suggestions when database queries fail"""
        fallback_suggestions = {
            'veg': [
                {"item_name": "Vegetable Pizza", "description": "Fresh vegetables on crispy crust", "price": "$12.99", "category": "Pizza", "source": "Fallback"},
                {"item_name": "Caesar Salad", "description": "Fresh lettuce with vegetarian dressing", "price": "$8.99", "category": "Salad", "source": "Fallback"},
                {"item_name": "Pasta Primavera", "description": "Mixed vegetables with pasta", "price": "$14.99", "category": "Pasta", "source": "Fallback"}
            ],
            'non-veg': [
                {"item_name": "Chicken Burger", "description": "Juicy chicken patty with fresh vegetables", "price": "$11.99", "category": "Burger", "source": "Fallback"},
                {"item_name": "Beef Steak", "description": "Tender beef steak cooked to perfection", "price": "$24.99", "category": "Main Course", "source": "Fallback"},
                {"item_name": "Fish & Chips", "description": "Crispy fish with golden fries", "price": "$16.99", "category": "Seafood", "source": "Fallback"}
            ],
            'vegan': [
                {"item_name": "Vegan Buddha Bowl", "description": "Quinoa, vegetables, and tahini dressing", "price": "$13.99", "category": "Bowl", "source": "Fallback"},
                {"item_name": "Vegan Tacos", "description": "Plant-based protein with fresh vegetables", "price": "$10.99", "category": "Mexican", "source": "Fallback"},
                {"item_name": "Vegan Smoothie", "description": "Mixed fruits and plant-based milk", "price": "$6.99", "category": "Beverage", "source": "Fallback"}
            ]
        }

        return fallback_suggestions.get(dietary_preference.lower(), fallback_suggestions['veg'])

    def format_suggestions_response(self, suggestions: List[Dict[str, str]], dietary_preference: str) -> str:
        """Format suggestions into a user-friendly response"""
        if not suggestions:
            return f"Sorry, I couldn't find any {dietary_preference} food suggestions at the moment. Please try again later."

        response = f"Here are some great {dietary_preference} food suggestions for you:\n\n"

        for i, suggestion in enumerate(suggestions, 1):
            response += f"{i}. **{suggestion['item_name']}**\n"
            response += f"   {suggestion['description']}\n"
            response += f"   Price: {suggestion['price']}\n"
            response += f"   Category: {suggestion['category']}\n\n"

        response += "Would you like to know more about any of these items or need different suggestions?"

        return response

    def format_suggestions_response_with_language(
        self,
        suggestions: List[Dict[str, str]],
        dietary_preference: str,
        language: str = "en"
    ) -> str:
        """Format suggestions into a user-friendly response with language support"""

        # Language-specific messages
        language_messages = {
            "en": {
                "intro": f"Here are some great {dietary_preference} food suggestions for you:",
                "fallback": f"Sorry, I couldn't find any {dietary_preference} food suggestions at the moment. Please try again later.",
                "follow_up": "Would you like to know more about any of these items or need different suggestions?"
            },
            "es": {
                "intro": f"Aquí tienes algunas excelentes sugerencias de comida {dietary_preference} para ti:",
                "fallback": f"Lo siento, no pude encontrar sugerencias de comida {dietary_preference} en este momento. Por favor, inténtalo de nuevo más tarde.",
                "follow_up": "¿Te gustaría saber más sobre alguno de estos artículos o necesitas sugerencias diferentes?"
            },
            "fr": {
                "intro": f"Voici quelques excellentes suggestions de nourriture {dietary_preference} pour vous:",
                "fallback": f"Désolé, je n'ai pas pu trouver de suggestions de nourriture {dietary_preference} pour le moment. Veuillez réessayer plus tard.",
                "follow_up": "Aimeriez-vous en savoir plus sur l'un de ces articles ou avez-vous besoin de suggestions différentes?"
            },
            "hi": {
                "intro": f"यहाँ आपके लिए कुछ बेहतरीन {dietary_preference} भोजन सुझाव हैं:",
                "fallback": f"क्षमा करें, मैं इस समय कोई {dietary_preference} भोजन सुझाव नहीं खोज सका। कृपया बाद में पुनः प्रयास करें।",
                "follow_up": "क्या आप इनमें से किसी आइटम के बारे में अधिक जानना चाहेंगे या आपको अलग सुझाव चाहिए?"
            }
        }

        # Get messages for the language, fallback to English
        messages = language_messages.get(language, language_messages["en"])

        if not suggestions:
            return messages["fallback"]

        response = f"{messages['intro']}\n\n"

        for i, suggestion in enumerate(suggestions, 1):
            response += f"{i}. **{suggestion['item_name']}**\n"
            response += f"   {suggestion['description']}\n"
            response += f"   Price: {suggestion['price']}\n"
            response += f"   Category: {suggestion['category']}\n\n"

        response += messages["follow_up"]

        return response
