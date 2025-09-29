from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from database.database import get_db
from models.language import (
    LanguageSelectionRequest,
    LanguageSelectionResponse,
    LanguageResponse,
    Language
)
from services.language_service import LanguageService

router = APIRouter()

@router.post("/select", response_model=LanguageSelectionResponse)
async def select_language(
    request: LanguageSelectionRequest,
    db: Session = Depends(get_db)
):
    """
    Select language via text or voice input
    - For text input: directly save the selected language
    - For voice input: use AI to detect and extract language from voice text
    """
    try:
        language_service = LanguageService()

        # Validate input
        if not request.language_text or not request.language_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Language text cannot be empty"
            )

        # Process based on input type
        if request.input_type == "text":
            # Direct text input - use as is
            selected_language = request.language_text.strip()
            detected_languages = [selected_language]

        elif request.input_type == "voice":
            # Voice input - use AI to detect languages
            detected_languages = language_service.detect_languages_from_text(request.language_text)
            selected_language = language_service.get_primary_language(detected_languages)

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input_type. Must be 'text' or 'voice'"
            )

        # Validate the selected language
        if not language_service.validate_language(selected_language):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid language name"
            )

        # Save to session
        success = language_service.save_language_to_session(
            db=db,
            session_id=request.session_id,
            user_id=request.user_id,
            language_name=selected_language,
            input_type=request.input_type
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save language selection"
            )

        return LanguageSelectionResponse(
            success=True,
            message=f"Language '{selected_language}' selected successfully",
            selected_language=selected_language,
            session_id=request.session_id,
            user_id=request.user_id,
            detected_languages=detected_languages if request.input_type == "voice" else None
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("/session/{session_id}")
async def get_session_language(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the current language for a session
    """
    try:
        language_service = LanguageService()
        language = language_service.get_language_from_session(db, session_id)

        if not language:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No language set for this session"
            )

        return {
            "success": True,
            "session_id": session_id,
            "language": language
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("/available", response_model=List[LanguageResponse])
async def get_available_languages(
    db: Session = Depends(get_db)
):
    """
    Get list of available languages
    """
    try:
        languages = db.query(Language).all()
        return [LanguageResponse.from_orm(lang) for lang in languages]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

# @router.post("/available", response_model=LanguageResponse)
# async def add_language(
#     language_name: str,
#     language_code: Optional[str] = None,
#     db: Session = Depends(get_db)
# ):
#     """
#     Add a new language to the available languages list
#     """
#     try:
#         # Check if language already exists
#         existing = db.query(Language).filter(
#             Language.language_name == language_name
#         ).first()

#         if existing:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Language already exists"
#             )

#         # Create new language
#         language = Language(
#             language_name=language_name,
#             language_code=language_code
#         )

#         db.add(language)
#         db.commit()
#         db.refresh(language)

#         return LanguageResponse.from_orm(language)

#     except HTTPException:
#         raise
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred: {str(e)}"
#         )

# @router.post("/detect")
# async def detect_languages(
#     text: str,
#     db: Session = Depends(get_db)
# ):
#     """
#     Detect languages from text using AI (for testing/debugging)
#     """
#     try:
#         language_service = LanguageService()
#         detected_languages = language_service.detect_languages_from_text(text)
#         primary_language = language_service.get_primary_language(detected_languages)

#         return {
#             "success": True,
#             "input_text": text,
#             "detected_languages": detected_languages,
#             "primary_language": primary_language
#         }

#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred: {str(e)}"
#         )
