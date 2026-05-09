from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models

from ..db import get_db

router = APIRouter(
    prefix="/likes",
    tags=["Likes"]
)


@router.post("/{product_id}/{user_id}")
def like_product(
    product_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):

    item = models.Like(
        user_id=user_id,
        product_id=product_id
    )

    db.add(item)
    db.commit()

    return {
        "message": "Product liked"
    }


@router.get("/")
def get_likes(db: Session = Depends(get_db)):
    return db.query(models.Like).all()