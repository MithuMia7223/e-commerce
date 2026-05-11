from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt

import models, schemas, auth

from db import get_db
from oauth2 import verify_token

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", status_code=201)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    existing_user = (
        db.query(models.User)
        .filter(
            (models.User.username == user.username) | (models.User.email == user.email)
        )
        .first()
    )

    if existing_user:
        raise HTTPException(status_code=400, detail="Username or Email already exists")

    hashed_password = auth.hash_password(user.password)

    new_user = models.User(
        username=user.username, email=user.email, password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully"}


@router.post("/login")
def login(data: schemas.LoginSchema, db: Session = Depends(get_db)):

    user = (
        db.query(models.User)
        .filter(
            (models.User.username == data.username_or_email)
            | (models.User.email == data.username_or_email)
        )
        .first()
    )

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not auth.verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = auth.create_access_token(data={"user_id": user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        },
    }


@router.post("/refresh")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(
            refresh_token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM]
        )
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        new_access_token = auth.create_access_token({"user_id": user.id})
        return {"access_token": new_access_token, "token_type": "bearer"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.put("/settings")
def update_settings(
    data: schemas.UserUpdate, db: Session = Depends(get_db), user=Depends(verify_token)
):

    if data.username:
        user.username = data.username

    if data.email:
        user.email = data.email

    db.commit()
    db.refresh(user)

    return {
        "message": "Settings updated",
        "user": {"id": user.id, "username": user.username, "email": user.email},
    }


@router.put("/role/{user_id}")
def update_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    admin=Depends(auth.admin_required),
):

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = role
    db.commit()

    return {"message": f"Role updated to {role}"}


@router.get("/profile")
def get_profile(db: Session = Depends(get_db), user=Depends(verify_token)):

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at,
    }
