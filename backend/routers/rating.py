from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models, schemas
from db import get_db
from oauth2 import verify_token

router = APIRouter(prefix="/ratings", tags=["Ratings"])


# =========================
# ADD / UPDATE RATING ⭐
# =========================
@router.post("/", status_code=status.HTTP_201_CREATED)
def add_rating(
    data: schemas.RatingCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_token),
):

    # check product exists
    product = (
        db.query(models.Product).filter(models.Product.id == data.product_id).first()
    )

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # check if rating already exists
    existing = (
        db.query(models.Rating)
        .filter(
            models.Rating.user_id == user.id,
            models.Rating.product_id == data.product_id,
        )
        .first()
    )

    if existing:
        existing.rating = data.rating
        db.commit()
        return {"message": "Rating updated ⭐", "rating": existing.rating}

    # create new rating
    rating = models.Rating(
        user_id=user.id, product_id=data.product_id, rating=data.rating
    )

    db.add(rating)
    db.commit()
    db.refresh(rating)

    return {"message": "Rating added ⭐", "rating": rating}


# =========================
# GET PRODUCT RATINGS 📊
# =========================
@router.get("/product/{product_id}")
def get_product_ratings(product_id: int, db: Session = Depends(get_db)):

    ratings = (
        db.query(models.Rating).filter(models.Rating.product_id == product_id).all()
    )

    if not ratings:
        return {
            "product_id": product_id,
            "average_rating": 0,
            "total_ratings": 0,
            "ratings": [],
        }

    avg_rating = sum([r.rating for r in ratings]) / len(ratings)

    return {
        "product_id": product_id,
        "average_rating": round(avg_rating, 2),
        "total_ratings": len(ratings),
        "ratings": ratings,
    }


# =========================
# GET MY RATING 👤
# =========================
@router.get("/me/{product_id}")
def my_rating(
    product_id: int, db: Session = Depends(get_db), user=Depends(verify_token)
):

    rating = (
        db.query(models.Rating)
        .filter(
            models.Rating.user_id == user.id, models.Rating.product_id == product_id
        )
        .first()
    )

    if not rating:
        return {"message": "No rating yet", "rating": None}

    return {"product_id": product_id, "rating": rating.rating}


# =========================
# DELETE RATING ❌
# =========================
@router.delete("/{product_id}")
def delete_rating(
    product_id: int, db: Session = Depends(get_db), user=Depends(verify_token)
):

    rating = (
        db.query(models.Rating)
        .filter(
            models.Rating.user_id == user.id, models.Rating.product_id == product_id
        )
        .first()
    )

    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")

    db.delete(rating)
    db.commit()

    return {"message": "Rating deleted ❌"}
