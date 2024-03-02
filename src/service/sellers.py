from fastapi import HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.sellers import Seller
from src.schemas import IncomingSeller
from src.schemas.sellers import ReturnedAllSellers, ReturnedSeller, ReturnedSellerWithBooks, SellerOut, UpdatedSeller
from src.utils.auth import get_password_hash, verify_password
from src.utils.db_session import DBSession


class SellersService:
    @staticmethod
    async def create_seller(seller: IncomingSeller, session: DBSession) -> ReturnedSeller:
        hashed_password = get_password_hash(seller.password)
        new_seller = Seller(
            first_name=seller.first_name,
            last_name=seller.last_name,
            email=seller.email,
            password=hashed_password,
        )
        session.add(new_seller)

        await session.flush()

        return ReturnedSeller.from_orm(new_seller)

    @staticmethod
    async def get_all_sellers(session: DBSession) -> ReturnedAllSellers | Response:
        query = select(Seller)
        res = await session.execute(query)
        sellers = res.scalars().all()
        if sellers:
            sellers_response = [ReturnedSeller.from_orm(seller) for seller in sellers]
            return ReturnedAllSellers(sellers=sellers_response)
        else:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

    @staticmethod
    async def get_seller(seller_id: int, session: DBSession) -> ReturnedSellerWithBooks | Response:

        res = await session.execute(select(Seller).where(Seller.id == seller_id).options(selectinload(Seller.books)))
        seller = res.scalars().first()
        if seller:
            return ReturnedSellerWithBooks.from_orm(seller)
        else:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

    @staticmethod
    async def delete_seller(seller_id: int, session: DBSession) -> Response:
        deleted_seller = await session.get(Seller, seller_id)
        if deleted_seller:
            await session.delete(deleted_seller)
            await session.flush()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

    @staticmethod
    async def update_seller(seller_id: int, new_data: UpdatedSeller, session: DBSession) -> ReturnedSeller | Response:
        updated_seller = await session.get(Seller, seller_id)
        if updated_seller:
            # Проходим по всем полям в new_data
            for field_name, value in new_data.dict(exclude_unset=True).items():
                # Устанавливаем значение поля updated_seller, соответствующее каждому полю new_data
                setattr(updated_seller, field_name, value)

            await session.flush()
            return ReturnedSeller.from_orm(updated_seller)
        else:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

    @staticmethod
    async def authenticate_seller(email: str, password: str, session: DBSession) -> SellerOut | None:
        query = select(Seller).where(Seller.email == email)
        res = await session.execute(query)

        # используется для получения одного результата из выполненного запроса или None, если результат отсутствует.
        seller = res.scalar_one_or_none()

        if seller and verify_password(password, seller.password):
            return SellerOut.from_orm(seller)
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
