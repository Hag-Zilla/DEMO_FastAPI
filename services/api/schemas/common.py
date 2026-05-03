"""Common/shared Pydantic schemas."""

from typing import Generic, Sequence, TypeVar

from pydantic import BaseModel, Field

from services.api.auth.schemas import Token, TokenData  # noqa: F401

SchemaT = TypeVar("SchemaT")


class ListResponse(BaseModel, Generic[SchemaT]):
    """Standard list payload wrapper used across collection endpoints.

    Uses Sequence (covariant) instead of list to allow passing subclass
    instances (e.g., list[UserResponse] where UserResponse extends User).
    """

    data: Sequence[SchemaT] = Field(default_factory=list)
    count: int = Field(0, ge=0)


__all__ = ["Token", "TokenData", "ListResponse"]
