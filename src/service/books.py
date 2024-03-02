from fastapi import Response, status
from sqlalchemy import select

from src.models.books import Book
from src.models.sellers import Seller
from src.schemas import IncomingBook
from src.schemas.books import ReturnedAllBooks, ReturnedBook, UpdatedBook
from src.utils.db_session import DBSession


class BookService:
    @staticmethod
    async def create_book(book: IncomingBook, session: DBSession) -> ReturnedBook | Response:
        seller = await session.get(Seller, book.seller_id)
        if not seller:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        new_book = Book(
            title=book.title, author=book.author, year=book.year, count_pages=book.count_pages, seller_id=book.seller_id
        )
        session.add(new_book)
        await session.flush()

        return ReturnedBook.from_orm(new_book)

    @staticmethod
    async def get_all_books(session: DBSession) -> ReturnedAllBooks | Response:
        query = select(Book)
        res = await session.execute(query)
        books = res.scalars().all()
        if books:
            books_response = [ReturnedBook.from_orm(book) for book in books]
            return ReturnedAllBooks(books=books_response)
        else:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

    @staticmethod
    async def get_book(book_id: int, session: DBSession) -> ReturnedBook | Response:
        res = await session.get(Book, book_id)
        if res:
            return ReturnedBook.from_orm(res)
        else:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

    @staticmethod
    async def delete_book(book_id: int, session: DBSession) -> Response:
        deleted_book = await session.get(Book, book_id)
        if deleted_book:
            await session.delete(deleted_book)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

    @staticmethod
    async def update_book(book_id: int, new_data: UpdatedBook, session: DBSession) -> ReturnedBook | Response:
        updated_book = await session.get(Book, book_id)
        if updated_book:
            # Итерация по полям модели UpdatedBook и обновление соответствующих атрибутов в updated_book
            for field, value in new_data.dict(exclude_unset=True).items():
                setattr(updated_book, field, value)

            await session.flush()
            return ReturnedBook.from_orm(updated_book)

        return Response(status_code=status.HTTP_404_NOT_FOUND)
