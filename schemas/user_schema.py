from pydantic import BaseModel, Field,EmailStr

"""
User schema module defining Pydantic models for user data validation.

This module provides data models for user registration, login, and custom
exceptions for authentication errors.
"""

class UserCreate(BaseModel):
    """
    Schema representing user registration data.
    """
    email: EmailStr
    password: str = Field(min_length=8)
    is_admin: bool


class UserLogin(BaseModel):
    """
    Schema representing user login credentials.
    """
    email: EmailStr
    password: str = Field(min_length=8)


class PasswordException(Exception):
    """
    Custom exception raised when password validation fails during authentication.
    """
    def __init__(self):
        super().__init__("incorrect password")