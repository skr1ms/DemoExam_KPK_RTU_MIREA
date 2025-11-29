"""
Сервис для работы с товарами
"""

from backend.internal.usecase.goods_usecase import GoodsUseCase
from backend.internal.entity.good import Good
from backend.internal.entity.user import User
from typing import List, Optional


class GoodsService:
    def __init__(self, goods_usecase: GoodsUseCase):
        self.usecase = goods_usecase

    async def get_all_goods(self, user: Optional[User] = None) -> List[Good]:
        """Получить все товары"""
        return await self.usecase.get_all(user)

    async def get_good_by_id(self, id: int) -> Optional[Good]:
        """Получить товар по ID"""
        return await self.usecase.get_by_id(id)

    async def search_goods(self, query: str, user: Optional[User] = None) -> List[Good]:
        """Поиск товаров"""
        return await self.usecase.search(query, user)

    async def create_good(
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
        return await self.usecase.create(
            article,
            name,
            unit_of_measurement,
            price,
            provider,
            manufacturer,
            category,
            discount,
            count,
            description,
            image,
            user,
        )

    async def update_good(self, good: Good, user: Optional[User] = None) -> Good:
        """Обновить товар"""
        return await self.usecase.update(good, user)

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
        return await self.usecase.update_good_data(
            good_id,
            article,
            name,
            unit_of_measurement,
            price,
            provider,
            manufacturer,
            category,
            discount,
            count,
            description,
            image,
            user,
        )

    async def delete_good(self, id: int, user: Optional[User] = None) -> bool:
        """Удалить товар"""
        return await self.usecase.delete(id, user)

    async def get_all_providers(self) -> List[str]:
        """Получить список всех поставщиков"""
        return await self.usecase.get_all_providers()

    async def get_all_categories(self) -> List[str]:
        """Получить список всех категорий"""
        return await self.usecase.get_all_categories()

    async def get_all_manufacturers(self) -> List[str]:
        """Получить список всех производителей"""
        return await self.usecase.get_all_manufacturers()

    async def filter_and_sort(
        self,
        provider: Optional[str] = None,
        sort_by_count: Optional[str] = None,
        search_query: Optional[str] = None,
        user: Optional[User] = None,
    ) -> List[Good]:
        """Комбинированная фильтрация, поиск и сортировка товаров"""
        return await self.usecase.filter_and_sort(
            provider, sort_by_count, search_query, user
        )

    def calculate_price_with_discount(
        self, price: float, discount: Optional[float] = None
    ) -> float:
        """Рассчитать цену товара с учетом скидки"""
        return self.usecase.calculate_price_with_discount(price, discount)
