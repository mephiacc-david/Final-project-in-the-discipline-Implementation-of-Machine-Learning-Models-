from __future__ import annotations

from typing import Any

from pydantic import ValidationError


class ApiError(Exception):
    def __init__(
        self,
        *,
        error_code: str,
        message: str,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


def validation_error_to_message(error: ValidationError) -> str:
    first_error = error.errors(include_url=False)[0]
    location = ".".join(str(value) for value in first_error["loc"])
    return f"{location}: {first_error['msg']}"
