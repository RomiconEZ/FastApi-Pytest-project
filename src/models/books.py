from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class Book(BaseModel):
    __tablename__ = "books_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author: Mapped[str] = mapped_column(String(150), nullable=False)
    year: Mapped[int]
    count_pages: Mapped[int]
    seller_id: Mapped[int] = mapped_column(ForeignKey("sellers_table.id"))

    def __repr__(self):
        return (
            f"<Book(id={self.id}, title='{self.title}', author='{self.author}', "
            f"year={self.year}, count_pages={self.count_pages}, seller_id={self.seller_id})>"
        )
