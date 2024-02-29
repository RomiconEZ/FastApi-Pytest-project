import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books, sellers


@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {"first_name": "Vasya", "last_name": "Petrov", "email": "qwe@qwe.rty", "password": "qwerty"}
    response = await async_client.post("/api/v1/seller/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data == {
        "id": 1,
        "first_name": "Vasya",
        "last_name": "Petrov",
        "email": "qwe@qwe.rty",
    }


@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    seller_1 = sellers.Seller(first_name="Vasya", last_name="Petrov", email="qwe@qwe.rty", password="qwerty")
    seller_2 = sellers.Seller(first_name="Petya", last_name="Vasiliev", email="asd@asd.zxc", password="qazwsx")

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
    seller = sellers.Seller(first_name="Vasya", last_name="Petrov", email="qwe@qwe.rty", password="qwerty")
    db_session.add(seller)
    await db_session.flush()

    response = await async_client.get(f"/api/v1/seller/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "first_name": "Vasya",
        "last_name": "Petrov",
        "email": "qwe@qwe.rty",
        "id": seller.id,
        "books": [],
    }


@pytest.mark.asyncio
async def test_get_single_seller_with_books(db_session, async_client):
    seller = sellers.Seller(first_name="Vasya", last_name="Petrov", email="qwe@qwe.rty", password="qwerty")
    db_session.add(seller)
    await db_session.flush()

    book_1 = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)
    book_2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller.id)

    db_session.add_all([book_1, book_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/seller/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "first_name": "Vasya",
        "last_name": "Petrov",
        "email": "qwe@qwe.rty",
        "id": seller.id,
        "books": [
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
        ],
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
