from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db
from ..oauth2 import verify_token

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def add_to_cart(
    cart: schemas.CartCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token),
):

    product = (
        db.query(models.Product).filter(models.Product.id == cart.product_id).first()
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    if product.stock <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Product out of stock"
        )

    existing_item = (
        db.query(models.Cart)
        .filter(
            models.Cart.user_id == user_id, models.Cart.product_id == cart.product_id
        )
        .first()
    )

    if existing_item:

        if existing_item.quantity >= product.stock:
            raise HTTPException(status_code=400, detail="Maximum stock reached")

        existing_item.quantity += 1

        db.commit()
        db.refresh(existing_item)

        return {"message": "Cart quantity updated", "cart": existing_item}
    item = models.Cart(user_id=user_id, product_id=cart.product_id, quantity=1)

    db.add(item)
    db.commit()
    db.refresh(item)

    return {"message": "Added to cart", "cart": item}


@router.get("/")
def get_cart(db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    # Optimized with join to avoid N+1 query problem
    results = (
        db.query(models.Cart, models.Product)
        .join(models.Product, models.Cart.product_id == models.Product.id)
        .filter(models.Cart.user_id == user_id)
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
                "product_name": product.name,
                "product_image": product.image,
                "price": product.price,
                "quantity": item.quantity,
                "subtotal": subtotal,
            }
        )

    return {"cart_items": response, "total_price": total_price}


# -------------------------
# REMOVE FROM CART
# -------------------------
@router.delete("/{product_id}")
def remove_from_cart(
    product_id: int, db: Session = Depends(get_db), user_id: int = Depends(verify_token)
):
    item = (
        db.query(models.Cart)
        .filter(models.Cart.user_id == user_id, models.Cart.product_id == product_id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(item)
    db.commit()

    return {"message": "Item removed from cart"}


@router.put("/{product_id}")
def update_cart_quantity(
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token),
):

    item = (
        db.query(models.Cart)
        .filter(models.Cart.user_id == user_id, models.Cart.product_id == product_id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if quantity > product.stock:
        raise HTTPException(status_code=400, detail="Quantity exceeds stock")

    item.quantity = quantity

    db.commit()
    db.refresh(item)

    return {"message": "Cart updated", "cart": item}


@router.post("/checkout")
def checkout(db: Session = Depends(get_db), user_id: int = Depends(verify_token)):

    cart_items = db.query(models.Cart).filter(models.Cart.user_id == user_id).all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Create single order
    order = models.Order(user_id=user_id, status="pending", payment_status="unpaid")

    # Don't commit yet, ensure everything is atomic
    db.add(order)
    db.flush()  # Get order ID without committing transaction

    total_amount = 0
    for item in cart_items:
        product = (
            db.query(models.Product)
            .filter(models.Product.id == item.product_id)
            .first()
        )

        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400, detail=f"{product.name} stock not available"
            )

        # reduce stock
        product.stock -= item.quantity

        subtotal = product.price * item.quantity

        total_amount += subtotal

        order_item = models.OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=product.price,
        )

        db.add(order_item)

    # clear cart
    db.query(models.Cart).filter(models.Cart.user_id == user_id).delete()

    db.commit()
    db.refresh(order)

    return {
        "message": "Checkout successful",
        "order_id": order.id,
        "total_amount": total_amount,
    }
