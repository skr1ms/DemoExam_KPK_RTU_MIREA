"""
ORM модель для заказов
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from backend.pkg.postgres.postgres import Base


class Order(Base):
    __tablename__ = "Order"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("User.id", ondelete="SET NULL"), nullable=True)
    pick_up_point_id = Column(
        Integer,
        ForeignKey("Order_Pick_Up_Point.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )
    delivered_at = Column(DateTime, nullable=True)
    recipient_code = Column(String(50), nullable=True)
    status = Column(String(50), nullable=True)

    def __init__(
        self,
        user_id: int = None,
        pick_up_point_id: int = None,
        delivered_at=None,
        recipient_code: str = None,
        status: str = None,
    ):
        self.user_id = user_id
        self.pick_up_point_id = pick_up_point_id
        self.delivered_at = delivered_at
        self.recipient_code = recipient_code
        self.status = status
