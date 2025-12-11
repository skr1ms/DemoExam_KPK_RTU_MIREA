"""
Конфигурация приложения для подключения к базе данных
"""

import os
from dotenv import load_dotenv

load_dotenv()


class DatabaseConfig:
    """Конфигурация подключения к базе данных PostgreSQL"""

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Создать конфигурацию из переменных окружения"""
        return cls(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "shop_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
        )


class AppConfig:
    """Основная конфигурация приложения"""

    def __init__(self, database: DatabaseConfig):
        self.database = database

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Создать конфигурацию приложения из переменных окружения"""
        return cls(database=DatabaseConfig.from_env())


config = AppConfig.from_env()
