"""
Скрипт для импорта данных из Excel файлов в базу данных
Проверяет наличие данных и импортирует только если таблицы пустые
"""

from backend.internal.entity.order_pick_up_point import OrderPickUpPoint
from backend.internal.entity.order import Order
from backend.internal.entity.good import Good
from backend.internal.entity.user import User
from backend.confg.config import config
from backend.pkg.postgres.postgres import PG
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path


root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


def excel_serial_to_date(serial_number):
    """Конвертирует Excel serial number в дату"""
    if pd.isna(serial_number):
        return None
    try:
        if isinstance(serial_number, datetime):
            return serial_number

        if isinstance(serial_number, pd.Timestamp):
            return serial_number.to_pydatetime()

        if isinstance(serial_number, str):
            if "30.02.2025" in serial_number or "30/02/2025" in serial_number:
                return datetime(2025, 2, 28)

            for fmt in ["%d.%m.%Y", "%m/%d/%y", "%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y"]:
                try:
                    return datetime.strptime(serial_number, fmt)
                except ValueError:
                    continue
            return None

        if isinstance(serial_number, (int, float)):
            excel_epoch = datetime(1899, 12, 30)
            return excel_epoch + timedelta(days=int(float(serial_number)))
        return None
    except (ValueError, TypeError):
        return None


async def check_table_empty(pg: PG, table_name: str) -> bool:
    """Проверяет, пуста ли таблица"""
    from sqlalchemy import text

    async with pg.get_session() as session:
        result = await session.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
        count = result.scalar()
        return count == 0


async def import_users(pg: PG, excel_file: str):
    """Импортирует пользователей из Excel"""
    if not await check_table_empty(pg, "User"):
        print("Таблица User уже содержит данные, пропускаем импорт")
        return

    print(f"Импорт пользователей из {excel_file}...")
    df = pd.read_excel(excel_file)

    role_col = None
    for col in df.columns:
        col_lower = str(col).lower()
        if "роль" in col_lower:
            role_col = col
            break

    fio_col = None
    for col in df.columns:
        col_lower = str(col).lower()
        if "фио" in col_lower or "полное имя" in col_lower or "имя" in col_lower:
            fio_col = col
            break

    login_col = None
    for col in df.columns:
        col_lower = str(col).lower()
        if (
            "логин" in col_lower
            or "login" in col_lower
            or "почта" in col_lower
            or "email" in col_lower
        ):
            login_col = col
            break

    password_col = None
    for col in df.columns:
        col_lower = str(col).lower()
        if "пароль" in col_lower or "password" in col_lower:
            password_col = col
            break

    from backend.internal.repo.persistent.user_postgres import UserPostgres

    user_repo = UserPostgres(pg)

    imported = 0
    for idx, row in df.iterrows():
        try:
            role = (
                str(row[role_col])
                if role_col and pd.notna(row.get(role_col))
                else "Авторизированный клиент"
            )
            full_name = (
                str(row[fio_col]) if fio_col and pd.notna(row.get(fio_col)) else ""
            )
            login = (
                str(row[login_col])
                if login_col and pd.notna(row.get(login_col))
                else ""
            )
            password = (
                str(row[password_col])
                if password_col and pd.notna(row.get(password_col))
                else ""
            )

            if not full_name or not login:
                print(f"Пропуск строки {idx + 2}: отсутствуют обязательные поля")
                continue

            user = User(role=role, full_name=full_name, login=login, password=password)
            await user_repo.create(user)
            imported += 1
        except Exception as e:
            print(f"Ошибка при импорте пользователя (строка {idx + 2}): {e}")

    print(f"Импортировано пользователей: {imported}")


def _parse_count(row, count_col, idx):
    """Парсит значение количества из строки Excel"""
    if not count_col:
        return 0
    try:
        value = row.get(count_col)
        if pd.isna(value):
            return 0
        count_str = str(value).strip()
        if not count_str or count_str == "" or count_str.lower() == "nan":
            return 0
        return int(float(count_str))
    except (ValueError, TypeError) as e:
        print(
            f"Ошибка при обработке количества для строки {idx + 2}: {row.get(count_col) if count_col else 'N/A'} -> {e}"
        )
        return 0


