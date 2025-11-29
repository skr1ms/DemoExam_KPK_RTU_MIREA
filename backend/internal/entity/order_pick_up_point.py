"""
ORM модель для пунктов выдачи заказов
"""

from sqlalchemy import Column, Integer, String
from backend.pkg.postgres.postgres import Base


class OrderPickUpPoint(Base):
    __tablename__ = "Order_Pick_Up_Point"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_address = Column(String(255), nullable=False)

    def __init__(self, full_address: str):
        self.full_address = full_address
