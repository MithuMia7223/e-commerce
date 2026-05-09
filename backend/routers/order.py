from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db
from ..oauth2 import verify_token
from ..auth import admin_required
from ..email_utils import send_email

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token),
):

    # check product exists
    product = (
        db.query(models.Product).filter(models.Product.id == order.product_id).first()
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    if product.stock < order.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    # Reduce stock immediately on order creation
    product.stock -= order.quantity

    new_order = models.Order(
        user_id=user_id,
        status="pending",
        payment_status="unpaid",
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    order_item = models.OrderItem(
        order_id=new_order.id,
        product_id=order.product_id,
        quantity=order.quantity,
        price=product.price,
    )

    db.add(order_item)
    db.commit()

    # Send email notification
    user = db.query(models.User).filter(models.User.id == user_id).first()
    send_email(
        user.email,
        "Order Created",
        f"Your order #{new_order.id} has been created successfully.",
    )

    return {"message": "Order created", "order": new_order}


@router.get("/")
def get_orders(db: Session = Depends(get_db), user_id: int = Depends(verify_token)):

    # Optimized to fetch orders and their items efficiently
    # Assuming a relationship 'items' exists in models.Order
    from sqlalchemy.orm import joinedload

    orders = (
        db.query(models.Order)
        .options(joinedload(models.Order.items))
        .filter(models.Order.user_id == user_id)
        .all()
    )
    return orders


@router.post("/{order_id}/pay")
def pay_order(
    order_id: int,
    payment_method: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token),
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # only owner can pay
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    if order.payment_status == "paid":
        raise HTTPException(status_code=400, detail="Order already paid")

    order.payment_status = "paid"
    order.payment_method = payment_method
    order.transaction_id = f"TXN_{order.id}"

    db.commit()
    db.refresh(order)

    return {
        "message": "Payment successful",
        "transaction_id": order.transaction_id,
        "order": order,
    }


@router.put("/{order_id}/status")
def update_order_status(
    order_id: int,
    status_value: str,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):

    order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status_value

    db.commit()
    db.refresh(order)

    return {"message": "Order status updated", "order": order}
