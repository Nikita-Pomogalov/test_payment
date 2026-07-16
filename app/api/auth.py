from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.models import User, Admin
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.auth import verify_password, create_access_token, create_refresh_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
        login_data: LoginRequest,
        db: AsyncSession = Depends(get_db)
):
    """Авторизация пользователя или администратора"""

    # Ищем сначала в пользователях
    result = await db.execute(
        select(User).where(User.email == login_data.email)
    )
    user = result.scalar_one_or_none()
    role = "user"

    # Если не нашли, ищем в админах
    if not user:
        result = await db.execute(
            select(Admin).where(Admin.email == login_data.email)
        )
        user = result.scalar_one_or_none()
        role = "admin"

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )

    # Создаем токены
    access_token = create_access_token(
        data={"sub": user.email, "role": role, "id": user.id}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email, "role": role, "id": user.id}
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )