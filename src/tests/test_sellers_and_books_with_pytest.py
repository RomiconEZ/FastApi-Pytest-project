import pytest
from fastapi import status

from src.tests.constants import NEW_SELLER_1_EXAMPLE, PREFIX, SELLER_1_EXAMPLE, SELLER_1_EXAMPLE_PASSWORD

from .models import BookExample


@pytest.mark.asyncio
async def test_create_addbook_update_delete_seller(async_client):
    # ============= Создание продавца ================
    seller_data = SELLER_1_EXAMPLE

    response = await async_client.post(PREFIX + "seller/", json=seller_data)

    assert response.status_code == status.HTTP_201_CREATED

    seller_id = response.json()["id"]

    # ================= Аутентификация продавца ===================

    login_data = {"username": seller_data["email"], "password": SELLER_1_EXAMPLE_PASSWORD}

    response = await async_client.post(PREFIX + "token", data=login_data)

    assert response.status_code == status.HTTP_200_OK

    access_token = response.json()["access_token"]

    # ============= Получение информации о продавце ================

    response = await async_client.get(
        PREFIX + f"seller/{seller_id}", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    book = BookExample(seller_id=seller_id).to_dict()

    # ==================== Добавление книги =======================

    response = await async_client.post(
        PREFIX + "books/", headers={"Authorization": f"Bearer {access_token}"}, json=book
    )

    assert response.status_code == status.HTTP_201_CREATED

    # ============= Получение информации о продавце ================

    response = await async_client.get(
        PREFIX + f"seller/{seller_id}", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    # ============= Обновление информации о продавце ================

    response = await async_client.put(
        PREFIX + f"seller/{seller_id}",
        json={
            "first_name": NEW_SELLER_1_EXAMPLE["first_name"],
            "last_name": NEW_SELLER_1_EXAMPLE["last_name"],
            "email": NEW_SELLER_1_EXAMPLE["email"],
        },
    )

    assert response.status_code == status.HTTP_200_OK

    # ========= Повторная аутентификация из-за смены email ========

    new_login_data = {"username": NEW_SELLER_1_EXAMPLE["email"], "password": SELLER_1_EXAMPLE_PASSWORD}

    response = await async_client.post(PREFIX + "token", data=new_login_data)

    assert response.status_code == status.HTTP_200_OK

    access_token = response.json()["access_token"]

    # ============= Получение информации о продавце ================

    response = await async_client.get(
        PREFIX + f"seller/{seller_id}", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    # ==================== Удаление продавца =======================

    response = await async_client.delete(PREFIX + f"seller/{seller_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