async def import_goods(pg: PG, excel_file: str):
    """Импортирует товары из Excel"""
    if not await check_table_empty(pg, "Goods"):
        print("Таблица Goods уже содержит данные, пропускаем импорт")
        return

    print(f"Импорт товаров из {excel_file}...")
    df = pd.read_excel(excel_file)

    def find_column(keywords):
        for col in df.columns:
            col_lower = str(col).lower()
            for keyword in keywords:
                if keyword.lower() in col_lower:
                    return col
        return None

    article_col = find_column(["артикул", "article"])
    name_col = find_column(["наименование", "название", "name", "имя", "товар"])
    unit_col = find_column(["единица", "unit", "измерения"])
    price_col = find_column(["цена", "price"])
    provider_col = find_column(["поставщик", "provider"])
    manufacturer_col = find_column(["производитель", "manufacturer"])
    category_col = find_column(["категория", "category"])
    discount_col = find_column(["скидка", "discount"])
    count_col = find_column(
        ["количество", "count", "quantity", "кол-во", "склад", "на складе"]
    )
    description_col = find_column(["описание", "description"])
    image_col = find_column(["изображение", "image", "фото", "photo"])

    if not name_col:
        print(
            "ВНИМАНИЕ: Колонка с названием товара не найдена! Проверьте названия колонок в Excel."
        )

    from backend.internal.repo.persistent.goods_postgres import GoodsPostgres

    goods_repo = GoodsPostgres(pg)

    imported = 0
    for idx, row in df.iterrows():
        try:
            article = (
                str(row[article_col])
                if article_col and pd.notna(row.get(article_col))
                else ""
            )
            name = (
                str(row[name_col]) if name_col and pd.notna(row.get(name_col)) else ""
            )
            unit = (
                str(row[unit_col]) if unit_col and pd.notna(row.get(unit_col)) else "шт"
            )
            price = (
                float(row[price_col])
                if price_col and pd.notna(row.get(price_col))
                else 0.0
            )

            if not article:
                print(f"Пропуск строки {idx + 2}: отсутствует артикул")
                continue

            count_value = _parse_count(row, count_col, idx)

            good = Good(
                article=article,
                name=name if name else f"Товар {article}",
                unit_of_measurement=unit,
                price=price,
                provider=str(row[provider_col])
                if provider_col and pd.notna(row.get(provider_col))
                else None,
                manufacturer=str(row[manufacturer_col])
                if manufacturer_col and pd.notna(row.get(manufacturer_col))
                else None,
                category=str(row[category_col])
                if category_col and pd.notna(row.get(category_col))
                else None,
                discount=float(row[discount_col])
                if discount_col and pd.notna(row.get(discount_col))
                else None,
                count=count_value,
                description=str(row[description_col])
                if description_col and pd.notna(row.get(description_col))
                else None,
                image=str(row[image_col])
                if image_col and pd.notna(row.get(image_col))
                else None,
            )
            await goods_repo.create(good)
            imported += 1
        except Exception as e:
            print(f"Ошибка при импорте товара (строка {idx + 2}): {e}")

    print(f"Импортировано товаров: {imported}")


