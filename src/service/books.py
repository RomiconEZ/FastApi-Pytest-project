from fastapi import Response, status
from sqlalchemy import select

from src.models.books import Book
from src.models.sellers import Seller
from src.schemas import IncomingBook
from src.schemas.books import UpdatedBook
from src.utils.db_session import DBSession

class BookService:
    @staticmethod
    async def create_book(book: IncomingBook, session: DBSession):
        seller = await session.get(Seller, book.seller_id)
        if not seller:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        new_book = Book(
            title=book.title, author=book.author, year=book.year, count_pages=book.count_pages, seller_id=book.seller_id
        )
        session.add(new_book)
        await session.flush()

        return new_book

    @staticmethod
    async def get_all_books(session: DBSession):
        query = select(Book)
        res = await session.execute(query)
        books = res.scalars().all()
        return {"books": books}

    @staticmethod
    async def get_book(book_id: int, session: DBSession):
        res = await session.get(Book, book_id)
        return res

    @staticmethod
    async def delete_book(book_id: int, session: DBSession):
        deleted_book = await session.get(Book, book_id)
        if deleted_book:
            await session.delete(deleted_book)

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @staticmethod
    async def update_book(book_id: int, new_data: UpdatedBook, session: DBSession):
        if updated_book := await session.get(Book, book_id):
            updated_book.author = new_data.author
            updated_book.title = new_data.title
            updated_book.year = new_data.year
            updated_book.count_pages = new_data.count_pages

            await session.flush()

            return updated_book

        return Response(status_code=status.HTTP_404_NOT_FOUND)
