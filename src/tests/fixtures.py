import pytest_asyncio

from src.models import sellers
from src.models.sellers import Seller
from src.tests.constants import HASH_SELLER_1_EXAMPLE, HASH_SELLER_2_EXAMPLE


@pytest_asyncio.fixture()
async def get_new_seller(db_session) -> Seller:
    seller = sellers.Seller(**HASH_SELLER_1_EXAMPLE)
    db_session.add(seller)
    await db_session.flush()
    yield seller


@pytest_asyncio.fixture()
async def get_2_new_sellers(db_session) -> Seller:
    seller_1 = sellers.Seller(**HASH_SELLER_1_EXAMPLE)
    seller_2 = sellers.Seller(**HASH_SELLER_2_EXAMPLE)
    db_session.add_all([seller_1, seller_2])
    await db_session.flush()
    yield seller_1, seller_2
