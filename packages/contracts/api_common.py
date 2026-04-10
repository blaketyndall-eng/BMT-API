from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str
    message: str
    retryable: bool = False
    details: dict[str, Any] = Field(default_factory=dict)


class ApiEnvelope(BaseModel):
    data: dict[str, Any]
    errors: list[ErrorDetail] = Field(default_factory=list)
