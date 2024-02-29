from pydantic import BaseModel, EmailStr, Field


class CreateUser(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4)


class UserOut(BaseModel):
    id: int
    email: EmailStr

    class ConfigDict:
        from_attributes = True
