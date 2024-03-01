from fastapi import status, Depends
from fastapi import APIRouter

from src.schemas import IncomingBook, ReturnedAllBooks, ReturnedBook, UserOut
from src.schemas.books import UpdatedBook
from src.service.books import BookService
from src.utils.auth import get_current_user
from src.utils.db_session import DBSession

books_router = APIRouter(tags=["books"], prefix="/books")


# Ручка для создания записи о книге в БД. Возвращает созданную книгу.
# @books_router.post("/", response_model=ReturnedBook, status_code=status.HTTP_201_CREATED)  # Прописываем модель ответа
# async def create_book(
#         book: IncomingBook, session: DBSession
# ):  # прописываем модель валидирующую входные данные и сессию как зависимость.
#     # это - бизнес логика. Обрабатываем данные, сохраняем, преобразуем и т.д.
#
#     return await BookService.create_book(book, session)


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


# Ручка для обновления данных о книге
# @books_router.put("/{book_id}")
# async def update_book(book_id: int, new_data: UpdatedBook, session: DBSession):
#     return await BookService.update_book(book_id, new_data, session)

# -------------------------------------------------------------

@books_router.post("/", response_model=ReturnedBook, status_code=status.HTTP_201_CREATED)
async def create_book(book: IncomingBook, session: DBSession, current_user: UserOut = Depends(get_current_user)):
    return await BookService.create_book(book, session)


@books_router.put("/{book_id}")
async def update_book(book_id: int, new_data: UpdatedBook, session: DBSession,
                      current_user: UserOut = Depends(get_current_user)):
    return await BookService.update_book(book_id, new_data, session)
