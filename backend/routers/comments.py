from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models, schemas
from db import get_db
from oauth2 import verify_token

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.post("/")
def create_comment(
    data: schemas.CommentCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_token),
):

    # check product exists
    product = (
        db.query(models.Product).filter(models.Product.id == data.product_id).first()
    )

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    new_comment = models.Comment(
        user_id=user.id, product_id=data.product_id, comment=data.comment
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return {"message": "Comment added", "comment": new_comment}


@router.get("/")
def get_comments(db: Session = Depends(get_db)):
    return db.query(models.Comment).all()


@router.get("/product/{product_id}")
def get_product_comments(product_id: int, db: Session = Depends(get_db)):

    return (
        db.query(models.Comment).filter(models.Comment.product_id == product_id).all()
    )


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int, db: Session = Depends(get_db), user=Depends(verify_token)
):

    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    db.delete(comment)
    db.commit()

    return {"message": "Comment deleted"}
