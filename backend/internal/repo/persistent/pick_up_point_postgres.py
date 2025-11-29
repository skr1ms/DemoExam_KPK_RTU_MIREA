"""
Репозиторий для работы с пунктами выдачи через PostgreSQL
"""

from backend.pkg.postgres.postgres import PG
from backend.internal.entity.order_pick_up_point import OrderPickUpPoint
from sqlalchemy import select
from typing import List, Optional


class PickUpPointPostgres:
    def __init__(self, pg: PG):
        self.pg = pg

    async def create(self, point: OrderPickUpPoint) -> OrderPickUpPoint:
        """Создать пункт выдачи"""
        async with self.pg.get_session() as session:
            session.add(point)
            await session.commit()
            await session.refresh(point)
            return point

    async def get(self, id: int) -> Optional[OrderPickUpPoint]:
        """Получить пункт выдачи по ID"""
        async with self.pg.get_session() as session:
            result = await session.execute(
                select(OrderPickUpPoint).filter(OrderPickUpPoint.id == id)
            )
            return result.scalar_one_or_none()

    async def get_all(self) -> List[OrderPickUpPoint]:
        """Получить все пункты выдачи"""
        async with self.pg.get_session() as session:
            result = await session.execute(select(OrderPickUpPoint))
            return list(result.scalars().all())

    async def update(self, point: OrderPickUpPoint) -> OrderPickUpPoint:
        """Обновить пункт выдачи"""
        async with self.pg.get_session() as session:
            await session.merge(point)
            await session.commit()
            await session.refresh(point)
            return point

    async def delete(self, id: int) -> bool:
        """Удалить пункт выдачи по ID"""
        async with self.pg.get_session() as session:
            point = await self.get(id)
            if point:
                await session.delete(point)
                await session.commit()
                return True
            return False
