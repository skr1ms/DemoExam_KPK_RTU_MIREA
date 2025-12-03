"""
Use case для авторизации пользователей
"""

from backend.internal.repo.persistent.user_postgres import UserPostgres
from backend.internal.entity.user import User
from backend.pkg.validator.email_validator import EmailValidator
from backend.pkg.validator.full_name_validator import FullNameValidator
from backend.pkg.validator.password_validator import PasswordValidator
from typing import Optional, List


class AuthUseCase:
    def __init__(self, user_repo: UserPostgres):
        self.user_repo = user_repo

    async def login(self, login: str, password: str) -> Optional[User]:
        """Авторизация пользователя"""
        user = await self.user_repo.get_by_login(login)
        if not user:
            return None

        if await self.user_repo.verify_password(user, password):
            return user

        return None

    async def register(
        self,
        login: str,
        password: str,
        full_name: str,
        role: str = "Авторизированный клиент",
    ) -> User:
        """Регистрация нового пользователя"""
        is_valid, error_msg = EmailValidator.validate(login)
        if not is_valid:
            raise ValueError(error_msg)

        is_valid, error_msg = FullNameValidator.validate(full_name)
        if not is_valid:
            raise ValueError(error_msg)

        is_valid, error_msg = PasswordValidator.validate(password)
        if not is_valid:
            raise ValueError(error_msg)

        existing_user = await self.user_repo.get_by_login(login)
        if existing_user:
            raise ValueError(f"Пользователь с логином '{login}' уже существует")

        user = User(role=role, full_name=full_name, login=login, password=password)

        return await self.user_repo.create(user)

    async def get_all_users(self) -> List[User]:
        """Получить всех пользователей"""
        return await self.user_repo.get_all()
