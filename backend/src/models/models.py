# Data models for user authentication
from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    # User info from Google OAuth
    name: str
    email: str
    picture: Optional[str] = None


class UserResponse(BaseModel):
    # API response for user endpoints
    user: Optional[User] = None
    error: Optional[str] = None
