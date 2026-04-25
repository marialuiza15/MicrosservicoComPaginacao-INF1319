from pydantic import BaseModel, HttpUrl, field_validator
from datetime import datetime
from typing import Optional, List


# ===== User Schemas =====
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: str
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== URL Schemas =====
class URLBase(BaseModel):
    original_url: str
    
    @field_validator('original_url')
    @classmethod
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL deve começar com http:// ou https://')
        return v


class URLCreate(URLBase):
    pass


class URLDelete(BaseModel):
    url_id: str


class URLResponse(BaseModel):
    id: str
    original_url: str
    short_code: str
    short_url: str
    user_id: str
    created_at: datetime
    is_active: bool
    count: int
    
    class Config:
        from_attributes = True


class URLUpdate(BaseModel):
    is_active: Optional[bool] = None


# ===== Pagination Schemas =====
class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[URLResponse]
    has_next: bool
    has_previous: bool


# ===== Auth Schemas =====
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
