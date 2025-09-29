"""
Response Middleware for automatic response formatting
"""
from typing import Callable, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class ResponseFormatMiddleware(BaseHTTPMiddleware):
    """
    Middleware that automatically formats responses to follow the standard format
    """

    def __init__(self, app, exclude_paths: list = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico"
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and format the response
        """
        # Skip formatting for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        try:
            # Process the request
            response = await call_next(request)

            # Only format JSON responses that aren't already formatted
            if (isinstance(response, JSONResponse) and
                response.status_code < 500 and
                not self._is_already_formatted(response)):

                # Format the response
                formatted_response = self._format_response(response)
                return formatted_response

            return response

        except Exception as e:
            logger.error(f"Error in response middleware: {str(e)}")
            # Return a formatted error response
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Internal server error",
                    "data": None
                },
                status_code=500
            )

    def _is_already_formatted(self, response: JSONResponse) -> bool:
        """
        Check if the response is already in the standard format
        """
        try:
            content = response.body.decode('utf-8')
            import json
            data = json.loads(content)

            # Check if it has the standard format
            return (
                isinstance(data, dict) and
                "success" in data and
                "message" in data and
                "data" in data
            )
        except:
            return False

    def _format_response(self, response: JSONResponse) -> JSONResponse:
        """
        Format the response to follow the standard format
        """
        try:
            import json
            content = response.body.decode('utf-8')
            data = json.loads(content)

            # Determine success based on status code
            success = 200 <= response.status_code < 400

            # Create standard format
            formatted_data = {
                "success": success,
                "message": self._get_message(data, success, response.status_code),
                "data": data if not self._is_already_formatted(response) else data.get("data", data)
            }

            return JSONResponse(
                content=formatted_data,
                status_code=response.status_code,
                headers=dict(response.headers)
            )

        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}")
            # Return original response if formatting fails
            return response

    def _get_message(self, data: Any, success: bool, status_code: int) -> str:
        """
        Extract or generate an appropriate message
        """
        # If data is a dict and has a message field, use it
        if isinstance(data, dict) and "message" in data:
            return data["message"]

        # Generate default messages based on status code
        if success:
            if status_code == 200:
                return "Operation completed successfully"
            elif status_code == 201:
                return "Resource created successfully"
            elif status_code == 204:
                return "Operation completed successfully"
        else:
            if status_code == 400:
                return "Bad request"
            elif status_code == 401:
                return "Unauthorized"
            elif status_code == 403:
                return "Forbidden"
            elif status_code == 404:
                return "Resource not found"
            elif status_code == 422:
                return "Validation error"
            else:
                return "An error occurred"

        return "Operation completed" if success else "An error occurred"

