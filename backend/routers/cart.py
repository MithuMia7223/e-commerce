from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models, schemas
from db import get_db
from auth import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def add_to_cart(
    cart: schemas.CartCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):

    product = (
        db.query(models.Product).filter(models.Product.id == cart.product_id).first()
    )

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.stock <= 0:
        raise HTTPException(status_code=400, detail="Out of stock")

    existing_item = (
        db.query(models.Cart)
        .filter(
            models.Cart.user_id == user.id, models.Cart.product_id == cart.product_id
        )
        .first()
    )

    if existing_item:
        if existing_item.quantity + cart.quantity > product.stock:
            raise HTTPException(status_code=400, detail="Not enough stock")

        existing_item.quantity += cart.quantity

        db.commit()
        db.refresh(existing_item)

        return {
            "message": "Cart updated",
            "cart": {
                "id": existing_item.id,
                "product_id": existing_item.product_id,
                "quantity": existing_item.quantity,
            },
        }

    item = models.Cart(
        user_id=user.id, product_id=cart.product_id, quantity=cart.quantity
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return {
        "message": "Added to cart",
        "cart": {
            "id": item.id,
            "product_id": item.product_id,
            "quantity": item.quantity,
        },
    }


@router.get("/")
def get_cart(db: Session = Depends(get_db), user=Depends(get_current_user)):

    results = (
        db.query(models.Cart, models.Product)
        .join(models.Product, models.Cart.product_id == models.Product.id)
        .filter(models.Cart.user_id == user.id)
        .all()
    )

    total_price = 0
    response = []

    for item, product in results:
        subtotal = product.price * item.quantity
        total_price += subtotal

        response.append(
            {
                "cart_id": item.id,
                "product_id": product.id,
                "name": product.name,
                "image": product.image,
                "price": product.price,
                "quantity": item.quantity,
                "subtotal": subtotal,
            }
        )

    return {"items": response, "total_price": total_price}


@router.delete("/{product_id}")
def remove_from_cart(
    product_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):

    item = (
        db.query(models.Cart)
        .filter(models.Cart.user_id == user.id, models.Cart.product_id == product_id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()

    return {"message": "Removed from cart"}


@router.put("/{product_id}")
def update_cart(
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):

    item = (
        db.query(models.Cart)
        .filter(models.Cart.user_id == user.id, models.Cart.product_id == product_id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if quantity > product.stock:
        raise HTTPException(status_code=400, detail="Not enough stock")

    item.quantity = quantity

    db.commit()
    db.refresh(item)

    return {"message": "Updated", "quantity": item.quantity}


@router.post("/checkout")
def checkout(db: Session = Depends(get_db), user=Depends(get_current_user)):

    cart_items = db.query(models.Cart).filter(models.Cart.user_id == user.id).all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart empty")

    order = models.Order(user_id=user.id, status="pending", payment_status="unpaid")

    db.add(order)
    db.flush()

    total = 0

    for item in cart_items:
        product = (
            db.query(models.Product)
            .filter(models.Product.id == item.product_id)
            .first()
        )

        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"{product.name} out of stock")

        product.stock -= item.quantity
        total += product.price * item.quantity

        db.add(
            models.OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=product.price,
            )
        )

    db.query(models.Cart).filter(models.Cart.user_id == user.id).delete()

    db.commit()

    return {"message": "Checkout successful", "order_id": order.id, "total": total}
