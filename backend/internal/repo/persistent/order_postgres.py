"""
Репозиторий для работы с заказами через PostgreSQL
"""

from backend.pkg.postgres.postgres import PG
from backend.internal.entity.order import Order
from backend.internal.entity.order_item import OrderItem
from sqlalchemy import select, delete
from typing import List


class OrderPostgres:
    def __init__(self, pg: PG):
        self.pg = pg

    async def create(self, order: Order) -> Order:
        """Создать заказ"""
        async with self.pg.get_session() as session:
            session.add(order)
            await session.commit()
            await session.refresh(order)
            return order

    async def get(self, id: int) -> Order | None:
        """Получить заказ по ID"""
        async with self.pg.get_session() as session:
            result = await session.execute(select(Order).filter(Order.id == id))
            return result.scalar_one_or_none()

    async def update(self, order: Order) -> Order:
        """Обновить заказ"""
        async with self.pg.get_session() as session:
            result = await session.execute(select(Order).filter(Order.id == order.id))
            db_order = result.scalar_one_or_none()

            if not db_order:
                raise ValueError(f"Заказ с ID {order.id} не найден")

            if hasattr(order, "status") and order.status is not None:
                db_order.status = order.status
            if hasattr(order, "created_at") and order.created_at is not None:
                db_order.created_at = order.created_at
            if hasattr(order, "delivered_at"):
                db_order.delivered_at = order.delivered_at
            if hasattr(order, "recipient_code") and order.recipient_code is not None:
                db_order.recipient_code = order.recipient_code
            if hasattr(order, "user_id") and order.user_id is not None:
                db_order.user_id = order.user_id
            if (
                hasattr(order, "pick_up_point_id")
                and order.pick_up_point_id is not None
            ):
                db_order.pick_up_point_id = order.pick_up_point_id

            await session.commit()
            await session.refresh(db_order)
            return db_order

    async def get_all(self) -> List[Order]:
        """Получить все заказы"""
        async with self.pg.get_session() as session:
            result = await session.execute(select(Order))
            return list(result.scalars().all())

    async def get_by_user(self, user_id: int) -> List[Order]:
        """Получить заказы по ID пользователя"""
        async with self.pg.get_session() as session:
            result = await session.execute(
                select(Order).filter(Order.user_id == user_id)
            )
            return list(result.scalars().all())

    async def delete(self, id: int) -> bool:
        """Удалить заказ по ID"""
        async with self.pg.get_session() as session:
            order = await self.get(id)
            if order:
                await session.delete(order)
                await session.commit()
                return True
            return False

    async def is_good_in_orders(self, goods_id: int) -> bool:
        """Проверить, используется ли товар в каких-либо заказах"""
        async with self.pg.get_session() as session:
            result = await session.execute(
                select(OrderItem).filter(OrderItem.goods_id == goods_id)
            )
            return result.scalar_one_or_none() is not None

    async def get_order_items(self, order_id: int) -> List[OrderItem]:
        """Получить все товары в заказе"""
        async with self.pg.get_session() as session:
            result = await session.execute(
                select(OrderItem).filter(OrderItem.order_id == order_id)
            )
            return list(result.scalars().all())

    async def add_order_item(self, order_item: OrderItem) -> OrderItem:
        """Добавить товар в заказ"""
        async with self.pg.get_session() as session:
            session.add(order_item)
            await session.commit()
            await session.refresh(order_item)
            return order_item

    async def delete_order_items(self, order_id: int) -> None:
        """Удалить все товары из заказа"""
        async with self.pg.get_session() as session:
            await session.execute(
                delete(OrderItem).filter(OrderItem.order_id == order_id)
            )
            await session.commit()
