"""
Custom Response Classes for automatic formatting
"""
from typing import Any, Dict, Optional, Union
from fastapi.responses import JSONResponse
from .response_formatter import ResponseFormatter

class StandardJSONResponse(JSONResponse):
    """Custom JSONResponse that automatically formats responses"""

    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        success: bool = True,
        message: str = "Operation completed successfully",
        data: Optional[Union[Dict[str, Any], list, Any]] = None,
        **kwargs
    ):
        """
        Initialize a standardized JSON response

        Args:
            content: Raw content (will be ignored if data is provided)
            status_code: HTTP status code
            success: Whether the operation was successful
            message: Response message
            data: Response data
            **kwargs: Additional arguments for JSONResponse
        """
        # If content is provided but data is not, treat content as data
        if data is None and content is not None:
            data = content

        # Format the response according to our standard
        formatted_content = {
            "success": success,
            "message": message,
            "data": data
        }

        super().__init__(
            content=formatted_content,
            status_code=status_code,
            **kwargs
        )

class SuccessResponse(StandardJSONResponse):
    """Response class for successful operations"""

    def __init__(
        self,
        message: str = "Operation completed successfully",
        data: Optional[Union[Dict[str, Any], list, Any]] = None,
        status_code: int = 200,
        **kwargs
    ):
        super().__init__(
            success=True,
            message=message,
            data=data,
            status_code=status_code,
            **kwargs
        )

class ErrorResponse(StandardJSONResponse):
    """Response class for error operations"""

    def __init__(
        self,
        message: str = "An error occurred",
        data: Optional[Union[Dict[str, Any], list, Any]] = None,
        status_code: int = 400,
        **kwargs
    ):
        super().__init__(
            success=False,
            message=message,
            data=data,
            status_code=status_code,
            **kwargs
        )

class CreatedResponse(SuccessResponse):
    """Response class for created resources"""

    def __init__(
        self,
        message: str = "Resource created successfully",
        data: Optional[Union[Dict[str, Any], list, Any]] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            data=data,
            status_code=201,
            **kwargs
        )

class UpdatedResponse(SuccessResponse):
    """Response class for updated resources"""

    def __init__(
        self,
        message: str = "Resource updated successfully",
        data: Optional[Union[Dict[str, Any], list, Any]] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            data=data,
            status_code=200,
            **kwargs
        )

class DeletedResponse(SuccessResponse):
    """Response class for deleted resources"""

    def __init__(
        self,
        message: str = "Resource deleted successfully",
        data: Optional[Union[Dict[str, Any], list, Any]] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            data=data,
            status_code=200,
            **kwargs
        )

class NotFoundResponse(ErrorResponse):
    """Response class for not found errors"""

    def __init__(
        self,
        message: str = "Resource not found",
        data: Optional[Union[Dict[str, Any], list, Any]] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            data=data,
            status_code=404,
            **kwargs
        )

class UnauthorizedResponse(ErrorResponse):
    """Response class for unauthorized errors"""

    def __init__(
        self,
        message: str = "Unauthorized access",
        data: Optional[Union[Dict[str, Any], list, Any]] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            data=data,
            status_code=401,
            **kwargs
        )

class ForbiddenResponse(ErrorResponse):
    """Response class for forbidden errors"""

    def __init__(
        self,
        message: str = "Access forbidden",
        data: Optional[Union[Dict[str, Any], list, Any]] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            data=data,
            status_code=403,
            **kwargs
        )

class ValidationErrorResponse(ErrorResponse):
    """Response class for validation errors"""

    def __init__(
        self,
        message: str = "Validation error",
        data: Optional[Union[Dict[str, Any], list, Any]] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            data=data,
            status_code=422,
            **kwargs
        )

class ServerErrorResponse(ErrorResponse):
    """Response class for server errors"""

    def __init__(
        self,
        message: str = "Internal server error",
        data: Optional[Union[Dict[str, Any], list, Any]] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            data=data,
            status_code=500,
            **kwargs
        )

