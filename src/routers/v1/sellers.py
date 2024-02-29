from fastapi import APIRouter, status

from src.schemas import IncomingSeller, ReturnedAllSellers, ReturnedSeller
from src.schemas.sellers import ReturnedSellerWithBooks, UpdatedSeller
from src.service.sellers import SellersService
from src.utils.db_session import DBSession

sellers_router = APIRouter(tags=["sellers"], prefix="/seller")



@sellers_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)
async def create_seller(seller: IncomingSeller, session: DBSession):
    return await SellersService.create_seller(seller, session)


@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    return await SellersService.get_all_sellers(session)


@sellers_router.get("/{seller_id}", response_model=ReturnedSellerWithBooks)
async def get_seller(seller_id: int, session: DBSession):
    return await SellersService.get_seller(seller_id, session)


@sellers_router.delete("/{seller_id}")
async def delete_seller(seller_id: int, session: DBSession):
    return await SellersService.delete_seller(seller_id, session)


@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, new_data: UpdatedSeller, session: DBSession):
    return await SellersService.update_seller(seller_id, new_data, session)
