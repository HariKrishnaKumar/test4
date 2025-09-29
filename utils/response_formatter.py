"""
Global Response Formatter for consistent API responses
"""
from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class StandardResponse(BaseModel):
    """Standard response model for all API endpoints"""
    success: bool
    message: str
    data: Optional[Union[Dict[str, Any], List[Any], Any]] = None

class ResponseFormatter:
    """Global response formatter for consistent API responses"""

    @staticmethod
    def success(
        message: str = "Operation completed successfully",
        data: Optional[Union[Dict[str, Any], List[Any], Any]] = None,
        status_code: int = 200
    ) -> JSONResponse:
        """
        Create a successful response

        Args:
            message: Success message
            data: Response data (can be dict, list, or any serializable object)
            status_code: HTTP status code

        Returns:
            JSONResponse with standard format
        """
        response_data = {
            "success": True,
            "message": message,
            "data": data
        }

        return JSONResponse(
            content=response_data,
            status_code=status_code
        )

    @staticmethod
    def error(
        message: str = "An error occurred",
        data: Optional[Union[Dict[str, Any], List[Any], Any]] = None,
        status_code: int = 400
    ) -> JSONResponse:
        """
        Create an error response

        Args:
            message: Error message
            data: Additional error data
            status_code: HTTP status code

        Returns:
            JSONResponse with standard format
        """
        response_data = {
            "success": False,
            "message": message,
            "data": data
        }

        return JSONResponse(
            content=response_data,
            status_code=status_code
        )

    @staticmethod
    def created(
        message: str = "Resource created successfully",
        data: Optional[Union[Dict[str, Any], List[Any], Any]] = None
    ) -> JSONResponse:
        """
        Create a 201 Created response

        Args:
            message: Success message
            data: Created resource data

        Returns:
            JSONResponse with 201 status
        """
        return ResponseFormatter.success(
            message=message,
            data=data,
            status_code=201
        )

    @staticmethod
    def updated(
        message: str = "Resource updated successfully",
        data: Optional[Union[Dict[str, Any], List[Any], Any]] = None
    ) -> JSONResponse:
        """
        Create a 200 OK response for updates

        Args:
            message: Success message
            data: Updated resource data

        Returns:
            JSONResponse with 200 status
        """
        return ResponseFormatter.success(
            message=message,
            data=data,
            status_code=200
        )

    @staticmethod
    def deleted(
        message: str = "Resource deleted successfully",
        data: Optional[Union[Dict[str, Any], List[Any], Any]] = None
    ) -> JSONResponse:
        """
        Create a 200 OK response for deletions

        Args:
            message: Success message
            data: Deletion confirmation data

        Returns:
            JSONResponse with 200 status
        """
        return ResponseFormatter.success(
            message=message,
            data=data,
            status_code=200
        )

    @staticmethod
    def not_found(
        message: str = "Resource not found",
        data: Optional[Union[Dict[str, Any], List[Any], Any]] = None
    ) -> JSONResponse:
        """
        Create a 404 Not Found response

        Args:
            message: Error message
            data: Additional error data

        Returns:
            JSONResponse with 404 status
        """
        return ResponseFormatter.error(
            message=message,
            data=data,
            status_code=404
        )

    @staticmethod
    def unauthorized(
        message: str = "Unauthorized access",
        data: Optional[Union[Dict[str, Any], List[Any], Any]] = None
    ) -> JSONResponse:
        """
        Create a 401 Unauthorized response

        Args:
            message: Error message
            data: Additional error data

        Returns:
            JSONResponse with 401 status
        """
        return ResponseFormatter.error(
            message=message,
            data=data,
            status_code=401
        )

    @staticmethod
    def forbidden(
        message: str = "Access forbidden",
        data: Optional[Union[Dict[str, Any], List[Any], Any]] = None
    ) -> JSONResponse:
        """
        Create a 403 Forbidden response

        Args:
            message: Error message
            data: Additional error data

        Returns:
            JSONResponse with 403 status
        """
        return ResponseFormatter.error(
            message=message,
            data=data,
            status_code=403
        )

    @staticmethod
    def validation_error(
        message: str = "Validation error",
        data: Optional[Union[Dict[str, Any], List[Any], Any]] = None
    ) -> JSONResponse:
        """
        Create a 422 Validation Error response

        Args:
            message: Error message
            data: Validation error details

        Returns:
            JSONResponse with 422 status
        """
        return ResponseFormatter.error(
            message=message,
            data=data,
            status_code=422
        )

    @staticmethod
    def server_error(
        message: str = "Internal server error",
        data: Optional[Union[Dict[str, Any], List[Any], Any]] = None
    ) -> JSONResponse:
        """
        Create a 500 Internal Server Error response

        Args:
            message: Error message
            data: Additional error data

        Returns:
            JSONResponse with 500 status
        """
        return ResponseFormatter.error(
            message=message,
            data=data,
            status_code=500
        )

# Convenience functions for common operations
def success_response(message: str, data: Any = None, status_code: int = 200) -> JSONResponse:
    """Convenience function for success responses"""
    return ResponseFormatter.success(message, data, status_code)

def error_response(message: str, data: Any = None, status_code: int = 400) -> JSONResponse:
    """Convenience function for error responses"""
    return ResponseFormatter.error(message, data, status_code)

def created_response(message: str, data: Any = None) -> JSONResponse:
    """Convenience function for created responses"""
    return ResponseFormatter.created(message, data)

def updated_response(message: str, data: Any = None) -> JSONResponse:
    """Convenience function for updated responses"""
    return ResponseFormatter.updated(message, data)

def deleted_response(message: str, data: Any = None) -> JSONResponse:
    """Convenience function for deleted responses"""
    return ResponseFormatter.deleted(message, data)

def not_found_response(message: str, data: Any = None) -> JSONResponse:
    """Convenience function for not found responses"""
    return ResponseFormatter.not_found(message, data)

def unauthorized_response(message: str, data: Any = None) -> JSONResponse:
    """Convenience function for unauthorized responses"""
    return ResponseFormatter.unauthorized(message, data)

def forbidden_response(message: str, data: Any = None) -> JSONResponse:
    """Convenience function for forbidden responses"""
    return ResponseFormatter.forbidden(message, data)

def validation_error_response(message: str, data: Any = None) -> JSONResponse:
    """Convenience function for validation error responses"""
    return ResponseFormatter.validation_error(message, data)

def server_error_response(message: str, data: Any = None) -> JSONResponse:
    """Convenience function for server error responses"""
    return ResponseFormatter.server_error(message, data)

