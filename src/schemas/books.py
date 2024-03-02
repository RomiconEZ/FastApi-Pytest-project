from typing import List

from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

__all__ = ["IncomingBook", "ReturnedAllBooks", "ReturnedBook", "UpdatedBook", "ReturnedBookForSeller"]


# Базовый класс "Книги", содержащий поля, которые есть во всех классах-наследниках.
class BaseBook(BaseModel):
    title: str
    author: str
    year: int


class BookWithSeller(BaseModel):
    seller_id: int


class ValidationIncomingBook(BaseBook):
    year: int = 2024  # Пример присваивания дефолтного значения
    count_pages: int = Field(
        alias="pages",
        default=1,
    )  # Пример использования тонкой настройки полей. Передачи в них метаинформации.

    @field_validator("year")  # Валидатор, проверяет что дата не слишком древняя
    @staticmethod
    def validate_year(val: int):
        if val < 1400:
            raise PydanticCustomError("Validation error", "Year is wrong!")
        return val

    class Config:
        populate_by_name = True


# Класс для валидации входящих данных.
class IncomingBook(ValidationIncomingBook, BookWithSeller):
    pass


# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedBook(BaseBook, BookWithSeller):
    id: int
    count_pages: int = 0

    class Config:
        from_attributes = True


class UpdatedBook(ValidationIncomingBook):
    pass


# Класс для возврата массива объектов "Книга"
class ReturnedAllBooks(BaseModel):
    books: List[ReturnedBook]

    class Config:
        from_attributes = True


class ReturnedBookForSeller(ReturnedBook):
    seller_id: int = Field(exclude=True)

    class Config:
        from_attributes = True
