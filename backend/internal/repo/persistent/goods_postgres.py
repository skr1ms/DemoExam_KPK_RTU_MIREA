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
                search_words = search_lower.split()

                def is_gender_word(word: str) -> bool:
                    """Проверяет, является ли слово указанием пола"""
                    return word.startswith("муж") or word.startswith("жен")

                def get_gender_prefix(word: str) -> str:
                    """Получает префикс пола (первые 3-4 символа)"""
                    if word.startswith("муж"):
                        return "муж"
                    elif word.startswith("жен"):
                        return "жен"
                    return None

                if len(search_words) == 1:
                    word = search_words[0]
                    if is_gender_word(word):
                        prefix = get_gender_prefix(word)
                        query = query.filter(
                            or_(
                                func.lower(Good.name) == word,
                                func.lower(Good.category).ilike(f"%{prefix}%"),
                            )
                        )
                    else:
                        query = query.filter(
                            or_(
                                func.lower(Good.name) == word,
                                func.lower(Good.category).ilike(f"%{word}%"),
                            )
                        )
                else:
                    conditions = []

                    for name_word in search_words:
                        other_words = [w for w in search_words if w != name_word]
                        if other_words:
                            category_conditions = []
                            for cat_word in other_words:
                                if is_gender_word(cat_word):
                                    prefix = get_gender_prefix(cat_word)
                                    category_conditions.append(
                                        func.lower(Good.category).ilike(f"%{prefix}%")
                                    )
                                else:
                                    category_conditions.append(
                                        func.lower(Good.category).ilike(f"%{cat_word}%")
                                    )

                            conditions.append(
                                and_(
                                    func.lower(Good.name) == name_word,
                                    and_(*category_conditions),
                                )
                            )

                    if len(search_words) > 1:
                        all_category_conditions = []
                        for cat_word in search_words:
                            if is_gender_word(cat_word):
                                prefix = get_gender_prefix(cat_word)
                                all_category_conditions.append(
                                    func.lower(Good.category).ilike(f"%{prefix}%")
                                )
                            else:
                                all_category_conditions.append(
                                    func.lower(Good.category).ilike(f"%{cat_word}%")
                                )
                        conditions.append(and_(*all_category_conditions))

                    if conditions:
                        query = query.filter(or_(*conditions))
                    else:
                        query = query.filter(False)

            if provider:
                query = query.filter(Good.provider == provider)

            if sort_by_count == "asc":
                query = query.order_by(Good.count.asc(), Good.id.asc())
            elif sort_by_count == "desc":
                query = query.order_by(Good.count.desc(), Good.id.desc())

            result = await session.execute(query)
            goods = list(result.scalars().all())
            return goods
