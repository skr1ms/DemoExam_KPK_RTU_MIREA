"""
Сервис для работы с заказами
"""

from backend.internal.usecase.orders_usecase import OrdersUseCase
from backend.internal.entity.order import Order
from backend.internal.entity.user import User
from typing import List, Optional, Dict
from datetime import datetime


class OrdersService:
    def __init__(self, orders_usecase: OrdersUseCase):
        self.usecase = orders_usecase

    async def get_all_orders(self, user: Optional[User] = None) -> List[Order]:
        """Получить все заказы"""
        return await self.usecase.get_all(user)

    async def get_order_by_id(self, id: int) -> Optional[Order]:
        """Получить заказ по ID"""
        return await self.usecase.get_by_id(id)

    async def get_user_orders(self, user_id: int) -> List[Order]:
        """Получить заказы по ID пользователя"""
        return await self.usecase.get_by_user(user_id)

    async def get_orders_for_user(self, user: Optional[User] = None) -> List[Order]:
        """Получить заказы для пользователя с учетом его роли"""
        return await self.usecase.get_orders_for_user(user)

    async def create_order(
        self,
        pick_up_point_id: Optional[int] = None,
        recipient_code: Optional[str] = None,
        items: List[Dict] = None,
        user: Optional[User] = None,
    ) -> Order:
        """Создать заказ"""
        return await self.usecase.create(pick_up_point_id, recipient_code, items, user)

    async def update_order_status(self, order_id: int, status: str) -> Optional[Order]:
        """Обновить статус заказа"""
        return await self.usecase.update_status(order_id, status)

    async def update_order(
        self, order: Order, user: Optional[User] = None
    ) -> Optional[Order]:
        """Обновить заказ"""
        return await self.usecase.update(order, user)

    async def delete_order(self, id: int, user: Optional[User] = None) -> bool:
        """Удалить заказ"""
        return await self.usecase.delete(id, user)

    async def update_order_data(
        self,
        order_id: int,
        status: Optional[str] = None,
        user_id: Optional[int] = None,
        pick_up_point_id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        delivered_at: Optional[datetime] = None,
        items: Optional[List[Dict]] = None,
        user: Optional[User] = None,
    ) -> Optional[Order]:
        """Обновить данные заказа (для администратора)"""
        return await self.usecase.update_order_data(
            order_id,
            status,
            user_id,
            pick_up_point_id,
            created_at,
            delivered_at,
            items,
            user,
        )

    async def create_order_for_admin(
        self,
        status: str,
        user_id: Optional[int] = None,
        pick_up_point_id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        delivered_at: Optional[datetime] = None,
        items: Optional[List[Dict]] = None,
        user: Optional[User] = None,
    ) -> Order:
        """Создать заказ администратором"""
        return await self.usecase.create_order_for_admin(
            status, user_id, pick_up_point_id, created_at, delivered_at, items, user
        )

    async def calculate_order_total(
        self, order_id: Optional[int] = None, items: Optional[List[Dict]] = None
    ) -> float:
        """Рассчитать итоговую сумму заказа"""
        return await self.usecase.calculate_order_total(order_id, items)

    async def get_all_pick_up_points(self):
        """Получить все пункты выдачи"""
        return await self.usecase.get_all_pick_up_points()
