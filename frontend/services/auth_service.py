"""
Сервис для работы с авторизацией пользователей
"""

from backend.internal.usecase.auth_usecase import AuthUseCase
from backend.internal.entity.user import User
from typing import Optional, List


class AuthService:
    def __init__(self, auth_usecase: AuthUseCase):
        self.usecase = auth_usecase

    async def login(self, login: str, password: str) -> Optional[User]:
        """Вход в систему"""
        return await self.usecase.login(login, password)

    async def register(
        self,
        login: str,
        password: str,
        full_name: str,
        role: str = "Авторизированный клиент",
    ) -> User:
        """Регистрация нового пользователя"""
        return await self.usecase.register(login, password, full_name, role)

    async def get_all_users(self) -> List[User]:
        """Получить всех пользователей"""
        return await self.usecase.get_all_users()
