from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from .. import schemas
from ..db import get_db

router = APIRouter(
    prefix="/comments",
    tags=["Comments"]
)


@router.post("/")
def create_comment(
    data: schemas.CommentCreate,
    db: Session = Depends(get_db)
):

    item = models.Comment(**data.dict())

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


@router.get("/")
def get_comments(db: Session = Depends(get_db)):
    return db.query(models.Comment).all()