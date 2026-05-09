import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from .. import schemas
from ..db import get_db
from ..oauth2 import verify_token
from ..websocket import manager

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/")
def create_notification(
    notification: schemas.NotificationCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    if notification.user_id != user_id:
        raise HTTPException(status_code=403, detail="You can only create notifications for yourself.")

    item = models.Notification(**notification.dict())

    db.add(item)
    db.commit()
    db.refresh(item)

    asyncio.create_task(manager.broadcast(f"New notification: {notification.message}"))

    return item


@router.get("/")
def get_notifications(db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    return db.query(models.Notification).filter(models.Notification.user_id == user_id).all()
