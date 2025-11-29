"""
Валидатор для проверки email адресов
"""

import re
from typing import Tuple


class EmailValidator:
    EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    @staticmethod
    def validate(email: str) -> Tuple[bool, str]:
        if not email:
            return False, "Логин не может быть пустым"

        email = email.strip()

        if not re.match(EmailValidator.EMAIL_PATTERN, email):
            return (
                False,
                "Логин должен быть корректным email адресом (например: user@example.com)",
            )

        return True, ""
