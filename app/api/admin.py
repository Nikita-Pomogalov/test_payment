from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.models.models import Admin, User, Account
from app.schemas.admin import AdminResponse
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.account import AccountResponse
from app.core.dependencies import get_current_admin
from app.services.admin_service import AdminService

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/me", response_model=AdminResponse)
async def get_me(
    current_admin: Admin = Depends(get_current_admin)
):
    """Получить данные о себе (админ)"""
    return current_admin

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Создать пользователя (только админ)"""
    service = AdminService(db)
    return await service.create_user(user_data)

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Получить список пользователей (только админ)"""
    service = AdminService(db)
    return await service.get_users(skip, limit)

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Получить пользователя по ID (только админ)"""
    service = AdminService(db)
    return await service.get_user(user_id)

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Обновить пользователя (только админ)"""
    service = AdminService(db)
    return await service.update_user(user_id, user_data)

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Удалить пользователя (только админ)"""
    service = AdminService(db)
    await service.delete_user(user_id)

@router.get("/users/{user_id}/accounts", response_model=List[AccountResponse])
async def get_user_accounts(
    user_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Получить счета пользователя (только админ)"""
    service = AdminService(db)
    return await service.get_user_accounts(user_id)