"""
ORM модель для пользователей
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from backend.pkg.postgres.postgres import Base


class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String(32), nullable=False)
    full_name = Column(String(255), nullable=False)
    login = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )

    def __init__(self, role: str, full_name: str, login: str, password: str):
        self.role = role
        self.full_name = full_name
        self.login = login
        self.password = password
