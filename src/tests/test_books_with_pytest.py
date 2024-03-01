import pytest
import pytest_asyncio
from fastapi import status
from sqlalchemy import select

from src.models import books, sellers
from src.utils.auth import authenticate_user, get_password_hash

result = {
    "books": [
        {"author": "fdhgdh", "title": "jdhdj", "year": 1997},
        {"author": "fdhgdfgfrh", "title": "jrrgdhdj", "year": 2001},
    ]
}


@pytest_asyncio.fixture()
async def seller_id(db_session):
    seller = sellers.Seller(first_name="Seller", last_name="Seller", email="seller@seller.seller", password="seller")
    db_session.add(seller)
    await db_session.flush()
    yield seller.id


# Тест на ручку создающую книгу
@pytest.mark.asyncio
async def test_create_book(async_client, db_session):
    # Подготовка: создание и аутентификация пользователя
    user = sellers.Seller(first_name="Seller", last_name="User", email="seller_user@example.com",
                          password=get_password_hash("secure_password"))
    db_session.add(user)
    await db_session.flush()
    seller_id = user.id

    access_token = await authenticate_user(async_client, "seller_user@example.com", "secure_password")

    # Данные для создания книги
    data = {"title": "Wrong Code", "author": "Robert Martin", "pages": 104, "year": 2007, "seller_id": seller_id}

    # Выполнение запроса с использованием токена аутентификации
    response = await async_client.post("/api/v1/books/", headers={"Authorization": f"Bearer {access_token}"}, json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    # Проверка, что данные в ответе соответствуют отправленным данным
    assert result_data["title"] == data["title"]
    assert result_data["author"] == data["author"]
    assert result_data["count_pages"] == data["pages"]
    assert result_data["year"] == data["year"]
    assert result_data["seller_id"] == seller_id


# Тест на ручку получения списка книг
@pytest.mark.asyncio
async def test_get_books(db_session, async_client, seller_id):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller_id)
    book_2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller_id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/books/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["books"]) == 2  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "books": [
            {
                "title": "Eugeny Onegin",
                "author": "Pushkin",
                "year": 2001,
                "id": book.id,
                "count_pages": 104,
                "seller_id": seller_id,
            },
            {
                "title": "Mziri",
                "author": "Lermontov",
                "year": 1997,
                "id": book_2.id,
                "count_pages": 104,
                "seller_id": seller_id,
            },
        ]
    }


# Тест на ручку получения одной книги
@pytest.mark.asyncio
async def test_get_single_book(db_session, async_client, seller_id):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller_id)
    book_2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller_id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "title": "Eugeny Onegin",
        "author": "Pushkin",
        "year": 2001,
        "count_pages": 104,
        "id": book.id,
        "seller_id": seller_id,
    }


# Тест на ручку удаления книги
@pytest.mark.asyncio
async def test_delete_book(db_session, async_client, seller_id):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller_id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_books = await db_session.execute(select(books.Book))
    res = all_books.scalars().all()
    assert len(res) == 0


# Тест на ручку обновления книги
@pytest.mark.asyncio
async def test_update_book(db_session, async_client):
    # Создание пользователя и его аутентификация для получения токена
    user = sellers.Seller(first_name="Seller", last_name="User",
                          email="update_book_user@example.com", password=get_password_hash("secure_password"))
    db_session.add(user)
    await db_session.flush()
    seller_id = user.id

    access_token = await authenticate_user(async_client, "update_book_user@example.com", "secure_password")

    # Создание книги вручную
    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller_id)
    db_session.add(book)
    await db_session.flush()

    # Выполнение запроса на обновление книги с использованием токена аутентификации
    response = await async_client.put(
        f"/api/v1/books/{book.id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"title": "Mziri", "author": "Lermontov", "count_pages": 100, "year": 2007},
    )

    assert response.status_code == status.HTTP_200_OK

    # Проверка обновления данных книги
    res = await db_session.get(books.Book, book.id)
    assert res.title == "Mziri"
    assert res.author == "Lermontov"
    assert res.count_pages == 100
    assert res.year == 2007
    assert res.id == book.id

