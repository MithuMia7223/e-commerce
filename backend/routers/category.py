from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models, schemas
from db import get_db
from oauth2 import verify_token
from auth import admin_required

router = APIRouter(prefix="/categories", tags=["Categories"])


# =========================
# CREATE CATEGORY 🏷️ (ADMIN ONLY)
# =========================
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_category(
    data: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):

    existing = (
        db.query(models.Category).filter(models.Category.name == data.name).first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    category = models.Category(name=data.name)

    db.add(category)
    db.commit()
    db.refresh(category)

    return {"message": "Category created 🏷️", "category": category}


# =========================
# GET ALL CATEGORIES 📄
# =========================
@router.get("/")
def get_categories(db: Session = Depends(get_db)):

    categories = db.query(models.Category).all()

    return {"total": len(categories), "categories": categories}


# =========================
# GET PRODUCTS BY CATEGORY 📦
# =========================
@router.get("/{category_id}/products")
def get_products_by_category(category_id: int, db: Session = Depends(get_db)):

    category = (
        db.query(models.Category).filter(models.Category.id == category_id).first()
    )

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    products = (
        db.query(models.Product).filter(models.Product.category_id == category_id).all()
    )

    return {
        "category": category.name,
        "total_products": len(products),
        "products": products,
    }


# =========================
# UPDATE CATEGORY ✏️ (ADMIN ONLY)
# =========================
@router.put("/{category_id}")
def update_category(
    category_id: int,
    data: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
):

    category = (
        db.query(models.Category).filter(models.Category.id == category_id).first()
    )

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category.name = data.name

    db.commit()
    db.refresh(category)

    return {"message": "Category updated ✏️", "category": category}


# =========================
# DELETE CATEGORY ❌ (ADMIN ONLY)
# =========================
@router.delete("/{category_id}")
def delete_category(
    category_id: int, db: Session = Depends(get_db), admin=Depends(admin_required)
):

    category = (
        db.query(models.Category).filter(models.Category.id == category_id).first()
    )

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(category)
    db.commit()

    return {"message": "Category deleted ❌"}
