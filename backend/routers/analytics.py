from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

import models, schemas
from db import get_db
from oauth2 import verify_token

router = APIRouter(prefix="/analytics", tags=["Product Analytics"])


# =========================
# RECORD PRODUCT VIEW
# =========================
@router.post("/view/{product_id}")
def record_product_view(
    product_id: int,
    db: Session = Depends(get_db)
):
    # Get today's date
    today = datetime.now().date()
    
    # Find or create analytics record for today
    analytics = db.query(models.ProductAnalytics).filter(
        models.ProductAnalytics.product_id == product_id,
        models.ProductAnalytics.date >= today,
        models.ProductAnalytics.date < today + timedelta(days=1)
    ).first()
    
    if not analytics:
        analytics = models.ProductAnalytics(
            product_id=product_id,
            views=1,
            purchases=0,
            revenue=0,
            date=datetime.now()
        )
        db.add(analytics)
    else:
        analytics.views += 1
    
    db.commit()
    return {"message": "View recorded successfully"}


# =========================
# RECORD PRODUCT PURCHASE
# =========================
@router.post("/purchase/{product_id}")
def record_product_purchase(
    product_id: int,
    quantity: int,
    revenue: float,
    db: Session = Depends(get_db)
):
    # Get today's date
    today = datetime.now().date()
    
    # Find or create analytics record for today
    analytics = db.query(models.ProductAnalytics).filter(
        models.ProductAnalytics.product_id == product_id,
        models.ProductAnalytics.date >= today,
        models.ProductAnalytics.date < today + timedelta(days=1)
    ).first()
    
    if not analytics:
        analytics = models.ProductAnalytics(
            product_id=product_id,
            views=0,
            purchases=quantity,
            revenue=revenue,
            date=datetime.now()
        )
        db.add(analytics)
    else:
        analytics.purchases += quantity
        analytics.revenue += revenue
    
    db.commit()
    return {"message": "Purchase recorded successfully"}


# =========================
# GET PRODUCT ANALYTICS (VENDOR ONLY)
# =========================
@router.get("/product/{product_id}", response_model=List[schemas.ProductAnalyticsOut])
def get_product_analytics(
    product_id: int,
    days: int = 30,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    # Check if user is the vendor of the product
    product = db.query(models.Product).filter(
        models.Product.id == product_id,
        models.Product.vendor_id == user["id"]
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or you're not the vendor"
        )
    
    # Get analytics for the specified number of days
    start_date = datetime.now() - timedelta(days=days)
    
    analytics = db.query(models.ProductAnalytics).filter(
        models.ProductAnalytics.product_id == product_id,
        models.ProductAnalytics.date >= start_date
    ).order_by(models.ProductAnalytics.date.desc()).all()
    
    return analytics


# =========================
# GET VENDOR ANALYTICS SUMMARY
# =========================
@router.get("/vendor/summary")
def get_vendor_analytics_summary(
    days: int = 30,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    # Get all products for this vendor
    products = db.query(models.Product).filter(
        models.Product.vendor_id == user["id"]
    ).all()
    
    product_ids = [p.id for p in products]
    
    if not product_ids:
        return {
            "total_views": 0,
            "total_purchases": 0,
            "total_revenue": 0,
            "top_products": []
        }
    
    # Get analytics for the specified number of days
    start_date = datetime.now() - timedelta(days=days)
    
    analytics = db.query(models.ProductAnalytics).filter(
        models.ProductAnalytics.product_id.in_(product_ids),
        models.ProductAnalytics.date >= start_date
    ).all()
    
    # Calculate totals
    total_views = sum(a.views for a in analytics)
    total_purchases = sum(a.purchases for a in analytics)
    total_revenue = sum(a.revenue for a in analytics)
    
    # Get top products by revenue
    product_revenue = {}
    for a in analytics:
        if a.product_id not in product_revenue:
            product_revenue[a.product_id] = 0
        product_revenue[a.product_id] += a.revenue
    
    top_products = sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total_views": total_views,
        "total_purchases": total_purchases,
        "total_revenue": total_revenue,
        "top_products": top_products
    }


# =========================
# GET ADMIN ANALYTICS DASHBOARD
# =========================
@router.get("/admin/dashboard")
def get_admin_analytics_dashboard(
    days: int = 30,
    db: Session = Depends(get_db),
    admin=Depends(verify_token)  # This should be admin_required
):
    # Get analytics for the specified number of days
    start_date = datetime.now() - timedelta(days=days)
    
    analytics = db.query(models.ProductAnalytics).filter(
        models.ProductAnalytics.date >= start_date
    ).all()
    
    # Calculate totals
    total_views = sum(a.views for a in analytics)
    total_purchases = sum(a.purchases for a in analytics)
    total_revenue = sum(a.revenue for a in analytics)
    
    # Get top products by views and revenue
    product_views = {}
    product_revenue = {}
    
    for a in analytics:
        if a.product_id not in product_views:
            product_views[a.product_id] = 0
            product_revenue[a.product_id] = 0
        product_views[a.product_id] += a.views
        product_revenue[a.product_id] += a.revenue
    
    top_viewed = sorted(product_views.items(), key=lambda x: x[1], reverse=True)[:10]
    top_revenue = sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "total_views": total_views,
        "total_purchases": total_purchases,
        "total_revenue": total_revenue,
        "top_viewed_products": top_viewed,
        "top_revenue_products": top_revenue
    }
