"""
Репозиторий для работы с товарами через PostgreSQL
"""

from backend.pkg.postgres.postgres import PG
from backend.internal.entity.good import Good
from sqlalchemy import select, or_, and_, func
from typing import List, Optional


class GoodsPostgres:
    def __init__(self, pg: PG):
        self.pg = pg

    async def create(self, good: Good) -> Good:
        """Создать товар"""
        async with self.pg.get_session() as session:
            session.add(good)
            await session.commit()
            await session.refresh(good)
            return good

    async def get(self, id: int) -> Optional[Good]:
        """Получить товар по ID"""
        async with self.pg.get_session() as session:
            result = await session.execute(select(Good).filter(Good.id == id))
            return result.scalar_one_or_none()

    async def get_all(self) -> List[Good]:
        """Получить все товары"""
        async with self.pg.get_session() as session:
            result = await session.execute(select(Good))
            return list(result.scalars().all())

    async def get_by_article(self, article: str) -> Optional[Good]:
        """Получить товар по артикулу"""
        async with self.pg.get_session() as session:
            result = await session.execute(select(Good).filter(Good.article == article))
            return result.scalar_one_or_none()

    async def update(self, good: Good) -> Good:
        """Обновить товар"""
        async with self.pg.get_session() as session:
            result = await session.execute(select(Good).filter(Good.id == good.id))
            db_good = result.scalar_one_or_none()

            if not db_good:
                raise ValueError(f"Товар с ID {good.id} не найден")

            db_good.article = good.article
            db_good.name = good.name
            db_good.unit_of_measurement = good.unit_of_measurement
            db_good.price = good.price
            db_good.count = good.count
            db_good.provider = good.provider
            db_good.manufacturer = good.manufacturer
            db_good.category = good.category
            db_good.discount = good.discount
            db_good.description = good.description
            db_good.image = good.image

            await session.commit()
            await session.refresh(db_good)
            return db_good

    async def delete(self, id: int) -> bool:
        """Удалить товар по ID"""
        async with self.pg.get_session() as session:
            good = await self.get(id)
            if good:
                await session.delete(good)
                await session.commit()
                return True
            return False

    async def search(self, query: str) -> List[Good]:
        """Поиск товаров по всем текстовым полям"""
        async with self.pg.get_session() as session:
            result = await session.execute(
                select(Good).filter(
                    (Good.name.ilike(f"%{query}%"))
                    | (Good.article.ilike(f"%{query}%"))
                    | (Good.description.ilike(f"%{query}%"))
                    | (Good.category.ilike(f"%{query}%"))
                    | (Good.manufacturer.ilike(f"%{query}%"))
                    | (Good.provider.ilike(f"%{query}%"))
                )
            )
            return list(result.scalars().all())

    async def filter_by_provider(self, provider: Optional[str] = None) -> List[Good]:
        """Фильтрация товаров по поставщику"""
        async with self.pg.get_session() as session:
            if provider:
                result = await session.execute(
                    select(Good).filter(Good.provider == provider)
                )
            else:
                result = await session.execute(select(Good))
            return list(result.scalars().all())

    async def get_all_providers(self) -> List[str]:
        """Получить список всех поставщиков"""
        async with self.pg.get_session() as session:
            result = await session.execute(
                select(Good.provider).distinct().filter(Good.provider.isnot(None))
            )
            return [row[0] for row in result.all() if row[0]]

    async def get_all_categories(self) -> List[str]:
        """Получить список всех категорий"""
        async with self.pg.get_session() as session:
            result = await session.execute(
                select(Good.category).distinct().filter(Good.category.isnot(None))
            )
            return [row[0] for row in result.all() if row[0]]

    async def get_all_manufacturers(self) -> List[str]:
        """Получить список всех производителей"""
        async with self.pg.get_session() as session:
            result = await session.execute(
                select(Good.manufacturer)
                .distinct()
                .filter(Good.manufacturer.isnot(None))
            )
            return [row[0] for row in result.all() if row[0]]

    async def filter_and_sort(
        self,
        provider: Optional[str] = None,
        sort_by_count: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> List[Good]:
        async with self.pg.get_session() as session:
            query = select(Good)

            if search_query:
                search_lower = search_query.strip().lower()
                words = search_lower.split()

                def is_gender_word(word: str) -> bool:
                    return word.startswith("муж") or word.startswith("жен")

                def get_gender_prefix(word: str) -> Optional[str]:
                    if word.startswith("муж"):
                        return "муж"
                    if word.startswith("жен"):
                        return "жен"
                    return None

                name_cat_conditions = []
                gender_conditions = []

                for w in words:
                    if is_gender_word(w):
                        prefix = get_gender_prefix(w)
                        gender_conditions.append(
                            func.lower(Good.category).ilike(f"%{prefix}%")
                        )
                    else:
                        name_cat_conditions.append(
                            or_(
                                func.lower(Good.name).ilike(f"%{w}%"),
                                func.lower(Good.category).ilike(f"%{w}%"),
                            )
                        )

                if name_cat_conditions:
                    query = query.filter(and_(*name_cat_conditions))

                if gender_conditions:
                    query = query.filter(and_(*gender_conditions))

            if provider:
                query = query.filter(Good.provider == provider)

            if sort_by_count == "asc":
                query = query.order_by(Good.count.asc(), Good.id.asc())
            elif sort_by_count == "desc":
                query = query.order_by(Good.count.desc(), Good.id.desc())

            result = await session.execute(query)
            return list(result.scalars().all())
