from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class Seller(BaseModel):
    __tablename__ = "sellers_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(30), nullable=False)
    last_name: Mapped[str] = mapped_column(String(90), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    books: Mapped[List["Book"]] = relationship("Book", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Seller(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}', email='{self.email}')>"
