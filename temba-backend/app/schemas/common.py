"""Shared response wrappers and pagination helpers."""
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int


class PaginationParams(BaseModel):
    page: int = 1
    size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size
