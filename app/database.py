from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.orm import declarative_base
from typing import Optional

from app.config import settings

Base = declarative_base()


class Database:
    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._sessionmaker: Optional[async_sessionmaker] = None

    async def connect(self):
        self._engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DB_ECHO,
            pool_size=10,
            max_overflow=20
        )
        self._sessionmaker = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def disconnect(self):
        if self._engine:
            await self._engine.dispose()

    def get_session(self) -> AsyncSession:
        if not self._sessionmaker:
            raise RuntimeError("Database not connected")
        return self._sessionmaker()


db = Database()


async def get_db() -> AsyncSession:
    """Dependency for getting database session"""
    async with db.get_session() as session:
        yield session