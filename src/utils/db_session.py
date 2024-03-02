from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session

DBSession = Annotated[AsyncSession, Depends(get_async_session)]
