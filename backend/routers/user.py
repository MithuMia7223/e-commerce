from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt

from .. import models, schemas, auth

from ..db import get_db
from ..oauth2 import verify_token

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if user.email:
        existing_email = (
            db.query(models.User).filter(models.User.email == user.email).first()
        )
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
    existing_username = (
        db.query(models.User).filter(models.User.username == user.username).first()
    )
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = auth.hash_password(user.password)

    new_user = models.User(
        username=user.username, email=user.email, password=hashed_password, role="user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role,
        },
    }


@router.post("/login")
def login(data: schemas.LoginSchema, db: Session = Depends(get_db)):
    user = (
        db.query(models.User)
        .filter(
            (models.User.email == data.username_or_email)
            | (models.User.username == data.username_or_email)
        )
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not auth.verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = auth.create_access_token({"user_id": user.id})
    refresh_token = auth.create_refresh_token({"user_id": user.id})
    return {
        "access_token": token,
        "refresh_token": refresh_token,
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
    data: schemas.UserUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token),
):

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if new username or email is already taken by another user
    if data.username != user.username:
        existing_user = (
            db.query(models.User).filter(models.User.username == data.username).first()
        )
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")

    if data.email != user.email:
        existing_email = (
            db.query(models.User).filter(models.User.email == data.email).first()
        )
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already taken")

    user.username = data.username
    user.email = data.email

    db.commit()
    db.refresh(user)

    return {
        "message": "Settings updated successfully",
        "user": {"id": user.id, "username": user.username, "email": user.email},
    }


@router.put("/role/{user_id}")
def update_user_role(
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
    return {"message": f"User role updated to {role}"}


@router.get("/profile")
def get_profile(db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at,
    }
