from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models, schemas
from db import get_db
from oauth2 import verify_token

router = APIRouter(prefix="/reviews", tags=["Reviews"])


# =========================
# CREATE REVIEW ⭐
# =========================
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_review(
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

    # prevent duplicate review
    existing = (
        db.query(models.Review)
        .filter(
            models.Review.user_id == user.id,
            models.Review.product_id == data.product_id,
        )
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="You already reviewed this product")

    review = models.Review(
        user_id=user.id,
        product_id=data.product_id,
        rating=data.rating,
        comment=data.comment,
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return {"message": "Review added ⭐", "review": review}


# =========================
# GET ALL REVIEWS 💬
# =========================
@router.get("/")
def get_reviews(db: Session = Depends(get_db)):

    reviews = db.query(models.Review).all()

    return {"total": len(reviews), "reviews": reviews}


# =========================
# GET PRODUCT REVIEWS 📦
# =========================
@router.get("/product/{product_id}")
def product_reviews(product_id: int, db: Session = Depends(get_db)):

    reviews = (
        db.query(models.Review).filter(models.Review.product_id == product_id).all()
    )

    if not reviews:
        return {"message": "No reviews yet", "reviews": []}

    # calculate average rating
    avg_rating = sum([r.rating for r in reviews]) / len(reviews)

    return {
        "product_id": product_id,
        "average_rating": round(avg_rating, 2),
        "total_reviews": len(reviews),
        "reviews": reviews,
    }


# =========================
# UPDATE REVIEW ✏️
# =========================
@router.put("/{review_id}")
def update_review(
    review_id: int,
    data: schemas.RatingCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_token),
):

    review = db.query(models.Review).filter(models.Review.id == review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    review.rating = data.rating
    review.comment = data.comment

    db.commit()
    db.refresh(review)

    return {"message": "Review updated ✏️", "review": review}


# =========================
# DELETE REVIEW ❌
# =========================
@router.delete("/{review_id}")
def delete_review(
    review_id: int, db: Session = Depends(get_db), user=Depends(verify_token)
):

    review = db.query(models.Review).filter(models.Review.id == review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    db.delete(review)
    db.commit()

    return {"message": "Review deleted ❌"}
