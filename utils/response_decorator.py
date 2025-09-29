"""
Response Decorator for automatic response formatting
"""
from functools import wraps
from typing import Any, Callable, Optional, Union
from fastapi import HTTPException
from .response_formatter import ResponseFormatter
import logging

logger = logging.getLogger(__name__)

def format_response(
    success_message: str = "Operation completed successfully",
    error_message: str = "An error occurred",
    success_status_code: int = 200,
    error_status_code: int = 400
):
    """
    Decorator to automatically format endpoint responses

    Args:
        success_message: Default success message
        error_message: Default error message
        success_status_code: Default success status code
        error_status_code: Default error status code
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                return ResponseFormatter.success(
                    message=success_message,
                    data=result,
                    status_code=success_status_code
                )
            except HTTPException as e:
                return ResponseFormatter.error(
                    message=e.detail,
                    data=None,
                    status_code=e.status_code
                )
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                return ResponseFormatter.error(
                    message=error_message,
                    data={"error": str(e)},
                    status_code=error_status_code
                )

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return ResponseFormatter.success(
                    message=success_message,
                    data=result,
                    status_code=success_status_code
                )
            except HTTPException as e:
                return ResponseFormatter.error(
                    message=e.detail,
                    data=None,
                    status_code=e.status_code
                )
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                return ResponseFormatter.error(
                    message=error_message,
                    data={"error": str(e)},
                    status_code=error_status_code
                )

        # Return appropriate wrapper based on whether function is async
        if func.__code__.co_flags & 0x80:  # Check if function is async
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

def success_response(message: str = "Operation completed successfully", status_code: int = 200):
    """Decorator for success responses"""
    return format_response(
        success_message=message,
        success_status_code=status_code
    )

def created_response(message: str = "Resource created successfully"):
    """Decorator for created responses"""
    return format_response(
        success_message=message,
        success_status_code=201
    )

def updated_response(message: str = "Resource updated successfully"):
    """Decorator for updated responses"""
    return format_response(
        success_message=message,
        success_status_code=200
    )

def deleted_response(message: str = "Resource deleted successfully"):
    """Decorator for deleted responses"""
    return format_response(
        success_message=message,
        success_status_code=200
    )

def list_response(message: str = "Data retrieved successfully"):
    """Decorator for list responses"""
    return format_response(
        success_message=message,
        success_status_code=200
    )

def detail_response(message: str = "Data retrieved successfully"):
    """Decorator for detail responses"""
    return format_response(
        success_message=message,
        success_status_code=200
    )

