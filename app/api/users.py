from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.models import User, Account, Transaction
from app.schemas.user import UserResponse
from app.schemas.account import AccountResponse
from app.schemas.transaction import TransactionResponse
from app.core.dependencies import get_current_user_only

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user_only)
):
    """Получить данные о себе"""
    return current_user

@router.get("/me/accounts", response_model=List[AccountResponse])
async def get_my_accounts(
    current_user: User = Depends(get_current_user_only),
    db: AsyncSession = Depends(get_db)
):
    """Получить список своих счетов и балансов"""
    result = await db.execute(
        select(Account).where(Account.user_id == current_user.id)
    )
    return result.scalars().all()

@router.get("/me/transactions", response_model=List[TransactionResponse])
async def get_my_transactions(
    current_user: User = Depends(get_current_user_only),
    db: AsyncSession = Depends(get_db)
):
    """Получить список своих платежей"""
    result = await db.execute(
        select(Transaction).where(Transaction.user_id == current_user.id)
        .order_by(Transaction.created_at.desc())
    )
    return result.scalars().all()