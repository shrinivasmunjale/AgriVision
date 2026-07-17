from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.core.security import verify_token
from app.models.user import User

reusable_oauth2 = HTTPBearer()

async def get_token_payload(credentials: HTTPAuthorizationCredentials = Depends(reusable_oauth2)) -> dict:
    token = credentials.credentials
    return verify_token(token)

async def get_current_user(
    payload: dict = Depends(get_token_payload),
    db: AsyncSession = Depends(get_db)
) -> User:
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing user identifier (sub)."
        )
    
    # Query the user in the database
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User profile not registered in local database. Please complete registration."
        )
        
    return user

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Insufficient permissions."
            )
        return current_user