async def import_pick_up_points(pg: PG, excel_file: str):
    """Импортирует пункты выдачи из Excel"""
    if not await check_table_empty(pg, "Order_Pick_Up_Point"):
        print("Таблица Order_Pick_Up_Point уже содержит данные, пропускаем импорт")
        return

    print(f"Импорт пунктов выдачи из {excel_file}...")
    df = pd.read_excel(excel_file)

    address_col = None
    for col in df.columns:
        col_lower = str(col).lower()
        if (
            "адрес" in col_lower
            or "address" in col_lower
            or "полный адрес" in col_lower
            or "full_address" in col_lower
        ):
            address_col = col
            break
    if not address_col:
        if "id" in df.columns or "ID" in df.columns or "Id" in df.columns:
            cols = list(df.columns)
            if len(cols) > 1:
                address_col = cols[1]
        else:
            address_col = df.columns[0]

    from backend.internal.repo.persistent.pick_up_point_postgres import (
        PickUpPointPostgres,
    )

    pick_up_repo = PickUpPointPostgres(pg)

    imported = 0
    for idx, row in df.iterrows():
        try:
            address = (
                str(row[address_col])
                if address_col and pd.notna(row.get(address_col))
                else ""
            )
            if not address or address.strip() == "":
                print(f"Пропуск строки {idx + 2}: пустой адрес")
                continue
            point = OrderPickUpPoint(full_address=address)
            await pick_up_repo.create(point)
            imported += 1
        except Exception as e:
            print(f"Ошибка при импорте пункта выдачи (строка {idx + 2}): {e}")

    print(f"Импортировано пунктов выдачи: {imported}")


async def import_orders(pg: PG, excel_file: str):
    """Импортирует заказы из Excel"""
    if not await check_table_empty(pg, "Order"):
        print("Таблица Order уже содержит данные, пропускаем импорт")
        return

    if not await check_table_empty(pg, "Order_Items"):
        print("Очистка таблицы Order_Items...")
        from sqlalchemy import text

        async with pg.get_session() as session:
            await session.execute(text('DELETE FROM "Order_Items"'))
            await session.commit()

    print(f"Импорт заказов из {excel_file}...")
    df = pd.read_excel(excel_file)

    from backend.internal.repo.persistent.order_postgres import OrderPostgres
    from backend.internal.repo.persistent.user_postgres import UserPostgres
    from backend.internal.repo.persistent.pick_up_point_postgres import (
        PickUpPointPostgres,
    )
    from backend.internal.repo.persistent.goods_postgres import GoodsPostgres
    from backend.internal.entity.order_item import OrderItem

    order_repo = OrderPostgres(pg)
    user_repo = UserPostgres(pg)
    pick_up_repo = PickUpPointPostgres(pg)
    goods_repo = GoodsPostgres(pg)

    imported = 0
    for idx, row in df.iterrows():
        try:
            created_at = None
            if pd.notna(row.get("Дата заказа")):
                created_at = excel_serial_to_date(row.get("Дата заказа"))
                if created_at and created_at.year == 2025 and created_at.month == 11:
                    if imported > 0:
                        prev_order = await order_repo.get_all()
                        if prev_order:
                            prev_date = prev_order[-1].created_at
                            if prev_date:
                                created_at = prev_date + timedelta(days=14)
                    if not created_at or (
                        created_at.year == 2025 and created_at.month == 11
                    ):
                        created_at = datetime(2025, 3, 15)
            delivered_at = None
            if pd.notna(row.get("Дата доставки")):
                delivered_at = excel_serial_to_date(row.get("Дата доставки"))

            user_id = None
            recipient_full_name = (
                str(row.get("ФИО авторизированного клиента", ""))
                if pd.notna(row.get("ФИО авторизированного клиента"))
                else None
            )
            if recipient_full_name:
                user = await user_repo.get_by_full_name(recipient_full_name)
                if user:
                    user_id = user.id
                else:
                    print(
                        f"Предупреждение: пользователь с ФИО '{recipient_full_name}' не найден (строка {idx + 2})"
                    )

            pick_up_point_id = None
            address_col = None
            for col in df.columns:
                col_lower = str(col).lower()
                if "адрес" in col_lower and (
                    "пункт" in col_lower or "выдач" in col_lower
                ):
                    address_col = col
                    break
            if not address_col:
                for col in df.columns:
                    col_lower = str(col).lower()
                    if "адрес" in col_lower:
                        address_col = col
                        break

            if address_col and pd.notna(row.get(address_col)):
                value = row.get(address_col)
                try:
                    pick_up_point_id = int(float(str(value)))
                    point = await pick_up_repo.get(pick_up_point_id)
                    if not point:
                        print(
                            f"Предупреждение: пункт выдачи с ID {pick_up_point_id} не найден (строка {idx + 2})"
                        )
                        pick_up_point_id = None
                except (ValueError, TypeError):
                    address = str(value).strip()
                    if address:
                        all_points = await pick_up_repo.get_all()
                        address_normalized = address.strip().lower()
                        for point in all_points:
                            if point.full_address.strip().lower() == address_normalized:
                                pick_up_point_id = point.id
                                break
                        if not pick_up_point_id:
                            print(
                                f"Предупреждение: пункт выдачи с адресом '{address}' не найден (строка {idx + 2})"
                            )
                            print(
                                f"  Доступные пункты выдачи: {[p.full_address for p in all_points[:5]]}"
                            )
            else:
                print(
                    f"Предупреждение: адрес пункта выдачи не найден в строке {idx + 2}, доступные колонки: {list(df.columns)}"
                )

            order = Order(
                user_id=user_id,
                pick_up_point_id=pick_up_point_id,
                delivered_at=delivered_at,
                recipient_code=str(row.get("Код для получения", ""))
                if pd.notna(row.get("Код для получения"))
                else None,
                status=str(row.get("Статус заказа", "новый"))
                if pd.notna(row.get("Статус заказа"))
                else "новый",
            )

            if created_at:
                order.created_at = created_at

            created_order = await order_repo.create(order)

            articles_str = (
                str(row.get("Артикул заказа", ""))
                if pd.notna(row.get("Артикул заказа"))
                else ""
            )
            if articles_str and articles_str.strip():
                parts = [p.strip() for p in articles_str.split(",")]
                if len(parts) % 2 != 0:
                    print(
                        f"Предупреждение: нечетное количество элементов в артикулах заказа (строка {idx + 2}): {articles_str}"
                    )

                for i in range(0, len(parts) - 1, 2):
                    if i + 1 < len(parts):
                        article = parts[i].strip()
                        try:
                            quantity = int(parts[i + 1].strip())
                            if quantity <= 0:
                                print(
                                    f"Предупреждение: некорректное количество для артикула {article}: {quantity}"
                                )
                                continue

                            good = await goods_repo.get_by_article(article)
                            if good:
                                order_item = OrderItem(
                                    order_id=created_order.id,
                                    goods_id=good.id,
                                    quantity=quantity,
                                )
                                await order_repo.add_order_item(order_item)
                            else:
                                print(
                                    f"Предупреждение: товар с артикулом '{article}' не найден (заказ ID: {created_order.id})"
                                )
                        except (ValueError, IndexError) as e:
                            print(
                                f"Ошибка при парсинге артикула '{article}' в заказе ID {created_order.id}: {e}"
                            )

            imported += 1
        except Exception as e:
            print(f"Ошибка при импорте заказа: {e}")

    print(f"Импортировано заказов: {imported}")


