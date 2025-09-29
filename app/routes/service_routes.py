from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from database.database import get_db
from models.service import (
    ServiceSelectionRequest,
    ServiceSelectionResponse,
    ServiceResponse,
    Service,
    UserService
)
from services.service_selection_service import ServiceSelectionService

router = APIRouter()

@router.post("/select", response_model=ServiceSelectionResponse)
async def select_service(
    request: ServiceSelectionRequest,
    db: Session = Depends(get_db)
):
    """
    Select service via text or voice input
    - For text input: directly save the selected service
    - For voice input: use AI to detect and extract service from voice text
    """
    try:
        service_selection_service = ServiceSelectionService()

        # Ensure default services exist
        service_selection_service.create_default_services(db)

        # Validate input
        if not request.service_text or not request.service_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Service text cannot be empty"
            )

        # Process based on input type
        if request.input_type == "text":
            # Direct text input - use as is
            selected_service = request.service_text.strip()
            detected_services = [selected_service]

        elif request.input_type == "voice":
            # Voice input - use AI to detect services
            detected_services = service_selection_service.detect_services_from_text(request.service_text)
            selected_service = service_selection_service.get_primary_service(detected_services)

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input_type. Must be 'text' or 'voice'"
            )

        # Validate the selected service
        if not service_selection_service.validate_service(selected_service):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid service name"
            )

        # Get service ID
        service_id = service_selection_service.get_service_id_by_name(db, selected_service)
        if not service_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service '{selected_service}' not found"
            )

        # Save to user services
        success = service_selection_service.save_user_service_selection(
            db=db,
            user_id=request.user_id,
            service_name=selected_service,
            input_type=request.input_type
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save service selection"
            )

        return ServiceSelectionResponse(
            success=True,
            message=f"Service '{selected_service}' selected successfully",
            selected_service=selected_service,
            user_id=request.user_id,
            detected_services=detected_services if request.input_type == "voice" else None,
            service_id=service_id
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("/user/{user_id}")
async def get_user_services(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all services selected by a user
    """
    try:
        service_selection_service = ServiceSelectionService()
        user_services = service_selection_service.get_user_services(db, user_id)

        return {
            "success": True,
            "user_id": user_id,
            "services": user_services,
            "total_services": len(user_services)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("/available", response_model=List[ServiceResponse])
async def get_available_services(
    db: Session = Depends(get_db)
):
    """
    Get list of available services
    """
    try:
        service_selection_service = ServiceSelectionService()
        # Ensure default services exist
        service_selection_service.create_default_services(db)

        services = db.query(Service).filter(Service.is_active == 'true').all()
        return [ServiceResponse.from_orm(service) for service in services]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.post("/available", response_model=ServiceResponse)
async def add_service(
    service_name: str,
    service_description: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Add a new service to the available services list
    """
    try:
        # Check if service already exists
        existing = db.query(Service).filter(
            Service.service_name == service_name
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Service already exists"
            )

        # Create new service
        service = Service(
            service_name=service_name,
            service_description=service_description,
            is_active='true'
        )

        db.add(service)
        db.commit()
        db.refresh(service)

        return ServiceResponse.from_orm(service)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.post("/detect")
async def detect_services(
    text: str,
    db: Session = Depends(get_db)
):
    """
    Detect services from text using AI (for testing/debugging)
    """
    try:
        service_selection_service = ServiceSelectionService()
        detected_services = service_selection_service.detect_services_from_text(text)
        primary_service = service_selection_service.get_primary_service(detected_services)

        return {
            "success": True,
            "input_text": text,
            "detected_services": detected_services,
            "primary_service": primary_service
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.delete("/user/{user_id}/service/{service_id}")
async def remove_user_service(
    user_id: str,
    service_id: int,
    db: Session = Depends(get_db)
):
    """
    Remove a service selection for a user
    """
    try:
        # Find the user service record
        user_service = db.query(UserService).filter(
            UserService.user_id == user_id,
            UserService.service_id == service_id
        ).first()

        if not user_service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User service selection not found"
            )

        # Get service name for response
        service = db.query(Service).filter(Service.id == service_id).first()
        service_name = service.service_name if service else "Unknown"

        # Delete the record
        db.delete(user_service)
        db.commit()

        return {
            "success": True,
            "message": f"Service '{service_name}' removed from user {user_id}",
            "user_id": user_id,
            "service_id": service_id
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("/user/{user_id}/latest")
async def get_latest_user_service(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the latest service selected by a user
    """
    try:
        latest_service = db.query(UserService, Service).join(
            Service, UserService.service_id == Service.id
        ).filter(
            UserService.user_id == user_id,
            Service.is_active == 'true'
        ).order_by(UserService.selected_at.desc()).first()

        if not latest_service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No service found for this user"
            )

        user_service, service = latest_service

        return {
            "success": True,
            "user_id": user_id,
            "service": {
                "id": user_service.id,
                "service_id": user_service.service_id,
                "service_name": service.service_name,
                "selected_at": user_service.selected_at
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
