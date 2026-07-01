from typing import Any

from pydantic import BaseModel


class APIResponse(BaseModel):
    status: bool
    message: str
    data: Any | None = None


def success_response(message: str, data: Any = None) -> dict:
    """Build a consistent success response."""
    return APIResponse(status=True, message=message, data=data).model_dump()


def error_response(message: str, data: Any = None) -> dict:
    """Build a consistent error response."""
    return APIResponse(status=False, message=message, data=data).model_dump()
