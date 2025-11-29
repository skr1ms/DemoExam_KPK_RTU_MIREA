"""
ORM модель для элементов заказа (связь многие-ко-многим между Order и Goods)
"""

from sqlalchemy import Column, Integer, ForeignKey
from backend.pkg.postgres.postgres import Base


class OrderItem(Base):
    __tablename__ = "Order_Items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(
        Integer, ForeignKey("Order.id", ondelete="CASCADE"), nullable=False
    )
    goods_id = Column(
        Integer, ForeignKey("Goods.id", ondelete="CASCADE"), nullable=False
    )
    quantity = Column(Integer, nullable=False)

    def __init__(self, order_id: int, goods_id: int, quantity: int):
        self.order_id = order_id
        self.goods_id = goods_id
        self.quantity = quantity
