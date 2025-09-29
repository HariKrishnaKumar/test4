from fastapi import APIRouter
from services.openai_service import get_emoji_response
from utils.response_formatter import success_response, error_response

router = APIRouter()

@router.get("/emoji-pizzas")
def get_emoji_pizzas():
    try:
        result = get_emoji_response("List 3 types of pizza with emojis.")
        return success_response(
            message="Emoji pizzas generated successfully",
            data={"response": result}
        )
    except Exception as e:
        return error_response(
            message="Failed to generate emoji pizzas",
            data={"error": str(e)}
        )

@router.get("/ai-suggest")
def suggest_pizza():
    try:
        result = get_emoji_response("Suggest a creative pizza combination with emojis.")
        return success_response(
            message="Pizza suggestion generated successfully",
            data={"response": result}
        )
    except Exception as e:
        return error_response(
            message="Failed to generate pizza suggestion",
            data={"error": str(e)}
        )
