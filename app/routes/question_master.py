from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from database.database import get_db
from models.question_model import QuestionMaster, QuestionTranslation

router = APIRouter(prefix="/api/v1/questions", tags=["question-master"])


# Pydantic models for Question Master
class QuestionCreate(BaseModel):
    question_key: str
    question_text: str
    question_order: int
    type: Optional[str] = None
    is_active: bool = True

class QuestionUpdate(BaseModel):
    question_key: Optional[str] = None
    question_text: Optional[str] = None
    question_order: Optional[int] = None
    type: Optional[str] = None
    is_active: Optional[bool] = None

class QuestionResponse(BaseModel):
    id: int
    question_key: str
    question_text: str
    question_order: int
    type: Optional[str] = None
    is_active: bool
    created_at: str
    updated_at: Optional[str] = None

# Pydantic models for Question Translations
class TranslationCreate(BaseModel):
    question_key: str
    language: str
    translated_text: str
    variant: Optional[str] = None

class TranslationUpdate(BaseModel):
    translated_text: Optional[str] = None
    variant: Optional[str] = None

class TranslationResponse(BaseModel):
    id: int
    question_key: str
    language: str
    translated_text: str
    variant: Optional[str] = None

class QuestionWithTranslationsResponse(BaseModel):
    question: QuestionResponse
    translations: List[TranslationResponse] = []


