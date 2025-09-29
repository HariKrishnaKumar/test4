from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from database.database import get_db
from app.schemas.conversation import (
    VoiceAnswerRequest,
    QuestionResponse
)
from services.conversation_service import ConversationService
from helpers.validators import get_question_with_answers

router = APIRouter()

@router.post("/answer", response_model=Dict[str, Any])
async def submit_voice_answer(
    request: VoiceAnswerRequest,
    db: Session = Depends(get_db)
):
    """
    Submit an answer using voice mode
    The voice_text should be the transcribed text from user's voice input
    """
    try:
        result = ConversationService.process_voice_answer(
            db=db,
            session_id=request.session_id,
            user_id=request.user_id,
            question_key=request.question_key,
            voice_text=request.voice_text,
            response_text=request.voice_text  # Use voice_text as response_text for voice answers
        )

        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("/question/{question_key}", response_model=QuestionResponse)
async def get_question_for_voice(
    question_key: str,
    db: Session = Depends(get_db)
):
    """
    Get question details with available answers for voice mode
    This helps in voice matching and UI display
    """
    question = get_question_with_answers(db, question_key)

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question not found: {question_key}"
        )

    return QuestionResponse.from_orm(question)

@router.post("/match-answer")
async def match_voice_to_answer(
    question_key: str,
    voice_text: str,
    db: Session = Depends(get_db)
):
    """
    Test endpoint to check voice matching without creating entry
    Useful for debugging and testing voice recognition
    """
    from helpers.voice_matcher import match_voice_to_answer

    matched_answer_key = match_voice_to_answer(
        db=db,
        voice_text=voice_text,
        question_key=question_key
    )

    if matched_answer_key:
        # Get the matched answer details
        from models.conversation import AnswerMaster
        answer = db.query(AnswerMaster).filter(
            AnswerMaster.answer_key == matched_answer_key
        ).first()

        return {
            "matched": True,
            "answer_key": matched_answer_key,
            "answer_text": answer.answer_text if answer else None,
            "voice_text": voice_text
        }

    return {
        "matched": False,
        "answer_key": None,
        "voice_text": voice_text,
        "message": "Could not match voice input to any answer"
    }

@router.get("/next-question")
async def get_next_question_voice(
    session_id: str,
    current_question_key: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get the next question in the wizard flow for voice mode
    """
    next_question = ConversationService.get_next_question(
        db=db,
        session_id=session_id,
        current_question_key=current_question_key
    )

    if not next_question:
        return {
            "message": "No more questions",
            "completed": True
        }

    return QuestionResponse.from_orm(next_question)
