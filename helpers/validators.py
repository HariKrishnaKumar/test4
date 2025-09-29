from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from models.conversation import QuestionMaster, AnswerMaster

def validate_question_key(db: Session, question_key: str) -> bool:
    """Validate if question key exists and is active"""
    question = db.query(QuestionMaster).filter(
        QuestionMaster.question_key == question_key,
        QuestionMaster.is_active == True
    ).first()
    return question is not None

def validate_answer_key(db: Session, answer_key: str, question_key: str) -> bool:
    """Validate if answer key exists for the given question"""
    answer = db.query(AnswerMaster).filter(
        AnswerMaster.answer_key == answer_key,
        AnswerMaster.question_key == question_key,
        AnswerMaster.is_active == True
    ).first()
    return answer is not None

def get_question_with_answers(db: Session, question_key: str) -> Optional[QuestionMaster]:
    """Get question with all its active answers"""
    return db.query(QuestionMaster).filter(
        QuestionMaster.question_key == question_key,
        QuestionMaster.is_active == True
    ).first()

def get_active_answers_for_question(db: Session, question_key: str) -> List[Dict[str, str]]:
    """Get all active answers for a question"""
    answers = db.query(AnswerMaster).filter(
        AnswerMaster.question_key == question_key,
        AnswerMaster.is_active == True
    ).all()

    return [
        {
            "answer_key": answer.answer_key,
            "answer_text": answer.answer_text
        }
        for answer in answers
    ]
