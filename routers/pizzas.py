from fastapi import APIRouter, HTTPException
from utils.response_formatter import success_response, not_found_response, created_response

router = APIRouter()

@router.get("/pizzas")
def get_pizzas():
    pizzas = [
        {"id": 1, "name": "Margherita", "price": 299},
        {"id": 2, "name": "Farmhouse", "price": 399},
        {"id": 3, "name": "Peppy Paneer", "price": 349}
    ]
    return success_response(
        message="Pizzas retrieved successfully",
        data={"pizzas": pizzas}
    )

@router.get("/pizzas/{pizza_id}")
def get_pizza(pizza_id: int):
    pizzas = [
        {"id": 1, "name": "Margherita", "price": 299},
        {"id": 2, "name": "Farmhouse", "price": 399},
        {"id": 3, "name": "Peppy Paneer", "price": 349}
    ]

    pizza = next((p for p in pizzas if p["id"] == pizza_id), None)
    if not pizza:
        return not_found_response(
            message=f"Pizza with ID {pizza_id} not found",
            data={"pizza_id": pizza_id}
        )

    return success_response(
        message="Pizza retrieved successfully",
        data=pizza
    )

@router.post("/pizzas")
def create_pizza(name: str, price: int):
    pizza = {"id": 4, "name": name, "price": price}
    return created_response(
        message=f"Pizza {name} created successfully",
        data=pizza
    )
