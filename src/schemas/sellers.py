from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from .books import ReturnedBookForSeller

__all__ = [
    "IncomingSeller",
    "ReturnedSeller",
    "ReturnedAllSellers",
    "BaseSeller",
    "ReturnedSellerWithBooks",
    "UpdatedSeller",
    "SellerOut",
]


class BaseSeller(BaseModel):
    first_name: str = Field(min_length=2)
    last_name: str = Field(min_length=2)
    email: EmailStr


class IncomingSeller(BaseSeller):
    password: str = Field(min_length=4)


class ReturnedSeller(BaseSeller):
    id: int

    class Config:
        from_attributes = True


class UpdatedSeller(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=2)
    last_name: Optional[str] = Field(default=None, min_length=2)
    email: Optional[EmailStr] = Field(default=None)

    class Config:
        from_attributes = True


class ReturnedAllSellers(BaseModel):
    sellers: List[ReturnedSeller]

    class Config:
        from_attributes = True


class ReturnedSellerWithBooks(ReturnedSeller):
    books: Optional[List[ReturnedBookForSeller]] = []

    class Config:
        from_attributes = True


class SellerOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True
