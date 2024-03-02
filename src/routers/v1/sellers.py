from fastapi import APIRouter, Depends, status

from src.schemas import IncomingSeller, ReturnedAllSellers, ReturnedSeller
from src.schemas.sellers import ReturnedSellerWithBooks, SellerOut, UpdatedSeller
from src.service.sellers import SellersService
from src.utils.auth import check_seller_token
from src.utils.db_session import DBSession

sellers_router = APIRouter(tags=["sellers"], prefix="/seller")


# ===================================================================
# ---------------------РУЧКИ БЕЗ АВТОРИЗАЦИИ-------------------------
# ===================================================================


# Ручка для создания продавца
@sellers_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)
async def create_seller(seller: IncomingSeller, session: DBSession):
    return await SellersService.create_seller(seller, session)


# Ручка для получения всех продавцов
@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    return await SellersService.get_all_sellers(session)


# Ручка для удаления определенного продавца
@sellers_router.delete("/{seller_id}")
async def delete_seller(seller_id: int, session: DBSession):
    return await SellersService.delete_seller(seller_id, session)


# Ручка для обновления информации об определенном продавце
@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, new_data: UpdatedSeller, session: DBSession):
    return await SellersService.update_seller(seller_id, new_data, session)


# ===================================================================
# ---------------------РУЧКИ С АВТОРИЗАЦИЕЙ--------------------------
# ===================================================================


# Ручка для получения информации об определенном продавце
@sellers_router.get("/{seller_id}", response_model=ReturnedSellerWithBooks)
async def get_seller(seller_id: int, session: DBSession, current_user: SellerOut = Depends(check_seller_token)):
    return await SellersService.get_seller(seller_id, session)
