from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.models.models import User, Account
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.auth import get_password_hash


class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        """Создание пользователя админом"""
        result = await self.db.execute(
            select(User).where(User.email == user_data.email)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=True
        )

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        account = Account(
            user_id=new_user.id,
            balance=0.00
        )
        self.db.add(account)
        await self.db.commit()

        return new_user

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получить список пользователей"""
        result = await self.db.execute(
            select(User)
            .offset(skip)
            .limit(limit)
            .order_by(User.id)
        )
        return result.scalars().all()

    async def get_user(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Обновить пользователя"""
        user = await self.get_user(user_id)

        if user_data.email:
            result = await self.db.execute(
                select(User).where(
                    User.email == user_data.email,
                    User.id != user_id
                )
            )
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            user.email = user_data.email

        if user_data.full_name:
            user.full_name = user_data.full_name

        if user_data.password:
            user.hashed_password = get_password_hash(user_data.password)

        if user_data.is_active is not None:
            user.is_active = user_data.is_active

        user.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: int) -> None:
        """Удалить пользователя"""
        user = await self.get_user(user_id)
        await self.db.delete(user)
        await self.db.commit()

    async def get_user_accounts(self, user_id: int) -> List[Account]:
        """Получить счета пользователя"""
        await self.get_user(user_id)  # Проверяем, что пользователь существует

        result = await self.db.execute(
            select(Account).where(Account.user_id == user_id)
        )
        return result.scalars().all()