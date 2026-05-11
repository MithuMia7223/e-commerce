from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

import models, schemas
from db import get_db
from oauth2 import verify_token
from auth import admin_required

router = APIRouter(prefix="/coupons", tags=["Coupons"])


# =========================
# CREATE COUPON (ADMIN ONLY)
# =========================
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_coupon(
    coupon: schemas.CouponCreate,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    db_coupon = models.Coupon(**coupon.dict())
    db.add(db_coupon)
    db.commit()
    db.refresh(db_coupon)
    return db_coupon


# =========================
# GET ALL COUPONS (ADMIN ONLY)
# =========================
@router.get("/", response_model=List[schemas.CouponOut])
def get_all_coupons(
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    coupons = db.query(models.Coupon).all()
    return coupons


# =========================
# GET ACTIVE COUPONS
# =========================
@router.get("/active", response_model=List[schemas.CouponOut])
def get_active_coupons(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    coupons = db.query(models.Coupon).filter(
        models.Coupon.is_active == True,
        models.Coupon.expires_at > datetime.now()
    ).all()
    return coupons


# =========================
# VALIDATE COUPON
# =========================
@router.post("/validate")
def validate_coupon(
    coupon_code: str,
    cart_total: float,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    coupon = db.query(models.Coupon).filter(
        models.Coupon.code == coupon_code,
        models.Coupon.is_active == True,
        models.Coupon.expires_at > datetime.now()
    ).first()
    
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired coupon"
        )
    
    # Check minimum amount requirement
    if cart_total < coupon.minimum_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Minimum order amount of ${coupon.minimum_amount} required"
        )
    
    # Check usage limit
    user_usage_count = db.query(models.CouponUsage).filter(
        models.CouponUsage.coupon_id == coupon.id,
        models.CouponUsage.user_id == user["id"]
    ).count()
    
    if coupon.usage_limit and user_usage_count >= coupon.usage_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon usage limit exceeded"
        )
    
    # Calculate discount
    if coupon.discount_type == "percentage":
        discount_amount = cart_total * (coupon.discount_value / 100)
    else:  # fixed amount
        discount_amount = min(coupon.discount_value, cart_total)
    
    return {
        "coupon": coupon,
        "discount_amount": discount_amount,
        "final_total": cart_total - discount_amount
    }


# =========================
# UPDATE COUPON (ADMIN ONLY)
# =========================
@router.put("/{coupon_id}", response_model=schemas.CouponOut)
def update_coupon(
    coupon_id: int,
    coupon_update: schemas.CouponCreate,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    coupon = db.query(models.Coupon).filter(models.Coupon.id == coupon_id).first()
    
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    for field, value in coupon_update.dict().items():
        setattr(coupon, field, value)
    
    db.commit()
    db.refresh(coupon)
    return coupon


# =========================
# DELETE COUPON (ADMIN ONLY)
# =========================
@router.delete("/{coupon_id}")
def delete_coupon(
    coupon_id: int,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    coupon = db.query(models.Coupon).filter(models.Coupon.id == coupon_id).first()
    
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    db.delete(coupon)
    db.commit()
    return {"message": "Coupon deleted successfully"}
