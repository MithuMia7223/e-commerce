from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import shutil
import os

import models, schemas
from db import get_db
from oauth2 import verify_token

router = APIRouter(prefix="/products", tags=["Products"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_token),
):

    new_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=getattr(product, "stock", 10),
        category=getattr(product, "category", None),
        vendor_id=user.id,
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {"message": "Product created", "product": new_product}


@router.post("/{product_id}/upload-image")
def upload_image(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(verify_token),
):

    product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.vendor_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    file_path = f"{UPLOAD_DIR}/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    product.image = file_path
    db.commit()

    return {"message": "Image uploaded", "image": file_path}


@router.get("/")
def get_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):

    products = db.query(models.Product).offset(skip).limit(limit).all()

    return products


@router.get("/search/{name}")
def search_product(name: str, db: Session = Depends(get_db)):

    return db.query(models.Product).filter(models.Product.name.contains(name)).all()


@router.put("/{id}")
def update_product(
    id: int,
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_token),
):

    item = db.query(models.Product).filter(models.Product.id == id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Product not found")

    if item.vendor_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    item.name = product.name
    item.description = product.description
    item.price = product.price
    item.stock = getattr(product, "stock", item.stock)
    item.category = getattr(product, "category", item.category)

    db.commit()
    db.refresh(item)

    return {"message": "Product updated", "product": item}


@router.delete("/{id}")
def delete_product(id: int, db: Session = Depends(get_db), user=Depends(verify_token)):

    item = db.query(models.Product).filter(models.Product.id == id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Product not found")

    if item.vendor_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    db.delete(item)
    db.commit()

    return {"message": "Product deleted"}


@router.post("/{id}/share")
def share_product(id: int, db: Session = Depends(get_db)):

    item = db.query(models.Product).filter(models.Product.id == id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Product not found")

    item.share_count = (item.share_count or 0) + 1
    db.commit()

    return {"message": "shared", "count": item.share_count}
