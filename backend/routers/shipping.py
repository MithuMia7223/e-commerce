from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from db import get_db
from oauth2 import verify_token

router = APIRouter(prefix="/shipping", tags=["Shipping Addresses"])


# =========================
# CREATE SHIPPING ADDRESS
# =========================
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_shipping_address(
    address: schemas.ShippingAddressCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    # If setting as default, unset other default addresses
    if address.is_default:
        db.query(models.ShippingAddress).filter(
            models.ShippingAddress.user_id == user["id"],
            models.ShippingAddress.is_default == True
        ).update({"is_default": False})
    
    db_address = models.ShippingAddress(
        user_id=user["id"],
        **address.dict()
    )
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address


# =========================
# GET USER SHIPPING ADDRESSES
# =========================
@router.get("/", response_model=List[schemas.ShippingAddressOut])
def get_shipping_addresses(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    addresses = db.query(models.ShippingAddress).filter(
        models.ShippingAddress.user_id == user["id"]
    ).all()
    return addresses


# =========================
# UPDATE SHIPPING ADDRESS
# =========================
@router.put("/{address_id}", response_model=schemas.ShippingAddressOut)
def update_shipping_address(
    address_id: int,
    address_update: schemas.ShippingAddressCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    address = db.query(models.ShippingAddress).filter(
        models.ShippingAddress.id == address_id,
        models.ShippingAddress.user_id == user["id"]
    ).first()
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipping address not found"
        )
    
    # If setting as default, unset other default addresses
    if address_update.is_default:
        db.query(models.ShippingAddress).filter(
            models.ShippingAddress.user_id == user["id"],
            models.ShippingAddress.is_default == True,
            models.ShippingAddress.id != address_id
        ).update({"is_default": False})
    
    for field, value in address_update.dict().items():
        setattr(address, field, value)
    
    db.commit()
    db.refresh(address)
    return address


# =========================
# DELETE SHIPPING ADDRESS
# =========================
@router.delete("/{address_id}")
def delete_shipping_address(
    address_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    address = db.query(models.ShippingAddress).filter(
        models.ShippingAddress.id == address_id,
        models.ShippingAddress.user_id == user["id"]
    ).first()
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipping address not found"
        )
    
    db.delete(address)
    db.commit()
    return {"message": "Shipping address deleted successfully"}
