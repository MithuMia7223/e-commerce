from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class LoginSchema(BaseModel):
    username_or_email: str
    password: str


class CategoryCreate(BaseModel):
    name: str


class CategoryOut(BaseModel):
    id: int
    name: str


class RatingCreate(BaseModel):
    product_id: int
    rating: int
    comment: str


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock: Optional[int] = 0
    category_id: Optional[int] = None


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock: Optional[int] = 0
    category_id: Optional[int] = None


class ProductImageCreate(BaseModel):
    product_id: int
    image_url: str


class ReviewCreate(BaseModel):
    user_id: int
    product_id: int
    rating: int  # ⭐ 1-5
    comment: Optional[str] = None


class WishlistCreate(BaseModel):
    user_id: int
    product_id: int


class CartCreate(BaseModel):
    product_id: int
    quantity: int = 1


class OrderCreate(BaseModel):
    user_id: int
    quantity: int


class CommentCreate(BaseModel):
    user_id: int
    product_id: int
    comment: str
    parent_id: Optional[int] = None


class OrderItemOut(BaseModel):
    product_id: int
    quantity: int
    price: float


class OrderOut(BaseModel):
    id: int
    user_id: int
    status: str
    payment_status: str
    items: List[OrderItemOut]


# =====================
# SHIPPING ADDRESS SCHEMAS
# =====================
class ShippingAddressCreate(BaseModel):
    name: str
    address: str
    city: str
    postal_code: str
    country: str
    phone: str
    is_default: Optional[bool] = False


class ShippingAddressOut(BaseModel):
    id: int
    name: str
    address: str
    city: str
    postal_code: str
    country: str
    phone: str
    is_default: bool


# =====================
# COUPON SCHEMAS
# =====================
class CouponCreate(BaseModel):
    code: str
    discount_type: str  # percentage or fixed
    discount_value: float
    minimum_amount: Optional[float] = 0
    usage_limit: Optional[int] = None
    expires_at: datetime


class CouponOut(BaseModel):
    id: int
    code: str
    discount_type: str
    discount_value: float
    minimum_amount: float
    usage_limit: Optional[int]
    used_count: int
    expires_at: datetime
    is_active: bool


class CouponUsageCreate(BaseModel):
    coupon_id: int
    order_id: int
    discount_amount: float


# =====================
# PRODUCT VARIANT SCHEMAS
# =====================
class ProductVariantCreate(BaseModel):
    product_id: int
    name: str
    value: str
    price_adjustment: Optional[float] = 0
    stock: Optional[int] = 0
    sku: str


class ProductVariantOut(BaseModel):
    id: int
    product_id: int
    name: str
    value: str
    price_adjustment: float
    stock: int
    sku: str


# =====================
# REFUND SCHEMAS
# =====================
class RefundCreate(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    reason: str


class RefundOut(BaseModel):
    id: int
    order_id: int
    user_id: int
    product_id: int
    quantity: int
    reason: str
    status: str
    refund_amount: Optional[float]
    refund_date: Optional[datetime]
    created_at: datetime


# =====================
# PRODUCT ANALYTICS SCHEMAS
# =====================
class ProductAnalyticsCreate(BaseModel):
    product_id: int
    views: Optional[int] = 0
    purchases: Optional[int] = 0
    revenue: Optional[float] = 0


class ProductAnalyticsOut(BaseModel):
    id: int
    product_id: int
    views: int
    purchases: int
    revenue: float
    date: datetime


# =====================
# USER PROFILE SCHEMAS
# =====================
class UserProfileCreate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None


class UserProfileOut(BaseModel):
    id: int
    user_id: int
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    date_of_birth: Optional[datetime]
    gender: Optional[str]


# =====================
# EXTENDED ORDER SCHEMAS
# =====================
class OrderCreateExtended(BaseModel):
    shipping_address_id: int
    coupon_code: Optional[str] = None
    payment_method: str


class OrderOutExtended(BaseModel):
    id: int
    user_id: int
    status: str
    payment_status: str
    payment_method: Optional[str]
    transaction: Optional[str]
    shipping_address: ShippingAddressOut
    items: List[OrderItemOut]
    subtotal: float
    discount_amount: Optional[float]
    total_amount: float
    created_at: datetime


class NotificationCreate(BaseModel):
    user_id: int
    message: str
