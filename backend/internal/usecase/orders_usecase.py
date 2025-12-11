"""
Use case для работы с заказами
"""

from backend.internal.repo.persistent.order_postgres import OrderPostgres
from backend.internal.repo.persistent.goods_postgres import GoodsPostgres
from backend.internal.repo.persistent.pick_up_point_postgres import PickUpPointPostgres
from backend.internal.entity.order import Order
from backend.internal.entity.order_item import OrderItem
from backend.internal.entity.user import User
from backend.internal.entity.order_pick_up_point import OrderPickUpPoint
from backend.internal.usecase.authorization_usecase import (
    AuthorizationUseCase,
    PermissionError,
)
from typing import List, Optional, Dict
from datetime import datetime


class OrdersUseCase:
    def __init__(
        self,
        order_repo: OrderPostgres,
        goods_repo: GoodsPostgres,
        pick_up_repo: Optional[PickUpPointPostgres] = None,
    ):
        self.order_repo = order_repo
        self.goods_repo = goods_repo
        self.pick_up_repo = pick_up_repo

    async def get_all(self, user: Optional[User] = None) -> List[Order]:
        """Получить все заказы"""
        if not AuthorizationUseCase.can_view_all_orders(user):
            raise PermissionError(
                "Только менеджер или администратор может просматривать все заказы"
            )
        return await self.order_repo.get_all()

    async def get_by_id(self, id: int) -> Optional[Order]:
        """Получить заказ по ID"""
        return await self.order_repo.get(id)

    async def get_by_user(self, user_id: int) -> List[Order]:
        """Получить заказы по ID пользователя"""
        return await self.order_repo.get_by_user(user_id)

    async def get_orders_for_user(self, user: Optional[User] = None) -> List[Order]:
        """Получить заказы для пользователя с учетом его роли"""
        if not user:
            raise PermissionError("Требуется авторизация для просмотра заказов")

        if AuthorizationUseCase.can_view_all_orders(user):
            return await self.get_all(user)
        elif AuthorizationUseCase.can_view_orders(user):
            return await self.get_by_user(user.id)
        else:
            raise PermissionError("У вас нет прав на просмотр заказов")

    async def create(
        self,
        pick_up_point_id: Optional[int] = None,
        recipient_code: Optional[str] = None,
        items: List[Dict] = None,
        user: Optional[User] = None,
    ) -> Order:
        """Создать заказ с товарами"""
        if user:
            if not AuthorizationUseCase.can_create_order(user):
                raise PermissionError(
                    "Только клиент или администратор может создавать заказы"
                )

        if not items:
            raise ValueError("Заказ должен содержать хотя бы один товар")

        for item in items:
            goods_id = item["goods_id"]
            quantity = item["quantity"]

            if quantity <= 0:
                raise ValueError("Количество товара должно быть больше 0")

            good = await self.goods_repo.get(goods_id)
            if not good:
                raise ValueError(f"Товар с ID {goods_id} не найден")

            if good.count < quantity:
                raise ValueError(
                    f"Недостаточно товара '{good.name}'. В наличии: {good.count}, запрошено: {quantity}"
                )

        order = Order(
            user_id=user.id if user else None,
            pick_up_point_id=pick_up_point_id,
            recipient_code=recipient_code,
            status="новый",
        )

        created_order = await self.order_repo.create(order)

        for item in items:
            order_item = OrderItem(
                order_id=created_order.id,
                goods_id=item["goods_id"],
                quantity=item["quantity"],
            )
            await self.order_repo.add_order_item(order_item)

        return created_order

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
        AuthorizationUseCase.require_admin(user, "создавать заказы")

        order = Order(user_id=user_id, pick_up_point_id=pick_up_point_id, status=status)

        if created_at:
            order.created_at = created_at
        if delivered_at:
            order.delivered_at = delivered_at

        created_order = await self.order_repo.create(order)

        if items:
            for item in items:
                order_item = OrderItem(
                    order_id=created_order.id,
                    goods_id=item["goods_id"],
                    quantity=item["quantity"],
                )
                await self.order_repo.add_order_item(order_item)

        return created_order

    async def calculate_order_total(
        self, order_id: Optional[int] = None, items: Optional[List[Dict]] = None
    ) -> float:
        """Рассчитать итоговую сумму заказа"""
        total = 0.0

        if order_id:
            order_items = await self.order_repo.get_order_items(order_id)
            for order_item in order_items:
                good = await self.goods_repo.get(order_item.goods_id)
                if not good:
                    continue
                price = float(good.price)
                if good.discount:
                    price = price * (1 - float(good.discount) / 100)
                total += price * order_item.quantity
        elif items:
            for item in items:
                goods_id = item["goods_id"]
                quantity = item["quantity"]

                if quantity <= 0:
                    raise ValueError("Количество товара должно быть больше 0")

                good = await self.goods_repo.get(goods_id)
                if not good:
                    raise ValueError(f"Товар с ID {goods_id} не найден")

                price = float(good.price)
                if good.discount:
                    price = price * (1 - float(good.discount) / 100)

                total += price * quantity

        return total

    async def get_all_pick_up_points(self) -> List[OrderPickUpPoint]:
        """Получить все пункты выдачи"""
        if not self.pick_up_repo:
            from backend.internal.repo.persistent.pick_up_point_postgres import (
                PickUpPointPostgres,
            )

            pick_up_repo = PickUpPointPostgres(self.order_repo.pg)
            return await pick_up_repo.get_all()
        return await self.pick_up_repo.get_all()

    async def update_status(self, order_id: int, status: str) -> Optional[Order]:
        """Обновить статус заказа"""
        order = await self.order_repo.get(order_id)
        if not order:
            return None
        order.status = status
        return await self.order_repo.update(order)

    async def update(
        self, order: Order, user: Optional[User] = None
    ) -> Optional[Order]:
        """Обновить заказ"""
        AuthorizationUseCase.require_admin(user, "редактировать заказы")
        return await self.order_repo.update(order)

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
        """Обновить данные заказа"""
        AuthorizationUseCase.require_admin(user, "редактировать заказы")

        order = await self.order_repo.get(order_id)
        if not order:
            raise ValueError(f"Заказ с ID {order_id} не найден")
        if status is not None:
            order.status = status
        if user_id is not None:
            order.user_id = user_id
        if pick_up_point_id is not None:
            order.pick_up_point_id = pick_up_point_id
        if created_at is not None:
            order.created_at = created_at
        if delivered_at is not None:
            order.delivered_at = delivered_at

        if items is not None:
            await self.order_repo.delete_order_items(order_id)
            for item in items:
                order_item = OrderItem(
                    order_id=order_id,
                    goods_id=item["goods_id"],
                    quantity=item["quantity"],
                )
                await self.order_repo.add_order_item(order_item)

        return await self.order_repo.update(order)

    async def delete(self, id: int, user: Optional[User] = None) -> bool:
        """Удалить заказ"""
        AuthorizationUseCase.require_admin(user, "удалять заказы")
        return await self.order_repo.delete(id)
