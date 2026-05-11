from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

import models, schemas
from db import get_db
from oauth2 import verify_token
from auth import admin_required

router = APIRouter(prefix="/refunds", tags=["Refunds"])


# =========================
# CREATE REFUND REQUEST
# =========================
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_refund_request(
    refund: schemas.RefundCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    # Check if order exists and belongs to user
    order = db.query(models.Order).filter(
        models.Order.id == refund.order_id,
        models.Order.user_id == user["id"]
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if refund already exists for this order and product
    existing_refund = db.query(models.Refund).filter(
        models.Refund.order_id == refund.order_id,
        models.Refund.product_id == refund.product_id,
        models.Refund.user_id == user["id"]
    ).first()
    
    if existing_refund:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refund request already exists for this item"
        )
    
    db_refund = models.Refund(
        user_id=user["id"],
        **refund.dict()
    )
    db.add(db_refund)
    db.commit()
    db.refresh(db_refund)
    return db_refund


# =========================
# GET USER REFUNDS
# =========================
@router.get("/", response_model=List[schemas.RefundOut])
def get_user_refunds(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    refunds = db.query(models.Refund).filter(
        models.Refund.user_id == user["id"]
    ).all()
    return refunds


# =========================
# GET ALL REFUNDS (ADMIN ONLY)
# =========================
@router.get("/admin/all", response_model=List[schemas.RefundOut])
def get_all_refunds(
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    refunds = db.query(models.Refund).all()
    return refunds


# =========================
# APPROVE/REJECT REFUND (ADMIN ONLY)
# =========================
@router.put("/{refund_id}/status", response_model=schemas.RefundOut)
def update_refund_status(
    refund_id: int,
    status: str,  # approved or rejected
    refund_amount: float = None,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    refund = db.query(models.Refund).filter(
        models.Refund.id == refund_id
    ).first()
    
    if not refund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refund not found"
        )
    
    if status not in ["approved", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be 'approved' or 'rejected'"
        )
    
    refund.status = status
    
    if status == "approved":
        refund.refund_amount = refund_amount or refund.quantity * 100  # Default calculation
        refund.refund_date = datetime.now()
    
    db.commit()
    db.refresh(refund)
    return refund


# =========================
# GET REFUND DETAILS
# =========================
@router.get("/{refund_id}", response_model=schemas.RefundOut)
def get_refund_details(
    refund_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    refund = db.query(models.Refund).filter(
        models.Refund.id == refund_id,
        models.Refund.user_id == user["id"]
    ).first()
    
    if not refund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refund not found"
        )
    
    return refund
