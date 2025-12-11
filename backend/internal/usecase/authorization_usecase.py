"""
Use case для проверки прав доступа пользователей
"""

from backend.internal.entity.user import User
from typing import Optional


class PermissionError(Exception):
    """Исключение при отсутствии прав доступа"""

    pass


class AuthorizationUseCase:
    ROLE_GUEST = "Гость"
    ROLE_CLIENT = "Авторизированный клиент"
    ROLE_MANAGER = "Менеджер"
    ROLE_ADMIN = "Администратор"

    @staticmethod
    def can_view_goods(user: Optional[User] = None) -> bool:
        """Проверить право на просмотр товаров"""
        return True

    @staticmethod
    def can_search_filter_sort_goods(user: Optional[User] = None) -> bool:
        """Проверить право на поиск, фильтрацию и сортировку товаров"""
        if not user:
            return False
        return user.role in [
            AuthorizationUseCase.ROLE_MANAGER,
            AuthorizationUseCase.ROLE_ADMIN,
        ]

    @staticmethod
    def can_create_good(user: Optional[User] = None) -> bool:
        """Проверить право на создание товара"""
        if not user:
            return False
        return user.role == AuthorizationUseCase.ROLE_ADMIN

    @staticmethod
    def can_update_good(user: Optional[User] = None) -> bool:
        """Проверить право на редактирование товара"""
        if not user:
            return False
        return user.role == AuthorizationUseCase.ROLE_ADMIN

    @staticmethod
    def can_delete_good(user: Optional[User] = None) -> bool:
        """Проверить право на удаление товара"""
        if not user:
            return False
        return user.role == AuthorizationUseCase.ROLE_ADMIN

    @staticmethod
    def can_view_orders(user: Optional[User] = None) -> bool:
        """Проверить право на просмотр заказов"""
        if not user:
            return False
        return user.role in [
            AuthorizationUseCase.ROLE_MANAGER,
            AuthorizationUseCase.ROLE_ADMIN,
        ]

    @staticmethod
    def can_view_all_orders(user: Optional[User] = None) -> bool:
        """Проверить право на просмотр всех заказов (не только своих)"""
        if not user:
            return False
        return user.role in [
            AuthorizationUseCase.ROLE_MANAGER,
            AuthorizationUseCase.ROLE_ADMIN,
        ]

    @staticmethod
    def can_create_order(user: Optional[User] = None) -> bool:
        """Проверить право на создание заказа"""
        if not user:
            return False
        return user.role == AuthorizationUseCase.ROLE_ADMIN

    @staticmethod
    def can_update_order(user: Optional[User] = None) -> bool:
        """Проверить право на редактирование заказа"""
        if not user:
            return False
        return user.role == AuthorizationUseCase.ROLE_ADMIN

    @staticmethod
    def can_delete_order(user: Optional[User] = None) -> bool:
        """Проверить право на удаление заказа"""
        if not user:
            return False
        return user.role == AuthorizationUseCase.ROLE_ADMIN

    @staticmethod
    def require_user(
        user: Optional[User] = None, action: str = "выполнить действие"
    ) -> User:
        """Проверить, что пользователь авторизован"""
        if not user:
            raise PermissionError(f"Требуется авторизация для {action}")
        return user

    @staticmethod
    def require_admin(
        user: Optional[User] = None, action: str = "выполнить действие"
    ) -> User:
        """Проверить, что пользователь является администратором"""
        user = AuthorizationUseCase.require_user(user, action)
        if user.role != AuthorizationUseCase.ROLE_ADMIN:
            raise PermissionError(f"Только администратор может {action}")
        return user

    @staticmethod
    def require_manager_or_admin(
        user: Optional[User] = None, action: str = "выполнить действие"
    ) -> User:
        """Проверить, что пользователь является менеджером или администратором"""
        user = AuthorizationUseCase.require_user(user, action)
        if user.role not in [
            AuthorizationUseCase.ROLE_MANAGER,
            AuthorizationUseCase.ROLE_ADMIN,
        ]:
            raise PermissionError(f"Только менеджер или администратор может {action}")
        return user
