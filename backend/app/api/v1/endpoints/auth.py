from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timedelta
from typing import Optional

from app.db.session import get_db
from app.api.deps import get_token_payload, get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.core.security import create_access_token, verify_password, get_password_hash, verify_token
from app.core.config import settings
from pydantic import BaseModel, EmailStr, Field

router = APIRouter()

# --- Password management schemas ---
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=6)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user with email and password"""
    # Check if user already exists
    result = await db.execute(select(User).filter(User.email == user_in.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Determine role
    role = user_in.role if user_in.role else "farmer"
    
    # Create new user
    db_user = User(
        email=user_in.email,
        name=user_in.full_name or "",
        hashed_password=get_password_hash(user_in.password),
        role=role,
        farm_name=user_in.farm_name or "",
        phone=user_in.phone or ""
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
async def login(
    user_in: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login with email and password"""
    # Find user by email
    result = await db.execute(select(User).filter(User.email == user_in.email))
    user = result.scalars().first()
    
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/change-password")
async def change_password(
    user_in: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change the current user's password (requires the existing password)"""
    if not current_user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account does not have a local password set.",
        )
    if not verify_password(user_in.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )

    current_user.hashed_password = get_password_hash(user_in.new_password)
    await db.commit()
    await db.refresh(current_user)
    return {"message": "Password changed successfully."}

@router.post("/forgot-password")
async def forgot_password(
    user_in: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Request a password reset. Generates a short-lived token.

    NOTE: No email provider is configured, so for this demo the reset token
    is returned directly so the flow can be completed end-to-end. In production,
    email this token to the user instead of returning it.
    """
    result = await db.execute(select(User).filter(User.email == user_in.email))
    user = result.scalars().first()

    if not user:
        # Don't reveal whether an email exists
        return {
            "message": "If that email is registered, a reset link has been generated.",
            "reset_token": None,
        }

    reset_token = create_access_token(
        data={"sub": user.email, "purpose": "password_reset"},
        expires_delta=timedelta(minutes=30),
    )
    return {
        "message": "Password reset token generated. (Demo mode: no email provider configured.)",
        "reset_token": reset_token,
    }

@router.post("/reset-password")
async def reset_password(
    user_in: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Set a new password using a valid reset token."""
    try:
        payload = verify_token(user_in.token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token.",
        )

    if payload.get("purpose") != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token.",
        )

    email = payload.get("sub")
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    user.hashed_password = get_password_hash(user_in.new_password)
    await db.commit()
    return {"message": "Password updated successfully. You can now sign in."}
