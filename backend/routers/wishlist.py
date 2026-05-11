from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
from db import get_db
from oauth2 import verify_token

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])


# =========================
# ADD TO WISHLIST ❤️
# =========================
@router.post("/{product_id}", status_code=status.HTTP_201_CREATED)
def add_to_wishlist(
    product_id: int, db: Session = Depends(get_db), user=Depends(verify_token)
):

    # check product exists
    product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # prevent duplicate wishlist
    existing = (
        db.query(models.Wishlist)
        .filter(
            models.Wishlist.user_id == user.id, models.Wishlist.product_id == product_id
        )
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Already in wishlist")

    item = models.Wishlist(user_id=user.id, product_id=product_id)

    db.add(item)
    db.commit()
    db.refresh(item)

    return {"message": "Added to wishlist ❤️", "wishlist_id": item.id}


# =========================
# GET WISHLIST 📄
# =========================
@router.get("/")
def get_wishlist(db: Session = Depends(get_db), user=Depends(verify_token)):

    items = (
        db.query(models.Wishlist, models.Product)
        .join(models.Product, models.Wishlist.product_id == models.Product.id)
        .filter(models.Wishlist.user_id == user.id)
        .all()
    )

    result = []

    for wishlist, product in items:
        result.append(
            {
                "wishlist_id": wishlist.id,
                "product_id": product.id,
                "name": product.name,
                "price": product.price,
                "image": product.image,
            }
        )

    return {"total": len(result), "wishlist": result}


# =========================
# REMOVE FROM WISHLIST ❌
# =========================
@router.delete("/{product_id}")
def remove_from_wishlist(
    product_id: int, db: Session = Depends(get_db), user=Depends(verify_token)
):

    item = (
        db.query(models.Wishlist)
        .filter(
            models.Wishlist.user_id == user.id, models.Wishlist.product_id == product_id
        )
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Item not found in wishlist")

    db.delete(item)
    db.commit()

    return {"message": "Removed from wishlist ❌"}
