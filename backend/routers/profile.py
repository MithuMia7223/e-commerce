from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models, schemas
from db import get_db
from oauth2 import verify_token

router = APIRouter(prefix="/profile", tags=["User Profile"])


# =========================
# CREATE/UPDATE USER PROFILE
# =========================
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user_profile(
    profile: schemas.UserProfileCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    # Check if profile already exists
    existing_profile = db.query(models.UserProfile).filter(
        models.UserProfile.user_id == user["id"]
    ).first()
    
    if existing_profile:
        # Update existing profile
        for field, value in profile.dict().items():
            if value is not None:
                setattr(existing_profile, field, value)
        
        db.commit()
        db.refresh(existing_profile)
        return existing_profile
    else:
        # Create new profile
        db_profile = models.UserProfile(
            user_id=user["id"],
            **profile.dict()
        )
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile


# =========================
# GET USER PROFILE
# =========================
@router.get("/", response_model=schemas.UserProfileOut)
def get_user_profile(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    profile = db.query(models.UserProfile).filter(
        models.UserProfile.user_id == user["id"]
    ).first()
    
    if not profile:
        # Create empty profile if it doesn't exist
        profile = models.UserProfile(user_id=user["id"])
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return profile


# =========================
# UPDATE USER PROFILE
# =========================
@router.put("/", response_model=schemas.UserProfileOut)
def update_user_profile(
    profile_update: schemas.UserProfileCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    profile = db.query(models.UserProfile).filter(
        models.UserProfile.user_id == user["id"]
    ).first()
    
    if not profile:
        # Create profile if it doesn't exist
        profile = models.UserProfile(user_id=user["id"])
        db.add(profile)
    
    # Update fields
    for field, value in profile_update.dict().items():
        if value is not None:
            setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    return profile


# =========================
# DELETE USER PROFILE
# =========================
@router.delete("/")
def delete_user_profile(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    profile = db.query(models.UserProfile).filter(
        models.UserProfile.user_id == user["id"]
    ).first()
    
    if profile:
        db.delete(profile)
        db.commit()
    
    return {"message": "User profile deleted successfully"}
