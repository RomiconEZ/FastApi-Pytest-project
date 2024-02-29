from fastapi import HTTPException, status
from sqlalchemy import select

from src.models.users import User
from src.schemas.users import CreateUser, UserOut
from src.utils.auth import get_password_hash, verify_password
from src.utils.db_session import DBSession


class UsersService:
    @staticmethod
    async def create_user(user_data: CreateUser, session: DBSession):
        hashed_password = get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
        )
        session.add(user)
        await session.commit()

        # асинхронно обновляет экземпляр user, синхронизируя его с текущим состоянием в базе данных.
        await session.refresh(user)

        return UserOut.from_orm(user)  # преобразования экземпляра модели SQLAlchemy user в модель Pydantic UserOut.

    @staticmethod
    async def authenticate_user(email: str, password: str, session: DBSession) -> UserOut | None:
        query = select(User).where(User.email == email)
        res = await session.execute(query)

        # используется для получения одного результата из выполненного запроса или None, если результат отсутствует.
        user = res.scalar_one_or_none()
        if user and verify_password(password, user.hashed_password):
            return UserOut.from_orm(user)
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
