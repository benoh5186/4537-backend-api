from pydantic import BaseModel, Field,EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    is_admin: bool


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)