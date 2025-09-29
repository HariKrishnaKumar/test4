"""
Custom exception handlers for consistent error responses
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from utils.response_formatter import error_response, validation_error_response, server_error_response
import logging

logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent response format"""
    return error_response(
        message=exc.detail,
        data={"status_code": exc.status_code, "path": str(request.url)},
        status_code=exc.status_code
    )

async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle Starlette HTTP exceptions with consistent response format"""
    return error_response(
        message=exc.detail,
        data={"status_code": exc.status_code, "path": str(request.url)},
        status_code=exc.status_code
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation exceptions with consistent response format"""
    return validation_error_response(
        message="Validation error",
        data={
            "errors": exc.errors(),
            "body": exc.body,
            "path": str(request.url)
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with consistent response format"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return server_error_response(
        message="An unexpected error occurred",
        data={
            "error_type": type(exc).__name__,
            "path": str(request.url)
        }
    )