async def import_all_data():
    """Импортирует все данные из Excel файлов"""
    pg = PG(
        host=config.database.host,
        port=config.database.port,
        database=config.database.database,
        user=config.database.user,
        password=config.database.password,
    )

    if not await pg.connect():
        print("Не удалось подключиться к БД")
        return

    print("Начало импорта данных из Excel файлов...")
    print("=" * 50)

    base_path = root_dir / "schema" / "data_for_import"

    users_file = base_path / "Пользователи.xlsx"
    if users_file.exists():
        await import_users(pg, str(users_file))
    else:
        print(f"Файл не найден: {users_file}")

    goods_file = base_path / "Товары.xlsx"
    if goods_file.exists():
        await import_goods(pg, str(goods_file))
    else:
        print(f"Файл не найден: {goods_file}")

    pick_up_file = base_path / "Пункты выдачи.xlsx"
    if pick_up_file.exists():
        await import_pick_up_points(pg, str(pick_up_file))
    else:
        print(f"Файл не найден: {pick_up_file}")

    orders_file = base_path / "Заказы.xlsx"
    if orders_file.exists():
        await import_orders(pg, str(orders_file))
    else:
        print(f"Файл не найден: {orders_file}")

    print("=" * 50)
    print("Импорт данных завершен!")

    await pg.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(import_all_data())
