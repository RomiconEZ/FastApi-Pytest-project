from datetime import timedelta

from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.schemas.token import Token
from src.service.users import UsersService
from src.utils.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from fastapi import Depends
from src.utils.db_session import DBSession

auth_router = APIRouter(tags=["auth"])



@auth_router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: DBSession = Depends()):
    user = await UsersService.authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}