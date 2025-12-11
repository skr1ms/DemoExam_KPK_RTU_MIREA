"""
Репозиторий для работы с пользователями через PostgreSQL
"""

from backend.pkg.postgres.postgres import PG
from backend.internal.entity.user import User
from sqlalchemy import select
from typing import List, Optional


class UserPostgres:
    def __init__(self, pg: PG):
        self.pg = pg

    async def create(self, user: User) -> User:
        """Создать пользователя"""
        async with self.pg.get_session() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def get(self, id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        async with self.pg.get_session() as session:
            result = await session.execute(select(User).filter(User.id == id))
            return result.scalar_one_or_none()

    async def get_by_login(self, login: str) -> Optional[User]:
        """Получить пользователя по логину"""
        async with self.pg.get_session() as session:
            result = await session.execute(select(User).filter(User.login == login))
            return result.scalar_one_or_none()

    async def get_by_full_name(self, full_name: str) -> Optional[User]:
        """Получить пользователя по ФИО"""
        async with self.pg.get_session() as session:
            result = await session.execute(
                select(User).filter(User.full_name == full_name)
            )
            return result.scalar_one_or_none()

    async def get_all(self) -> List[User]:
        """Получить всех пользователей"""
        async with self.pg.get_session() as session:
            result = await session.execute(select(User))
            return list(result.scalars().all())

    async def update(self, user: User) -> User:
        """Обновить пользователя"""
        async with self.pg.get_session() as session:
            await session.merge(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def delete(self, id: int) -> bool:
        """Удалить пользователя по ID"""
        async with self.pg.get_session() as session:
            user = await self.get(id)
            if user:
                await session.delete(user)
                await session.commit()
                return True
            return False

    async def verify_password(self, user: User, password: str) -> bool:
        """Проверить пароль пользователя"""
        return user.password == password
