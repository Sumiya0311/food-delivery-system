from typing import Any


def success_response(
    message: str,
    data: Any = None,
) -> dict:
    """Create a standard success response."""
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(message: str) -> dict:
    """Create a standard error response."""
    return {
        "success": False,
        "message": message,
        "data": None,
    }