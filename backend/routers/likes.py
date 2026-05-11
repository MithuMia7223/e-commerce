from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
from db import get_db
from oauth2 import verify_token

router = APIRouter(prefix="/likes", tags=["Likes"])


# =========================
# LIKE PRODUCT
# =========================
@router.post("/{product_id}")
def like_product(
    product_id: int, db: Session = Depends(get_db), user=Depends(verify_token)
):

    product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing_like = (
        db.query(models.Like)
        .filter(models.Like.user_id == user.id, models.Like.product_id == product_id)
        .first()
    )

    if existing_like:
        raise HTTPException(status_code=400, detail="Already liked")

    like = models.Like(user_id=user.id, product_id=product_id)

    db.add(like)
    db.commit()

    return {"message": "Liked successfully"}


# =========================
# UNLIKE PRODUCT (NEW FEATURE)
# =========================
@router.delete("/{product_id}")
def unlike_product(
    product_id: int, db: Session = Depends(get_db), user=Depends(verify_token)
):

    like = (
        db.query(models.Like)
        .filter(models.Like.user_id == user.id, models.Like.product_id == product_id)
        .first()
    )

    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    db.delete(like)
    db.commit()

    return {"message": "Unlike successfully"}


# =========================
# GET LIKES (USER)
# =========================
@router.get("/me")
def my_likes(db: Session = Depends(get_db), user=Depends(verify_token)):

    likes = db.query(models.Like).filter(models.Like.user_id == user.id).all()

    return likes


@router.get("/")
def get_likes(db: Session = Depends(get_db)):
    return db.query(models.Like).all()
