from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..auth import admin_required
from .. import models

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db), admin=Depends(admin_required)):
    total_users = db.query(models.User).count()
    total_products = db.query(models.Product).count()
    total_orders = db.query(models.Order).count()
    total_sales = (
        db.query(models.Order).filter(models.Order.payment_status == "paid").count()
    )

    return {
        "total_users": total_users,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_sales": total_sales,
    }


@router.get("/users")
def get_all_users(db: Session = Depends(get_db), admin=Depends(admin_required)):
    users = db.query(models.User).all()
    return users


@router.get("/orders")
def get_all_orders(db: Session = Depends(get_db), admin=Depends(admin_required)):
    from sqlalchemy.orm import joinedload

    orders = db.query(models.Order).options(joinedload(models.Order.items)).all()
    return orders
