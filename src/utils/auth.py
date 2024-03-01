from datetime import datetime, timedelta

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from src.configurations.settings import settings
from src.models.sellers import Seller
from src.schemas import UserOut
from src.utils.db_session import DBSession
from fastapi import Depends, HTTPException
from jose import jwt, JWTError

from fastapi import status
from sqlalchemy import select

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


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except JWTError:
        raise credentials_exception


async def get_current_user(session: DBSession, token: str = Depends(oauth2_scheme)) -> UserOut:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=400, detail="Invalid token payload")

        result = await session.execute(select(Seller).filter(Seller.email == username))
        user = result.scalars().first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return UserOut.from_orm(user)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Функция для аутентификации пользователя и получения токена доступа
async def authenticate_user(async_client, username: str, password: str):
    response = await async_client.post("/api/v1/token", data={"username": username, "password": password})
    assert response.status_code == status.HTTP_200_OK
    return response.json()["access_token"]
