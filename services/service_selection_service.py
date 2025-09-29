# service_selection_service.py
from typing import Optional, List, Dict
import google.generativeai as genai
import os
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
import json
from models.service import Service, UserService
from dotenv import load_dotenv
import re

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class ServiceSelectionService:
    """Service for processing service selection with AI support"""

    def __init__(self):
        self.api_key = GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def detect_services_from_text(self, text: str) -> List[str]:
        """
        Detect services from user text using AI
        Returns a list of detected services
        """
        prompt = f"""You are a service detection assistant. Analyze the following text and identify which food service the user is requesting.

User text: "{text}"

Available services:
1. Delivery - Home delivery, bringing food to customer's address
2. Pickup - Customer picks up food themselves, takeaway
3. Reservation - Table reservation for dining in
4. Catering - Food service for events, parties, bulk orders
5. Events - Special event planning and food service

Instructions:
1. Identify which service(s) the user is requesting
2. Return only the service names (e.g., "Delivery", "Pickup", "Reservation", "Catering", "Events")
3. If multiple services are mentioned, return them as a comma-separated list
4. If no specific service is mentioned, return "Delivery" as default
5. Return only the service names, nothing else

Examples:
- "I want delivery at my house" -> Delivery
- "I'll pick it up myself" -> Pickup
- "I need catering for my event" -> Catering
- "I want to book for an event" -> Events
- "I need both delivery and catering" -> Delivery, Catering

Response:"""

        try:
            response = self.model.generate_content(prompt)
            services_text = response.text.strip()

            # Parse the response and clean up
            services = [service.strip() for service in services_text.split(',')]
            services = [service for service in services if service and service.lower() != 'none']

            # If no services detected, default to Delivery
            if not services:
                services = ['Delivery']

            return services

        except Exception as e:
            print(f"Service detection error: {str(e)}")
            return ['Delivery']  # Default fallback

    def get_primary_service(self, services: List[str]) -> str:
        """
        Get the primary service from a list of services
        For user selection, we'll use the first service mentioned
        """
        if not services:
            return 'Delivery'

        # Return the first service as primary
        return services[0]

    def validate_service(self, service_name: str) -> bool:
        """
        Validate if the service name is valid
        """
        if not service_name or not service_name.strip():
            return False

        # Basic validation - check if it's a reasonable service name
        service_name = service_name.strip()
        if len(service_name) < 2 or len(service_name) > 50:
            return False

        # Check for valid service types
        valid_services = [
            'Delivery', 'Pickup', 'Reservation', 'Catering', 'Events'
        ]

        # Check if it matches any valid service (case insensitive)
        for service in valid_services:
            if service_name.lower() == service.lower():
                return True

        return False

    def get_service_id_by_name(self, db: Session, service_name: str) -> Optional[int]:
        """
        Get service ID by service name
        """
        try:
            service = db.query(Service).filter(
                Service.service_name == service_name,
                Service.is_active == 'true'
            ).first()
            return service.id if service else None
        except Exception as e:
            print(f"Error getting service ID: {str(e)}")
            return None

    def save_user_service_selection(self, db: Session, user_id: str, service_name: str, input_type: str = None) -> bool:
        """
        Save user service selection to database
        """
        try:
            # Get service ID
            service_id = self.get_service_id_by_name(db, service_name)
            if not service_id:
                print(f"Service '{service_name}' not found in database")
                return False

            # Check if user already has this service selected
            existing = db.query(UserService).filter(
                UserService.user_id == user_id,
                UserService.service_id == service_id
            ).first()

            if existing:
                # Update existing selection
                existing.selected_at = func.now()
                existing.input_type = input_type
                db.commit()
                return True
            else:
                # Create new selection
                user_service = UserService(
                    user_id=user_id,
                    service_id=service_id,
                    input_type=input_type
                )
                db.add(user_service)
                db.commit()
                return True

        except Exception as e:
            print(f"Error saving user service selection: {str(e)}")
            db.rollback()
            return False

    def get_user_services(self, db: Session, user_id: str) -> List[Dict]:
        """
        Get all services selected by a user
        """
        try:
            user_services = db.query(UserService, Service).join(
                Service, UserService.service_id == Service.id
            ).filter(
                UserService.user_id == user_id,
                Service.is_active == 'true'
            ).all()

            result = []
            for user_service, service in user_services:
                result.append({
                    'id': user_service.id,
                    'user_id': user_service.user_id,
                    'service_id': user_service.service_id,
                    'service_name': service.service_name,
                    'input_type': user_service.input_type,
                    'selected_at': user_service.selected_at
                })

            return result

        except Exception as e:
            print(f"Error getting user services: {str(e)}")
            return []

    def get_available_services(self, db: Session) -> List[Dict]:
        """
        Get all available services
        """
        try:
            services = db.query(Service).filter(Service.is_active == 'true').all()
            return [
                {
                    'id': service.id,
                    'service_name': service.service_name,
                    'service_description': service.service_description,
                    'is_active': service.is_active
                }
                for service in services
            ]
        except Exception as e:
            print(f"Error getting available services: {str(e)}")
            return []

    def create_default_services(self, db: Session) -> bool:
        """
        Create default services if they don't exist
        """
        try:
            default_services = [
                {
                    'service_name': 'Delivery',
                    'service_description': 'Home delivery service - bringing food to your address'
                },
                {
                    'service_name': 'Pickup',
                    'service_description': 'Self-pickup service - collect your order from our location'
                },
                {
                    'service_name': 'Reservation',
                    'service_description': 'Table reservation service - book a table for dining in'
                },
                {
                    'service_name': 'Catering',
                    'service_description': 'Catering service - food service for events and parties'
                },
                {
                    'service_name': 'Events',
                    'service_description': 'Event planning service - special event food and service support'
                }
            ]

            for service_data in default_services:
                existing = db.query(Service).filter(
                    Service.service_name == service_data['service_name']
                ).first()

                if not existing:
                    service = Service(
                        service_name=service_data['service_name'],
                        service_description=service_data['service_description'],
                        is_active='true'
                    )
                    db.add(service)

            db.commit()
            return True

        except Exception as e:
            print(f"Error creating default services: {str(e)}")
            db.rollback()
            return False
