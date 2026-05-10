from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db
from ..oauth2 import verify_token

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/")
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):

    new_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=10,   # default stock
        vendor_id=user_id
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "message": "Product created",
        "product": {
            "id": new_product.id,
            "name": new_product.name,
            "price": new_product.price,
            "stock": new_product.stock,
            "category": new_product.category
        }
    }



@router.get("/")
def get_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "stock": p.stock,
            "category": p.category
        }
        for p in products
    ]
@router.get("/search/{name}")
def search_product(name: str, db: Session = Depends(get_db)):

    products = db.query(models.Product).filter(
        models.Product.name.contains(name)
    ).all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "stock": p.stock,
            "category": p.category
        }
        for p in products
    ]



@router.put("/{id}")
def update_product(
    id: int,
    product: schemas.ProductCreate,
    db: Session = Depends(get_db)
):

    item = db.query(models.Product).filter(models.Product.id == id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Product not found")

    item.name = product.name
    item.description = product.description
    item.price = product.price

    db.commit()
    db.refresh(item)

    return {"message": "Product updated", "product": item}



@router.delete("/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):

    item = db.query(models.Product).filter(models.Product.id == id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(item)
    db.commit()

    return {"message": "Product deleted"}


@router.post("/{id}/share")
def share_product(
    id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):

    item = db.query(models.Product).filter(models.Product.id == id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Product not found")

    item.share_count = (item.share_count or 0) + 1

    db.commit()
    db.refresh(item)

    return {
        "message": "Product shared",
        "share_count": item.share_count
    }