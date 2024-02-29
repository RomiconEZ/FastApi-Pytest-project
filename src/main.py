from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.security import OAuth2PasswordBearer

from src.configurations.database import create_db_and_tables, delete_db_and_tables, global_init
from src.routers import v1_router

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запускается при старте приложения
    global_init()
    await create_db_and_tables()
    yield
    # Запускается при остановке приложения
    await delete_db_and_tables()


def create_application() -> FastAPI:
    app = FastAPI(
        title="Book Library App",
        description="",
        version="0.0.1",
        responses={404: {"description": "Not Found!"}},
        default_response_class=ORJSONResponse,  # Подключаем быстрый сериализатор,
        lifespan=lifespan,
    )
    _configure(app)  # Конфигурируем приложение
    return app


def _configure(app: FastAPI):
    app.include_router(v1_router)


app = create_application()
