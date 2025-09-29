from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from database.database import get_db
from app.schemas.conversation import (
    SelectAnswerRequest,
    ConversationEntryResponse,
    QuestionResponse
)
from services.conversation_service import ConversationService
from helpers.validators import get_question_with_answers

router = APIRouter()

@router.post("/answer", response_model=ConversationEntryResponse)
async def submit_select_answer(
    request: SelectAnswerRequest,
    db: Session = Depends(get_db)
):
    """
    Submit an answer using select mode
    """

    try:
        result = ConversationService.process_select_answer(
            db=db,
            session_id=request.session_id,
            user_id=request.user_id,
            question_key=request.question_key,
            answer_key=request.answer_key,
            response_text=request.responseText
        )

        # Add language information to the response
        user_language = ConversationService.get_user_language(db, request.session_id)

        # Convert result to dict if it's a Pydantic model
        if hasattr(result, 'dict'):
            result_dict = result.dict()
        else:
            result_dict = result

        result_dict["user_language"] = user_language

        return result_dict
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
async def get_question_details(
    question_key: str,
    db: Session = Depends(get_db)
):
    """
    Get question details with available answers for select mode
    """
    question = get_question_with_answers(db, question_key)

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question not found: {question_key}"
        )

    return QuestionResponse.from_orm(question)

@router.get("/next-question")
async def get_next_question(
    session_id: str,
    current_question_key: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get the next question in the wizard flow
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
