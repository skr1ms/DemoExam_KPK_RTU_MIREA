"""
Класс для управления подключением к PostgreSQL через SQLAlchemy async
"""

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)
from sqlalchemy import text
from sqlalchemy.orm import declarative_base
from typing import Optional
from backend.confg.config import config

Base = declarative_base()


class PG:
    def __init__(
        self,
        host: str = config.database.host,
        port: int = config.database.port,
        database: str = config.database.database,
        user: str = config.database.user,
        password: str = config.database.password,
    ):
        self.connection_string = (
            f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"
        )
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker[AsyncSession]] = None

    async def connect(self) -> bool:
        try:
            self.engine = create_async_engine(
                self.connection_string,
                echo=False,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
            )

            self.session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False,
            )

            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))

            return True

        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            return False

    def get_session(self) -> AsyncSession:
        if self.session_factory is None:
            raise RuntimeError("БД не подключена. Вызовите connect() сначала")
        return self.session_factory()

    async def create_tables(self):
        if self.engine is None:
            raise RuntimeError("БД не подключена")

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self):
        if self.engine:
            await self.engine.dispose()
