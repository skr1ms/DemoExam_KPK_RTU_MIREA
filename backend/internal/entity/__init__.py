"""
Пакет сущностей приложения
"""

from backend.internal.entity.good import Good
from backend.internal.entity.order import Order
from backend.internal.entity.order_item import OrderItem
from backend.internal.entity.order_pick_up_point import OrderPickUpPoint
from backend.internal.entity.user import User

__all__ = ["Good", "Order", "OrderItem", "OrderPickUpPoint", "User"]
