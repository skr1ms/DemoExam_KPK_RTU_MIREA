"""
Точка входа в приложение. Инициализирует backend и запускает GUI
"""

from backend.confg.config import config
from backend.pkg.postgres.postgres import PG
from PySide6.QtWidgets import QApplication
import sys
from frontend.utils.async_helper import close_loop, run_async_sync

# Backend: Repositories
from backend.internal.repo.persistent import (
    GoodsPostgres,
    UserPostgres,
    OrderPostgres,
    PickUpPointPostgres,
)

# Backend: Use Cases
from backend.internal.usecase import AuthUseCase, GoodsUseCase, OrdersUseCase

# Frontend: Services
from frontend.services import AuthService, GoodsService, OrdersService

# Frontend: Windows
from frontend.windows.login_window import LoginWindow
from frontend.windows.main_window import MainWindow


async def init_backend():
    """Инициализация backend компонентов"""
    # Подключение к БД
    db = PG(
        host=config.database.host,
        port=config.database.port,
        database=config.database.database,
        user=config.database.user,
        password=config.database.password,
    )

    if not await db.connect():
        print("Не удалось подключиться к БД")
        sys.exit(1)

    await db.create_tables()

    # Импорт данных из Excel файлов
    try:
        from schema.import_data import import_all_data

        await import_all_data()
    except Exception as e:
        print(f"Ошибка при импорте данных: {e}")

    # Создаем репозитории
    goods_repo = GoodsPostgres(db)
    user_repo = UserPostgres(db)
    order_repo = OrderPostgres(db)
    pick_up_repo = PickUpPointPostgres(db)

    # Создаем Use Cases
    auth_usecase = AuthUseCase(user_repo)
    goods_usecase = GoodsUseCase(goods_repo, order_repo)
    orders_usecase = OrdersUseCase(order_repo, goods_repo, pick_up_repo)

    # Создаем Services
    auth_service = AuthService(auth_usecase)
    goods_service = GoodsService(goods_usecase)
    orders_service = OrdersService(orders_usecase)

    return {
        "db": db,
        "auth_service": auth_service,
        "goods_service": goods_service,
        "orders_service": orders_service,
    }


# Глобальная переменная для хранения главного окна
_main_window = None


def show_main_window(user, services, login_window=None):
    """Показать главное окно после авторизации"""
    global _main_window
    try:

        def on_logout():
            """Обработка выхода - показываем окно входа"""
            global _main_window
            if login_window:
                login_window.show()
            _main_window = None

        _main_window = MainWindow(
            user=user,
            goods_service=services["goods_service"],
            orders_service=services["orders_service"],
            auth_service=services.get("auth_service"),
            on_logout=on_logout,
        )
        _main_window.show()
        return _main_window
    except Exception as e:
        print(f"Ошибка при создании главного окна: {e}")
        raise


def main():
    """Главная функция приложения"""
    services = run_async_sync(init_backend())

    # Создание Qt приложения
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Применяем глобальные стили для всех диалогов
    from frontend.utils.styles import STYLES

    app.setStyleSheet(STYLES.get("MESSAGEBOX_STYLE", ""))

    # Окно авторизации
    login_window = LoginWindow(
        auth_service=services["auth_service"],
        on_success=lambda user: show_main_window(user, services, login_window),
    )
    login_window.show()

    # Запуск приложения
    exit_code = app.exec()

    # Закрываем соединения с БД перед выходом
    try:
        if "db" in services:
            run_async_sync(services["db"].close())
    except Exception as e:
        print(f"Ошибка при закрытии БД: {e}")

    # Закрываем event loop
    close_loop()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
