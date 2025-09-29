from fastapi import APIRouter
from utils.response_formatter import success_response, created_response

router = APIRouter()

@router.get("/users")
def get_users():
    users = ["John", "Jane", "Bob"]
    return success_response(
        message="Users retrieved successfully",
        data={"users": users}
    )

@router.post("/users")
def create_user(name: str, email: str):
    user = {"name": name, "email": email, "id": 4}
    return created_response(
        message=f"User {name} created successfully",
        data=user
    )
