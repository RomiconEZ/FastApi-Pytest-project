import pytest
from fastapi import status

from .constants import PREFIX, SELLER_1_EXAMPLE_PASSWORD
from .fixtures import get_new_seller


@pytest.mark.asyncio
async def test_login_for_access_token_success(async_client, db_session, get_new_seller):
    # Предварительное создание продавца (пользователя) в БД
    seller = get_new_seller

    # Данные для аутентификации
    login_data = {"username": seller.email, "password": SELLER_1_EXAMPLE_PASSWORD}

    # Отправка запроса на аутентификацию
    response = await async_client.post(PREFIX + "token", data=login_data)

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_for_access_token_wrong_password(async_client, db_session, get_new_seller):
    seller = get_new_seller

    login_data = {"username": seller.email, "password": SELLER_1_EXAMPLE_PASSWORD + "wrong"}

    response = await async_client.post(PREFIX + "token", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_login_for_access_token_wrong_email(async_client, db_session, get_new_seller):
    seller = get_new_seller

    login_data = {"username": seller.email + "wrong", "password": SELLER_1_EXAMPLE_PASSWORD}

    response = await async_client.post(PREFIX + "token", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
