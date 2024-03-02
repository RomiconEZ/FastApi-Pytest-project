from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select

from src.configurations.settings import settings
from src.models.sellers import Seller
from src.schemas import SellerOut
from src.utils.db_session import DBSession

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Создание контекста хеширования
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Возвращает хеш пароля.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли введенный пароль сохраненному хешу пароля.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def check_seller_token(session: DBSession, token: str = Depends(oauth2_scheme)) -> SellerOut:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token payload")

        result = await session.execute(select(Seller).filter_by(email=email))
        seller = result.scalars().first()
        if seller is None:
            raise HTTPException(status_code=404, detail="Seller not found")

        return SellerOut.model_validate(seller)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Функция для аутентификации пользователя и получения токена доступа
async def authenticate_user(async_client, username: str, password: str):
    """
    Получение токена по email и истинному password(не хэшированному)
    """
    response = await async_client.post("/api/v1/token", data={"username": username, "password": password})
    assert response.status_code == status.HTTP_200_OK
    return response.json()["access_token"]
