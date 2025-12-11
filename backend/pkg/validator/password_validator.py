"""
Валидатор для проверки паролей
"""

from typing import Tuple


class PasswordValidator:
    MIN_LENGTH = 6
    MAX_LENGTH = 50

    @staticmethod
    def validate(password: str) -> Tuple[bool, str]:
        """Валидация пароля"""
        if not password:
            return False, "Пароль не может быть пустым"

        if len(password) < PasswordValidator.MIN_LENGTH:
            return (
                False,
                f"Пароль должен содержать минимум {PasswordValidator.MIN_LENGTH} символов",
            )

        if len(password) > PasswordValidator.MAX_LENGTH:
            return (
                False,
                f"Пароль не должен превышать {PasswordValidator.MAX_LENGTH} символов",
            )

        return True, ""

    @staticmethod
    def validate_confirmation(password: str, confirm: str) -> Tuple[bool, str]:
        """Проверка совпадения пароля и подтверждения"""
        if password != confirm:
            return (
                False,
                "Пароли не совпадают. Убедитесь, что вы ввели одинаковые пароли в оба поля.",
            )

        return True, ""
