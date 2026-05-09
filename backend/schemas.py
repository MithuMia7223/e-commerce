from pydantic import BaseModel
from typing import Optional


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class LoginSchema(BaseModel):
    email: str
    password: str


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float


class CartCreate(BaseModel):
    user_id: int
    product_id: int


class OrderCreate(BaseModel):
    user_id: int
    product_id: int


class CommentCreate(BaseModel):
    user_id: int
    product_id: int
    comment: str


class NotificationCreate(BaseModel):
    user_id: int
    message: str
