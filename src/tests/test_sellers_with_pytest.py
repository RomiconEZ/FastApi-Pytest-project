import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books, sellers
from src.tests.constants import (
    HASH_SELLER_1_EXAMPLE,
    NEW_SELLER_1_EXAMPLE,
    PREFIX,
    SELLER_1_EXAMPLE,
    SELLER_1_EXAMPLE_PASSWORD,
)
from src.utils.auth import authenticate_user

from .helpers import add_2_books_for_seller

from .fixtures import get_new_seller, get_2_new_sellers


@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = SELLER_1_EXAMPLE
    response = await async_client.post(PREFIX + "seller/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert {key: result_data[key] for key in result_data if key != "id"} == {
        "first_name": HASH_SELLER_1_EXAMPLE["first_name"],
        "last_name": HASH_SELLER_1_EXAMPLE["last_name"],
        "email": HASH_SELLER_1_EXAMPLE["email"],
    }


@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client, get_2_new_sellers):
    seller_1, seller_2 = get_2_new_sellers

    response = await async_client.get(PREFIX + "seller/")

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
async def test_get_single_seller_without_books(db_session, async_client, get_2_new_sellers):
    # Подготовка: создание пользователя для аутентификации
    seller_1, seller_2 = get_2_new_sellers

    # Аутентификация пользователя для получения токена
    access_token = await authenticate_user(async_client, seller_1.email, SELLER_1_EXAMPLE_PASSWORD)

    # Выполнение запроса по 2-ому продавцу с токеном аутентификации
    response = await async_client.get(
        PREFIX + f"seller/{seller_2.id}", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    # Проверка интерфейса ответа
    assert response.json() == {
        "first_name": seller_2.first_name,
        "last_name": seller_2.last_name,
        "email": seller_2.email,
        "id": seller_2.id,
        "books": [],
    }


@pytest.mark.asyncio
async def test_get_single_seller_with_books(db_session, async_client, get_2_new_sellers):
    # Подготовка: создание пользователя для аутентификации
    seller_1, seller_2 = get_2_new_sellers

    # Аутентификация пользователя для получения токена
    access_token = await authenticate_user(async_client, seller_1.email, SELLER_1_EXAMPLE_PASSWORD)

    book_1, book_2 = await add_2_books_for_seller(db_session=db_session, sellerID=seller_2.id)

    # Выполнение запроса по 2-ому продавцу с токеном аутентификации
    response = await async_client.get(
        PREFIX + f"seller/{seller_2.id}", headers={"Authorization": f"Bearer {access_token}"}
    )

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

    assert response.json() == {
        "first_name": seller_2.first_name,
        "last_name": seller_2.last_name,
        "email": seller_2.email,
        "id": seller_2.id,
        "books": expected_books,
    }


@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client, get_new_seller):
    seller = get_new_seller

    response = await async_client.delete(PREFIX + f"seller/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_sellers = await db_session.execute(select(sellers.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0


@pytest.mark.asyncio
async def test_delete_seller_with_books(db_session, async_client, get_new_seller):
    seller = get_new_seller

    book_1, book_2 = await add_2_books_for_seller(db_session=db_session, sellerID=seller.id)

    response = await async_client.delete(PREFIX + f"seller/{seller.id}")

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
async def test_update_seller(db_session, async_client, get_new_seller):
    seller = get_new_seller

    response = await async_client.put(
        PREFIX + f"seller/{seller.id}",
        json={
            "first_name": NEW_SELLER_1_EXAMPLE["first_name"],
            "last_name": NEW_SELLER_1_EXAMPLE["last_name"],
            "email": NEW_SELLER_1_EXAMPLE["email"],
        },
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    res = await db_session.get(sellers.Seller, seller.id)
    assert res.first_name == NEW_SELLER_1_EXAMPLE["first_name"]
    assert res.last_name == NEW_SELLER_1_EXAMPLE["last_name"]
    assert res.email == NEW_SELLER_1_EXAMPLE["email"]
    assert res.password == seller.password
    assert res.id == seller.id
