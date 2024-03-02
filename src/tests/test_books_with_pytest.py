import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books
from src.tests.constants import PREFIX, SELLER_1_EXAMPLE_PASSWORD
from src.tests.helpers import add_2_books_for_seller, add_book_for_seller
from src.tests.models import BookExample
from src.utils.auth import authenticate_user

from .fixtures import get_new_seller


# Тест на ручку создающую книгу
@pytest.mark.asyncio
async def test_create_book(async_client, db_session, get_new_seller):
    seller = get_new_seller

    access_token = await authenticate_user(async_client, seller.email, SELLER_1_EXAMPLE_PASSWORD)

    # Данные для создания книги
    book = BookExample(seller_id=seller.id).to_dict()

    # Выполнение запроса с использованием токена аутентификации
    response = await async_client.post(
        PREFIX + "books/", headers={"Authorization": f"Bearer {access_token}"}, json=book
    )

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    # Проверка, что данные в ответе соответствуют отправленным данным
    assert result_data["title"] == book["title"]
    assert result_data["author"] == book["author"]
    assert result_data["count_pages"] == book["count_pages"]
    assert result_data["year"] == book["year"]
    assert result_data["seller_id"] == seller.id


# Тест на ручку получения списка книг
@pytest.mark.asyncio
async def test_get_books(db_session, async_client, get_new_seller):
    seller = get_new_seller
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке

    book_1, book_2 = await add_2_books_for_seller(db_session=db_session, sellerID=seller.id)

    response = await async_client.get(PREFIX + "books/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["books"]) == 2  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "books": [
            {
                "title": book_1.title,
                "author": book_1.author,
                "year": book_1.year,
                "id": book_1.id,
                "count_pages": book_1.count_pages,
                "seller_id": seller.id,
            },
            {
                "title": book_2.title,
                "author": book_2.author,
                "year": book_2.year,
                "id": book_2.id,
                "count_pages": book_2.count_pages,
                "seller_id": seller.id,
            },
        ]
    }


# Тест на ручку получения одной книги
@pytest.mark.asyncio
async def test_get_single_book(db_session, async_client, get_new_seller):
    seller = get_new_seller

    book_1, book_2 = await add_2_books_for_seller(db_session=db_session, sellerID=seller.id)

    response = await async_client.get(PREFIX + f"books/{book_1.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "title": book_1.title,
        "author": book_1.author,
        "year": book_1.year,
        "id": book_1.id,
        "count_pages": book_1.count_pages,
        "seller_id": seller.id,
    }


# Тест на ручку удаления книги
@pytest.mark.asyncio
async def test_delete_book(db_session, async_client, get_new_seller):
    seller = get_new_seller

    book = await add_book_for_seller(db_session=db_session, sellerID=seller.id)

    response = await async_client.delete(PREFIX + f"books/{book.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_books = await db_session.execute(select(books.Book))
    res = all_books.scalars().all()
    assert len(res) == 0


# Тест на ручку обновления книги
@pytest.mark.asyncio
async def test_update_book(db_session, async_client, get_new_seller):
    # Создание пользователя и его аутентификация для получения токена
    seller = get_new_seller
    access_token = await authenticate_user(async_client, seller.email, SELLER_1_EXAMPLE_PASSWORD)

    # Создание книги вручную
    book = await add_book_for_seller(db_session=db_session, sellerID=seller.id)
    new_book_data = BookExample(seller_id=seller.id).gen_new_book_data()
    # Выполнение запроса на обновление книги с использованием токена аутентификации
    response = await async_client.put(
        f"/api/v1/books/{book.id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "title": new_book_data["title"],
            "author": new_book_data["author"],
            "count_pages": new_book_data["count_pages"],
            "year": new_book_data["year"],
        },
    )

    assert response.status_code == status.HTTP_200_OK

    # Проверка обновления данных книги
    res = await db_session.get(books.Book, book.id)
    assert res.title == new_book_data["title"]
    assert res.author == new_book_data["author"]
    assert res.count_pages == new_book_data["count_pages"]
    assert res.year == new_book_data["year"]
    assert res.id == book.id
