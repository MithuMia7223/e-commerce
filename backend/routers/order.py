from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

import models
from db import get_db
from oauth2 import verify_token
from auth import admin_required
from email_utils import send_email

router = APIRouter(prefix="/orders", tags=["Orders"])


# =========================
# CREATE ORDER (SAFE)
# =========================
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_order(
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    user=Depends(verify_token),
):

    product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.stock < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    order = models.Order(user_id=user.id, status="pending", payment_status="unpaid")

    db.add(order)
    db.flush()

    product.stock -= quantity

    order_item = models.OrderItem(
        order_id=order.id, product_id=product_id, quantity=quantity, price=product.price
    )

    db.add(order_item)
    db.commit()

    # email (non-blocking safe style)
    try:
        send_email(
            user.email, "Order Created", f"Your order #{order.id} has been created"
        )
    except:
        pass

    return {"message": "Order created", "order_id": order.id}


# =========================
# GET ORDERS (PAGINATION)
# =========================
@router.get("/")
def get_orders(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    user=Depends(verify_token),
):

    orders = (
        db.query(models.Order)
        .options(joinedload(models.Order.items))
        .filter(models.Order.user_id == user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return orders


# =========================
# PAYMENT
# =========================
@router.post("/{order_id}/pay")
def pay_order(
    order_id: int,
    payment_method: str,
    db: Session = Depends(get_db),
    user=Depends(verify_token),
):

    order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    if order.payment_status == "paid":
        raise HTTPException(status_code=400, detail="Already paid")

    order.payment_status = "paid"
    order.payment_method = payment_method
    order.transaction = f"TXN_{order.id}"

    db.commit()

    return {"message": "Payment successful", "transaction": order.transaction}


# =========================
# UPDATE STATUS (ADMIN)
# =========================
@router.put("/{order_id}/status")
def update_status(
    order_id: int,
    status_value: str,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):

    order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    allowed_status = ["pending", "shipped", "delivered", "cancelled"]

    if status_value not in allowed_status:
        raise HTTPException(status_code=400, detail="Invalid status")

    order.status = status_value
    db.commit()

    return {"message": "Order status updated"}


# =========================
# CANCEL ORDER (NEW FEATURE)
# =========================
@router.delete("/{order_id}")
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_token),
):

    order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    if order.status == "shipped":
        raise HTTPException(status_code=400, detail="Cannot cancel shipped order")

    order.status = "cancelled"
    db.commit()

    return {"message": "Order cancelled"}
