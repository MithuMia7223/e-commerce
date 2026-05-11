from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    Text,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db import Base


# =====================
# USER
# =====================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(String, default="buyer")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    products = relationship("Product", back_populates="vendor")
    comments = relationship("Comment", back_populates="user")
    orders = relationship("Order", back_populates="user")


# =====================
# CATEGORY
# =====================
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)

    products = relationship("Product", back_populates="category")


# =====================
# PRODUCT
# =====================
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, index=True)
    description = Column(Text)
    price = Column(Float)
    stock = Column(Integer, default=0)

    vendor_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))

    share_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    vendor = relationship("User", back_populates="products")
    category = relationship("Category", back_populates="products")

    images = relationship("ProductImage", back_populates="product")
    reviews = relationship("Review", back_populates="product")


# =====================
# PRODUCT IMAGE
# =====================
class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    image_url = Column(String)

    product = relationship("Product", back_populates="images")


# =====================
# WISHLIST ❤️
# =====================
class Wishlist(Base):
    __tablename__ = "wishlist"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))


# =====================
# REVIEW + RATING ⭐
# =====================
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))

    rating = Column(Integer)  # 1-5
    comment = Column(Text)

    parent_id = Column(Integer, ForeignKey("reviews.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="reviews")
    replies = relationship("Review", remote_side=[id])


# =====================
# LIKE
# =====================
class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    product_id = Column(Integer)


# =====================
# COMMENT (REPLY SYSTEM FIXED)
# =====================
class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))

    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)

    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="comments")
    replies = relationship("Comment", remote_side=[id])


# =====================
# NOTIFICATION
# =====================
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    message = Column(String)


# =====================
# CART
# =====================
class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)


# =====================
# SHIPPING ADDRESS
# =====================
class ShippingAddress(Base):
    __tablename__ = "shipping_addresses"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    address = Column(String)
    city = Column(String)
    postal_code = Column(String)
    country = Column(String)
    phone = Column(String)
    is_default = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# =====================
# COUPON/DISCOUNT
# =====================
class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    discount_type = Column(String)  # percentage or fixed
    discount_value = Column(Float)
    minimum_amount = Column(Float, default=0)
    usage_limit = Column(Integer, default=None)
    used_count = Column(Integer, default=0)
    expires_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CouponUsage(Base):
    __tablename__ = "coupon_usage"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    coupon_id = Column(Integer, ForeignKey("coupons.id"))
    order_id = Column(Integer, ForeignKey("orders.id"))
    discount_amount = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# =====================
# PRODUCT VARIANTS
# =====================
class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    name = Column(String)  # e.g., "Size", "Color"
    value = Column(String)  # e.g., "Large", "Red"
    price_adjustment = Column(Float, default=0)
    stock = Column(Integer, default=0)
    sku = Column(String, unique=True)

    product = relationship("Product")


# =====================
# REFUND/RETURN
# =====================
class Refund(Base):
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    reason = Column(Text)
    status = Column(String, default="pending")  # pending/approved/rejected
    refund_amount = Column(Float)
    refund_date = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# =====================
# PRODUCT ANALYTICS
# =====================
class ProductAnalytics(Base):
    __tablename__ = "product_analytics"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    views = Column(Integer, default=0)
    purchases = Column(Integer, default=0)
    revenue = Column(Float, default=0)
    date = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product")


# =====================
# USER PROFILE EXTENSIONS
# =====================
class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)
    avatar_url = Column(String)
    bio = Column(Text)
    date_of_birth = Column(DateTime(timezone=True), nullable=True)
    gender = Column(String, nullable=True)

    user = relationship("User")


# =====================
# ORDER + TRACKING 🚚
# =====================
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    status = Column(String, default="processing")  # processing/shipped/delivered
    payment_status = Column(String, default="unpaid")

    payment_method = Column(String, nullable=True)
    transaction = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))

    quantity = Column(Integer)
    price = Column(Float)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
