from fastapi import APIRouter, Depends, status

from src.schemas import IncomingBook, ReturnedAllBooks, ReturnedBook, SellerOut
from src.schemas.books import UpdatedBook
from src.service.books import BookService
from src.utils.auth import check_seller_token
from src.utils.db_session import DBSession

books_router = APIRouter(tags=["books"], prefix="/books")


# ===================================================================
# ---------------------РУЧКИ БЕЗ АВТОРИЗАЦИИ-------------------------
# ===================================================================
# Ручка, возвращающая все книги
@books_router.get("/", response_model=ReturnedAllBooks)
async def get_all_books(session: DBSession):
    return await BookService.get_all_books(session)


# Ручка для получения книги по ее ИД
@books_router.get("/{book_id}", response_model=ReturnedBook)
async def get_book(book_id: int, session: DBSession):
    return await BookService.get_book(book_id, session)


# Ручка для удаления книги
@books_router.delete("/{book_id}")
async def delete_book(book_id: int, session: DBSession):
    return await BookService.delete_book(book_id, session)


# ===================================================================
# ---------------------РУЧКИ С АВТОРИЗАЦИЕЙ--------------------------
# ===================================================================


# Ручка для создания книги
@books_router.post("/", response_model=ReturnedBook, status_code=status.HTTP_201_CREATED)
async def create_book(book: IncomingBook, session: DBSession, current_user: SellerOut = Depends(check_seller_token)):
    return await BookService.create_book(book, session)


# Ручка для обновления книги
@books_router.put("/{book_id}")
async def update_book(
    book_id: int, new_data: UpdatedBook, session: DBSession, current_user: SellerOut = Depends(check_seller_token)
):
    return await BookService.update_book(book_id, new_data, session)
