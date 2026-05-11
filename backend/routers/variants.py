from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from db import get_db
from oauth2 import verify_token
from auth import admin_required

router = APIRouter(prefix="/variants", tags=["Product Variants"])


# =========================
# CREATE PRODUCT VARIANT
# =========================
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_product_variant(
    variant: schemas.ProductVariantCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    # Check if product exists and user is the vendor
    product = db.query(models.Product).filter(
        models.Product.id == variant.product_id,
        models.Product.vendor_id == user["id"]
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or you're not the vendor"
        )
    
    db_variant = models.ProductVariant(**variant.dict())
    db.add(db_variant)
    db.commit()
    db.refresh(db_variant)
    return db_variant


# =========================
# GET PRODUCT VARIANTS
# =========================
@router.get("/product/{product_id}", response_model=List[schemas.ProductVariantOut])
def get_product_variants(
    product_id: int,
    db: Session = Depends(get_db)
):
    variants = db.query(models.ProductVariant).filter(
        models.ProductVariant.product_id == product_id
    ).all()
    return variants


# =========================
# UPDATE PRODUCT VARIANT
# =========================
@router.put("/{variant_id}", response_model=schemas.ProductVariantOut)
def update_product_variant(
    variant_id: int,
    variant_update: schemas.ProductVariantCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    variant = db.query(models.ProductVariant).filter(
        models.ProductVariant.id == variant_id
    ).first()
    
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product variant not found"
        )
    
    # Check if user is the vendor of the product
    product = db.query(models.Product).filter(
        models.Product.id == variant.product_id,
        models.Product.vendor_id == user["id"]
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You're not authorized to update this variant"
        )
    
    for field, value in variant_update.dict().items():
        setattr(variant, field, value)
    
    db.commit()
    db.refresh(variant)
    return variant


# =========================
# DELETE PRODUCT VARIANT
# =========================
@router.delete("/{variant_id}")
def delete_product_variant(
    variant_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    variant = db.query(models.ProductVariant).filter(
        models.ProductVariant.id == variant_id
    ).first()
    
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product variant not found"
        )
    
    # Check if user is the vendor of the product
    product = db.query(models.Product).filter(
        models.Product.id == variant.product_id,
        models.Product.vendor_id == user["id"]
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You're not authorized to delete this variant"
        )
    
    db.delete(variant)
    db.commit()
    return {"message": "Product variant deleted successfully"}
