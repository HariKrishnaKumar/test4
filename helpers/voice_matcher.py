from sqlalchemy.orm import Session
from typing import Optional, List
from difflib import SequenceMatcher
from models.conversation import AnswerMaster

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts"""
    text1 = text1.lower().strip()
    text2 = text2.lower().strip()
    return SequenceMatcher(None, text1, text2).ratio()

def match_voice_to_answer(
    db: Session,
    voice_text: str,
    question_key: str,
    threshold: float = 0.6
) -> Optional[str]:
    """
    Match voice text to the most appropriate answer
    Returns answer_key if match found, None otherwise
    """
    # Get all active answers for the question
    answers = db.query(AnswerMaster).filter(
        AnswerMaster.question_key == question_key,
        AnswerMaster.is_active == True
    ).all()

    if not answers:
        return None

    best_match = None
    best_score = 0.0

    for answer in answers:
        # Check against answer text
        score = calculate_similarity(voice_text, answer.answer_text)

        # Also check for common variations
        variations = get_common_variations(answer.answer_text)
        for variation in variations:
            variation_score = calculate_similarity(voice_text, variation)
            score = max(score, variation_score)

        if score > best_score and score >= threshold:
            best_score = score
            best_match = answer.answer_key

    return best_match

def get_common_variations(answer_text: str) -> List[str]:
    """
    Get common variations of answer text
    For example: "Vegetarian" -> ["veg", "veggie", "vegetarian"]
    """
    variations = []
    answer_lower = answer_text.lower()

    # Add common food preference variations
    variation_map = {
        "vegetarian": ["veg", "veggie", "vegetarian", "pure veg"],
        "non-vegetarian": ["non veg", "non-veg", "nonveg", "meat"],
        "vegan": ["vegan", "plant based", "no dairy"],
        "chinese": ["chinese", "chinese food", "indo chinese"],
        "italian": ["italian", "pasta", "pizza"],
        "mexican": ["mexican", "tex mex", "tacos"],
        "japanese": ["japanese", "sushi", "ramen"],
        "hungry": ["hungry", "very hungry", "starving"],
        "just snacking": ["snacking", "snack", "light bite"],
        "super hungry": ["super hungry", "very hungry", "famished", "starving"]
    }

    for key, values in variation_map.items():
        if key in answer_lower:
            variations.extend(values)

    return variations
