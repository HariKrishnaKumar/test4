from fastapi import APIRouter
from app.routes import select_routes, voice_routes, language_routes, service_routes

api_router = APIRouter()

# Include route modules
api_router.include_router(
    select_routes.router,
    prefix="/select",
    tags=["Select Mode"]
)

api_router.include_router(
    voice_routes.router,
    prefix="/voice",
    tags=["Voice Mode"]
)

api_router.include_router(
    language_routes.router,
    prefix="/language",
    tags=["Language Selection"]
)

api_router.include_router(
    service_routes.router,
    prefix="/service",
    tags=["Service Selection"]
)
