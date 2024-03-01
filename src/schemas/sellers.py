from typing import List

from pydantic import BaseModel, EmailStr, Field

from .books import ReturnedBookForSeller

__all__ = [
    "IncomingSeller",
    "ReturnedSeller",
    "ReturnedAllSellers",
    "BaseSeller",
    "ReturnedSellerWithBooks",
    "UpdatedSeller",
    "UserOut"
]


class BaseSeller(BaseModel):
    first_name: str = Field(min_length=3)
    last_name: str = Field(min_length=3)
    email: EmailStr


class IncomingSeller(BaseSeller):
    password: str = Field(min_length=4)


class ReturnedSeller(BaseSeller):
    id: int


class UpdatedSeller(BaseSeller):
    pass


class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]


class ReturnedSellerWithBooks(ReturnedSeller):
    books: List[ReturnedBookForSeller]


class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True
