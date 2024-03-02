from src.models import books
from src.models.books import Book
from src.tests.models import BookExample


async def add_book_for_seller(db_session, sellerID) -> Book:
    book = books.Book(**BookExample(seller_id=sellerID).to_dict())
    db_session.add(book)
    await db_session.flush()
    return book


async def add_2_books_for_seller(db_session, sellerID) -> (Book, Book):
    book_1 = books.Book(**BookExample(seller_id=sellerID).to_dict())
    book_2 = books.Book(**BookExample(seller_id=sellerID).to_dict())
    db_session.add_all([book_1, book_2])
    await db_session.flush()
    return book_1, book_2
