import pytest
from fastapi import status
from src.models import sellers
from src.utils.auth import get_password_hash


@pytest.mark.asyncio
async def test_login_for_access_token_success(async_client, db_session):
    # Предварительное создание продавца (пользователя) в БД
    test_seller = sellers.Seller(first_name="Test_First_Name",
                                 last_name="Test_Last_Name",
                                 email="seller@example.com",
                                 password=get_password_hash("hashed_password"))
    db_session.add(test_seller)
    await db_session.flush()

    # Данные для аутентификации
    login_data = {
        "username": "seller@example.com",
        "password": "hashed_password"
    }

    # Отправка запроса на аутентификацию
    response = await async_client.post("/api/v1/token", data=login_data)
    print(response.json())

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_for_access_token_wrong_password(async_client, db_session):
    test_seller = sellers.Seller(first_name="Test_First_Name",
                                 last_name="Test_Last_Name",
                                 email="seller@example.com",
                                 password=get_password_hash("hashed_password"))
    db_session.add(test_seller)
    await db_session.flush()

    login_data = {
        "username": "seller@example.com",
        "password": "wrong_password"
    }

    response = await async_client.post("/api/v1/token", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_login_for_access_token_wrong_email(async_client, db_session):
    test_seller = sellers.Seller(first_name="Test_First_Name",
                                 last_name="Test_Last_Name",
                                 email="seller@example.com",
                                 password=get_password_hash("hashed_password"))
    db_session.add(test_seller)
    await db_session.flush()

    login_data = {
        "username": "wrong@example.com",
        "password": "password"
    }

    response = await async_client.post("/api/v1/token", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
