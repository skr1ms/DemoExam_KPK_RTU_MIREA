"""
Валидатор для проверки ФИО
"""

import re
from typing import Tuple


class FullNameValidator:
    NAME_PATTERN = r"^[а-яА-ЯёЁa-zA-Z-]+$"
    MIN_LENGTH = 3
    MIN_WORDS = 2

    @staticmethod
    def validate(full_name: str) -> Tuple[bool, str]:
        if not full_name:
            return False, "ФИО не может быть пустым"

        full_name = full_name.strip()

        if len(full_name) < FullNameValidator.MIN_LENGTH:
            return (
                False,
                f"ФИО должно содержать минимум {FullNameValidator.MIN_LENGTH} символа",
            )

        words = full_name.split()
        if len(words) < FullNameValidator.MIN_WORDS:
            return (
                False,
                "ФИО должно содержать минимум имя и фамилию (например: Иванов Иван)",
            )

        for word in words:
            if not re.match(FullNameValidator.NAME_PATTERN, word):
                return False, "ФИО должно содержать только буквы, дефисы и пробелы"

        return True, ""