# Question Master CRUD Operations
@router.post("/", response_model=QuestionResponse)
async def create_question(
    question_data: QuestionCreate,
    db: Session = Depends(get_db)
):
    """Create a new question (English only)"""
    try:
        # Check if question_key already exists
        existing = db.query(QuestionMaster).filter(
            QuestionMaster.question_key == question_data.question_key
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Question with key '{question_data.question_key}' already exists"
            )

        # Create new question
        question = QuestionMaster(
            question_key=question_data.question_key,
            question_text=question_data.question_text,
            question_order=question_data.question_order,
            type=question_data.type,
            is_active=question_data.is_active
        )

        db.add(question)
        db.commit()
        db.refresh(question)

        return QuestionResponse(
            id=question.id,
            question_key=question.question_key,
            question_text=question.question_text,
            question_order=question.question_order,
            type=question.type,
            is_active=question.is_active,
            created_at=question.created_at.isoformat(),
            updated_at=question.updated_at.isoformat() if question.updated_at else None
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create question: {str(e)}")


@router.get("/", response_model=List[QuestionResponse])
async def get_all_questions(
    type: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all questions (English only)"""
    query = db.query(QuestionMaster)

    if type:
        query = query.filter(QuestionMaster.type == type)

    if active_only:
        query = query.filter(QuestionMaster.is_active == True)

    questions = query.order_by(QuestionMaster.question_order).all()

    return [
        QuestionResponse(
            id=q.id,
            question_key=q.question_key,
            question_text=q.question_text,
            question_order=q.question_order,
            type=q.type,
            is_active=q.is_active,
            created_at=q.created_at.isoformat(),
            updated_at=q.updated_at.isoformat() if q.updated_at else None
        ) for q in questions
    ]


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(question_id: int, db: Session = Depends(get_db)):
    """Get question by ID"""
    question = db.query(QuestionMaster).filter(QuestionMaster.id == question_id).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    return QuestionResponse(
        id=question.id,
        question_key=question.question_key,
        question_text=question.question_text,
        question_order=question.question_order,
        type=question.type,
        is_active=question.is_active,
        created_at=question.created_at.isoformat(),
        updated_at=question.updated_at.isoformat() if question.updated_at else None
    )


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int,
    question_data: QuestionUpdate,
    db: Session = Depends(get_db)
):
    """Update question"""
    question = db.query(QuestionMaster).filter(QuestionMaster.id == question_id).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    try:
        # Update fields
        update_data = question_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(question, field, value)

        db.commit()
        db.refresh(question)

        return QuestionResponse(
            id=question.id,
            question_key=question.question_key,
            question_text=question.question_text,
            question_order=question.question_order,
            type=question.type,
            is_active=question.is_active,
            created_at=question.created_at.isoformat(),
            updated_at=question.updated_at.isoformat() if question.updated_at else None
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update question: {str(e)}")


@router.delete("/{question_id}")
async def delete_question(question_id: int, db: Session = Depends(get_db)):
    """Delete question (soft delete by setting is_active=False)"""
    question = db.query(QuestionMaster).filter(QuestionMaster.id == question_id).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    try:
        # Soft delete
        question.is_active = False
        db.commit()

        return {"success": True, "message": f"Question '{question.question_key}' deactivated successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete question: {str(e)}")


# Translation CRUD Operations
@router.post("/translations", response_model=TranslationResponse)
async def add_translation(
    translation_data: TranslationCreate,
    db: Session = Depends(get_db)
):
    """Add translation for a question"""
    try:
        # Check if question_key exists in question_masters
        question_exists = db.query(QuestionMaster).filter(
            QuestionMaster.question_key == translation_data.question_key
        ).first()

        if not question_exists:
            raise HTTPException(
                status_code=404,
                detail=f"Question with key '{translation_data.question_key}' not found"
            )

        # Check if translation already exists
        existing_translation = db.query(QuestionTranslation).filter(
            QuestionTranslation.question_key == translation_data.question_key,
            QuestionTranslation.language == translation_data.language
        ).first()

        if existing_translation:
            raise HTTPException(
                status_code=400,
                detail=f"Translation for question '{translation_data.question_key}' in language '{translation_data.language}' already exists"
            )

        # Create new translation
        translation = QuestionTranslation(
            question_key=translation_data.question_key,
            language=translation_data.language,
            translated_text=translation_data.translated_text,
            variant=translation_data.variant
        )

        db.add(translation)
        db.commit()
        db.refresh(translation)

        return TranslationResponse(
            id=translation.id,
            question_key=translation.question_key,
            language=translation.language,
            translated_text=translation.translated_text,
            variant=translation.variant
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add translation: {str(e)}")


@router.get("/translations", response_model=List[TranslationResponse])
async def get_all_translations(
    language: Optional[str] = None,
    question_key: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all translations with optional filtering"""
    query = db.query(QuestionTranslation)

    if language:
        query = query.filter(QuestionTranslation.language == language)

    if question_key:
        query = query.filter(QuestionTranslation.question_key == question_key)

    translations = query.all()

    return [
        TranslationResponse(
            id=t.id,
            question_key=t.question_key,
            language=t.language,
            translated_text=t.translated_text,
            variant=t.variant
        ) for t in translations
    ]


@router.get("/translations/{translation_id}", response_model=TranslationResponse)
async def get_translation(translation_id: int, db: Session = Depends(get_db)):
    """Get translation by ID"""
    translation = db.query(QuestionTranslation).filter(
        QuestionTranslation.id == translation_id
    ).first()

    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")

    return TranslationResponse(
        id=translation.id,
        question_key=translation.question_key,
        language=translation.language,
        translated_text=translation.translated_text,
        variant=translation.variant
    )


@router.put("/translations/{translation_id}", response_model=TranslationResponse)
async def update_translation(
    translation_id: int,
    translation_data: TranslationUpdate,
    db: Session = Depends(get_db)
):
    """Update translation"""
    translation = db.query(QuestionTranslation).filter(
        QuestionTranslation.id == translation_id
    ).first()

    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")

    try:
        # Update fields
        update_data = translation_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(translation, field, value)

        db.commit()
        db.refresh(translation)

        return TranslationResponse(
            id=translation.id,
            question_key=translation.question_key,
            language=translation.language,
            translated_text=translation.translated_text,
            variant=translation.variant
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update translation: {str(e)}")


@router.delete("/translations/{translation_id}")
async def delete_translation(translation_id: int, db: Session = Depends(get_db)):
    """Delete translation"""
    translation = db.query(QuestionTranslation).filter(
        QuestionTranslation.id == translation_id
    ).first()

    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")

    try:
        db.delete(translation)
        db.commit()

        return {"success": True, "message": "Translation deleted successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete translation: {str(e)}")


# Combined Operations
@router.get("/{question_key}/with-translations", response_model=QuestionWithTranslationsResponse)
async def get_question_with_translations(question_key: str, db: Session = Depends(get_db)):
    """Get question with all its translations"""
    # Get the main question
    question = db.query(QuestionMaster).filter(
        QuestionMaster.question_key == question_key
    ).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Get all translations
    translations = db.query(QuestionTranslation).filter(
        QuestionTranslation.question_key == question_key
    ).all()

    question_response = QuestionResponse(
        id=question.id,
        question_key=question.question_key,
        question_text=question.question_text,
        question_order=question.question_order,
        type=question.type,
        is_active=question.is_active,
        created_at=question.created_at.isoformat(),
        updated_at=question.updated_at.isoformat() if question.updated_at else None
    )

    translation_responses = [
        TranslationResponse(
            id=t.id,
            question_key=t.question_key,
            language=t.language,
            translated_text=t.translated_text,
            variant=t.variant
        ) for t in translations
    ]

    return QuestionWithTranslationsResponse(
        question=question_response,
        translations=translation_responses
    )


@router.get("/localized/{language}", response_model=List[dict])
async def get_localized_questions(
    language: str = "en",
    type: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get questions in specified language (English from master, others from translations)"""
    query = db.query(QuestionMaster)

    if type:
        query = query.filter(QuestionMaster.type == type)

    if active_only:
        query = query.filter(QuestionMaster.is_active == True)

    questions = query.order_by(QuestionMaster.question_order).all()

    result = []
    for question in questions:
        if language == "en":
            # Return English from master table
            result.append({
                "question_key": question.question_key,
                "question_text": question.question_text,
                "question_order": question.question_order,
                "type": question.type,
                "language": "en",
                "variant": None
            })
        else:
            # Look for translation
            translation = db.query(QuestionTranslation).filter(
                QuestionTranslation.question_key == question.question_key,
                QuestionTranslation.language == language
            ).first()

            if translation:
                result.append({
                    "question_key": question.question_key,
                    "question_text": translation.translated_text,
                    "question_order": question.question_order,
                    "type": question.type,
                    "language": language,
                    "variant": translation.variant
                })
            else:
                # Fallback to English if translation not found
                result.append({
                    "question_key": question.question_key,
                    "question_text": question.question_text,
                    "question_order": question.question_order,
                    "type": question.type,
                    "language": "en",
                    "variant": None,
                    "note": f"Translation not available for {language}, showing English"
                })

    return result


@router.get("/languages/available")
async def get_available_languages(db: Session = Depends(get_db)):
    """Get all available languages"""
    languages = db.query(QuestionTranslation.language).distinct().all()

    # Always include English
    available_languages = ["en"]
    available_languages.extend([lang[0] for lang in languages if lang[0] != "en"])

    return {
        "success": True,
        "languages": list(set(available_languages))
    }


@router.post("/bulk-create")
async def create_default_questions(db: Session = Depends(get_db)):
    """Create default food ordering questions"""
    default_questions = [
        {
            "question_key": "dietary_preference",
            "question_text": "What is your dietary preference?",
            "question_order": 1,
            "type": "single_choice"
        },
        {
            "question_key": "cuisine_type",
            "question_text": "What cuisine are you craving?",
            "question_order": 2,
            "type": "single_choice"
        },
        {
            "question_key": "hunger_level",
            "question_text": "How hungry are you?",
            "question_order": 3,
            "type": "single_choice"
        },
        {
            "question_key": "spice_preference",
            "question_text": "What's your spice preference?",
            "question_order": 4,
            "type": "single_choice"
        },
        {
            "question_key": "budget_range",
            "question_text": "What's your budget range for this meal?",
            "question_order": 5,
            "type": "single_choice"
        }
    ]

    try:
        created_questions = []
        for q_data in default_questions:
            # Check if exists
            existing = db.query(QuestionMaster).filter(
                QuestionMaster.question_key == q_data["question_key"]
            ).first()

            if not existing:
                question = QuestionMaster(**q_data, is_active=True)
                db.add(question)
                created_questions.append(q_data["question_key"])

        db.commit()
        return {
            "success": True,
            "message": f"Created {len(created_questions)} default questions",
            "created_questions": created_questions
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create default questions: {str(e)}")


@router.post("/translations/bulk-add")
async def bulk_add_translations(
    translations: List[TranslationCreate],
    db: Session = Depends(get_db)
):
    """Bulk add translations"""
    try:
        added_translations = []
        skipped_translations = []

        for translation_data in translations:
            # Check if question exists
            question_exists = db.query(QuestionMaster).filter(
                QuestionMaster.question_key == translation_data.question_key
            ).first()

            if not question_exists:
                skipped_translations.append({
                    "question_key": translation_data.question_key,
                    "language": translation_data.language,
                    "reason": "Question not found"
                })
                continue

            # Check if translation already exists
            existing = db.query(QuestionTranslation).filter(
                QuestionTranslation.question_key == translation_data.question_key,
                QuestionTranslation.language == translation_data.language
            ).first()

            if existing:
                skipped_translations.append({
                    "question_key": translation_data.question_key,
                    "language": translation_data.language,
                    "reason": "Translation already exists"
                })
                continue

            # Add translation
            translation = QuestionTranslation(
                question_key=translation_data.question_key,
                language=translation_data.language,
                translated_text=translation_data.translated_text,
                variant=translation_data.variant
            )

            db.add(translation)
            added_translations.append({
                "question_key": translation_data.question_key,
                "language": translation_data.language
            })

        db.commit()
        return {
            "success": True,
            "message": f"Added {len(added_translations)} translations, skipped {len(skipped_translations)}",
            "added": added_translations,
            "skipped": skipped_translations
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to bulk add translations: {str(e)}")


@router.get("/by-type/{question_type}", response_model=List[QuestionResponse])
async def get_questions_by_type(
    question_type: str,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get questions by type"""
    query = db.query(QuestionMaster).filter(QuestionMaster.type == question_type)

    if active_only:
        query = query.filter(QuestionMaster.is_active == True)

    questions = query.order_by(QuestionMaster.question_order).all()

    return [
        QuestionResponse(
            id=q.id,
            question_key=q.question_key,
            question_text=q.question_text,
            question_order=q.question_order,
            type=q.type,
            is_active=q.is_active,
            created_at=q.created_at.isoformat(),
            updated_at=q.updated_at.isoformat() if q.updated_at else None
        ) for q in questions
    ]


@router.get("/types/list")
async def get_question_types(db: Session = Depends(get_db)):
    """Get all unique question types"""
    types = db.query(QuestionMaster.type).filter(
        QuestionMaster.type.isnot(None),
        QuestionMaster.is_active == True
    ).distinct().all()

    return {
        "success": True,
        "types": [t[0] for t in types if t[0] is not None]
    }
