from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.database.connection import get_db
from src.database.models import User
from src.routers.schemas.user import UserResponse, UserUpdate
from src.utils.security import get_current_user, require_admin

router = APIRouter(prefix="/users", tags=["Users"])


# ── Get current user (me) ─────────────────────────────────────────────────────

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    return current_user


# ── List all users (admin only) ───────────────────────────────────────────────

@router.get("/", response_model=List[UserResponse])
def get_all_users(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Return a paginated list of all users. Admin only."""
    return db.query(User).order_by(User.id).offset(offset).limit(limit).all()


# ── Get user by ID (admin only) ───────────────────────────────────────────────

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Return a single user by ID. Admin only."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# ── Update user (admin or own account) ───────────────────────────────────────

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a user's profile. Admins can update any user; users can only update themselves."""
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Only apply fields that were explicitly provided
    update_data = payload.model_dump(exclude_unset=True)

    # Non-admins cannot change their own role
    if current_user.role != "admin" and "role" in update_data:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot change your own role")

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


# ── Deactivate user (admin only) ──────────────────────────────────────────────

@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Deactivate a user account (soft delete). Admin only."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_active = False
    db.commit()
    return {"message": f"User '{user.username}' has been deactivated"}
