"""
Use case для работы с товарами
"""

from backend.internal.repo.persistent.goods_postgres import GoodsPostgres
from backend.internal.repo.persistent.order_postgres import OrderPostgres
from backend.internal.entity.good import Good
from backend.internal.entity.user import User
from backend.internal.usecase.authorization_usecase import (
    AuthorizationUseCase,
    PermissionError,
)
from typing import List, Optional


class GoodsUseCase:
    def __init__(self, goods_repo: GoodsPostgres, order_repo: OrderPostgres = None):
        self.goods_repo = goods_repo
        self.order_repo = order_repo

    async def get_all(self, user: Optional[User] = None) -> List[Good]:
        """Получить все товары"""
        return await self.goods_repo.get_all()

    async def get_by_id(self, id: int) -> Optional[Good]:
        """Получить товар по ID"""
        return await self.goods_repo.get(id)

    async def get_by_article(self, article: str) -> Optional[Good]:
        """Получить товар по артикулу"""
        return await self.goods_repo.get_by_article(article)

    async def search(self, query: str, user: Optional[User] = None) -> List[Good]:
        """Поиск товаров"""
        if not AuthorizationUseCase.can_search_filter_sort_goods(user):
            raise PermissionError(
                "Только менеджер или администратор может выполнять поиск товаров"
            )
        if not query or not query.strip():
            return await self.get_all()
        return await self.goods_repo.search(query)

    async def create(
        self,
        article: str,
        name: str,
        unit_of_measurement: str,
        price: float,
        provider: str = None,
        manufacturer: str = None,
        category: str = None,
        discount: float = None,
        count: int = 0,
        description: str = None,
        image: str = None,
        user: Optional[User] = None,
    ) -> Good:
        """Создать товар"""
        AuthorizationUseCase.require_admin(user, "создавать товары")

        if not article or not article.strip():
            raise ValueError("Артикул товара не может быть пустым")
        if not name or not name.strip():
            raise ValueError("Название товара не может быть пустым")
        if not unit_of_measurement or not unit_of_measurement.strip():
            raise ValueError("Единица измерения не может быть пустой")
        if price < 0:
            raise ValueError("Стоимость товара не может быть отрицательной")
        if count < 0:
            raise ValueError("Количество товара не может быть отрицательным")

        existing = await self.goods_repo.get_by_article(article)
        if existing:
            raise ValueError(f"Товар с артикулом '{article}' уже существует")

        good = Good(
            article=article,
            name=name,
            unit_of_measurement=unit_of_measurement,
            price=price,
            provider=provider,
            manufacturer=manufacturer,
            category=category,
            discount=discount,
            count=count,
            description=description,
            image=image,
        )

        return await self.goods_repo.create(good)

    async def update(self, good: Good, user: Optional[User] = None) -> Good:
        """Обновить товар"""
        AuthorizationUseCase.require_admin(user, "редактировать товары")

        if not good.article or not good.article.strip():
            raise ValueError("Артикул товара не может быть пустым")
        if not good.name or not good.name.strip():
            raise ValueError("Название товара не может быть пустым")
        if not good.unit_of_measurement or not good.unit_of_measurement.strip():
            raise ValueError("Единица измерения не может быть пустой")
        if float(good.price) < 0:
            raise ValueError("Стоимость товара не может быть отрицательной")
        if good.count < 0:
            raise ValueError("Количество товара не может быть отрицательным")

        return await self.goods_repo.update(good)

    async def update_good_data(
        self,
        good_id: int,
        article: str,
        name: str,
        unit_of_measurement: str,
        price: float,
        provider: Optional[str] = None,
        manufacturer: Optional[str] = None,
        category: Optional[str] = None,
        discount: Optional[float] = None,
        count: int = 0,
        description: Optional[str] = None,
        image: Optional[str] = None,
        user: Optional[User] = None,
    ) -> Good:
        """Обновить данные товара по ID"""
        AuthorizationUseCase.require_admin(user, "редактировать товары")

        good = await self.goods_repo.get(good_id)
        if not good:
            raise ValueError(f"Товар с ID {good_id} не найден")

        good.article = article
        good.name = name
        good.unit_of_measurement = unit_of_measurement
        good.price = price
        good.provider = provider
        good.manufacturer = manufacturer
        good.category = category
        good.discount = discount
        good.count = count
        good.description = description
        if image is not None:
            good.image = image

        return await self.update(good, user)

    async def delete(self, id: int, user: Optional[User] = None) -> bool:
        """Удалить товар"""
        AuthorizationUseCase.require_admin(user, "удалять товары")
        if self.order_repo:
            is_in_orders = await self.order_repo.is_good_in_orders(id)
            if is_in_orders:
                raise ValueError("Товар, который присутствует в заказе, удалить нельзя")
        return await self.goods_repo.delete(id)

    async def update_count(self, id: int, new_count: int) -> Optional[Good]:
        """Обновить количество товара"""
        good = await self.goods_repo.get(id)
        if not good:
            return None

        good.count = new_count
        return await self.goods_repo.update(good)

    async def get_all_providers(self) -> List[str]:
        """Получить список всех поставщиков"""
        return await self.goods_repo.get_all_providers()

    async def get_all_categories(self) -> List[str]:
        """Получить список всех категорий"""
        return await self.goods_repo.get_all_categories()

    async def get_all_manufacturers(self) -> List[str]:
        """Получить список всех производителей"""
        return await self.goods_repo.get_all_manufacturers()

    def calculate_price_with_discount(
        self, price: float, discount: Optional[float] = None
    ) -> float:
        """Рассчитать цену товара с учетом скидки"""
        if discount and discount > 0:
            return price * (1 - float(discount) / 100)
        return float(price)

    async def filter_and_sort(
        self,
        provider: Optional[str] = None,
        sort_by_count: Optional[str] = None,
        search_query: Optional[str] = None,
        user: Optional[User] = None,
    ) -> List[Good]:
        """Комбинированная фильтрация, поиск и сортировка товаров"""
        if not AuthorizationUseCase.can_search_filter_sort_goods(user):
            raise PermissionError(
                "Только менеджер или администратор может фильтровать и сортировать товары"
            )
        return await self.goods_repo.filter_and_sort(
            provider, sort_by_count, search_query
        )
