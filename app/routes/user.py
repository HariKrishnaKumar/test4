from fastapi import APIRouter
from utils.response_formatter import success_response

router = APIRouter()

@router.get("/users")
def get_users():
    return success_response(
        message="List of users retrieved successfully",
        data={"message": "List of users"}
    )
