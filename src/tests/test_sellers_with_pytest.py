import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books, sellers
from src.utils.auth import authenticate_user, get_password_hash


@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {"first_name": "Test_First_Name", "last_name": "Test_Last_Name",
            "email": "seller@example.com", "password": get_password_hash("hashed_password")}
    response = await async_client.post("/api/v1/seller/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data == {
        "id": 1,
        "first_name": "Test_First_Name",
        "last_name": "Test_Last_Name",
        "email": "seller@example.com",
    }


@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    seller_1 = sellers.Seller(first_name="Test_First_Name1", last_name="Test_Last_Name1",
                              email="seller1@example.com", password="hashed_password1")
    seller_2 = sellers.Seller(first_name="Test_First_Name2", last_name="Test_Last_Name2",
                              email="seller2@example.com", password="hashed_password2")

    db_session.add_all([seller_1, seller_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/seller/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["sellers"]) == 2

    assert response.json() == {
        "sellers": [
            {
                "first_name": seller_1.first_name,
                "last_name": seller_1.last_name,
                "email": seller_1.email,
                "id": seller_1.id,
            },
            {
                "first_name": seller_2.first_name,
                "last_name": seller_2.last_name,
                "email": seller_2.email,
                "id": seller_2.id,
            },
        ]
    }


@pytest.mark.asyncio
async def test_get_single_seller_without_books(db_session, async_client):
    # Подготовка: создание пользователя для аутентификации
    test_user = sellers.Seller(first_name="Auth_User", last_name="Auth_User_LastName",
                               email="auth_user@example.com", password=get_password_hash("hashed_password"))
    db_session.add(test_user)
    await db_session.flush()

    # Аутентификация пользователя для получения токена
    access_token = await authenticate_user(async_client, "auth_user@example.com","hashed_password")

    # Создание продавца для теста
    seller = sellers.Seller(first_name="Test_First_Name", last_name="Test_Last_Name",
                            email="seller@example.com", password="hashed_password")
    db_session.add(seller)
    await db_session.flush()

    # Выполнение запроса с токеном аутентификации
    response = await async_client.get(f"/api/v1/seller/{seller.id}",
                                      headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == status.HTTP_200_OK

    # Проверка интерфейса ответа
    assert response.json() == {
        "first_name": "Test_First_Name",
        "last_name": "Test_Last_Name",
        "email": "seller@example.com",
        "id": seller.id,
        "books": [],
    }



@pytest.mark.asyncio
async def test_get_single_seller_with_books(db_session, async_client):
    # Создание и аутентификация пользователя для получения токена доступа
    user = sellers.Seller(first_name="Auth", last_name="User",
                          email="auth@example.com", password=get_password_hash("hashed_password"))
    db_session.add(user)
    await db_session.flush()
    access_token = await authenticate_user(async_client, "auth@example.com", "hashed_password")

    # Создание продавца и книг для тестирования
    seller = sellers.Seller(first_name="Test_First_Name", last_name="Test_Last_Name",
                            email="seller@example.com", password="hashed_password")
    db_session.add(seller)
    await db_session.flush()

    book_1 = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)
    book_2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller.id)
    db_session.add_all([book_1, book_2])
    await db_session.flush()

    # Выполнение запроса с использованием токена аутентификации
    response = await async_client.get(f"/api/v1/seller/{seller.id}",
                                      headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == status.HTTP_200_OK

    # Проверка ожидаемого интерфейса ответа
    expected_books = [
        {
            "title": book_1.title,
            "author": book_1.author,
            "year": book_1.year,
            "id": book_1.id,
            "count_pages": book_1.count_pages,
        },
        {
            "title": book_2.title,
            "author": book_2.author,
            "year": book_2.year,
            "id": book_2.id,
            "count_pages": book_2.count_pages,
        },
    ]

    # Важно отметить, что порядок книг в ответе может отличаться,
    # поэтому для проверки списка книг используйте сравнение независимое от порядка элементов,
    # если порядок книг в вашем API не гарантирован.
    assert response.json() == {
        "first_name": "Test_First_Name",
        "last_name": "Test_Last_Name",
        "email": "seller@example.com",
        "id": seller.id,
        "books": expected_books,
    }


@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    seller = sellers.Seller(first_name="Vasya", last_name="Petrov", email="qwe@qwe.rty", password="qwerty")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/seller/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_sellers = await db_session.execute(select(sellers.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0


@pytest.mark.asyncio
async def test_delete_seller_with_books(db_session, async_client):
    seller = sellers.Seller(first_name="Vasya", last_name="Petrov", email="qwe@qwe.rty", password="qwerty")

    db_session.add(seller)
    await db_session.flush()

    book_1 = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)
    book_2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller.id)

    db_session.add_all([book_1, book_2])
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/seller/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_sellers = await db_session.execute(select(sellers.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0

    res = await db_session.execute(select(books.Book).where(books.Book.id == book_1.id))
    book = res.scalars().first()
    assert book is None

    res = await db_session.execute(select(books.Book).where(books.Book.id == book_2.id))
    book = res.scalars().first()
    assert book is None


@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    seller = sellers.Seller(first_name="Vasya", last_name="Petrov", email="qwe@qwe.rty", password="qwerty")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/seller/{seller.id}", json={"first_name": "Petya", "last_name": "Vasiliev", "email": "asd@asd.zxc"}
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    res = await db_session.get(sellers.Seller, seller.id)
    assert res.first_name == "Petya"
    assert res.last_name == "Vasiliev"
    assert res.email == "asd@asd.zxc"
    assert res.password == seller.password
    assert res.id == seller.id
