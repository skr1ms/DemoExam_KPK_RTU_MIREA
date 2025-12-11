"""
Сервисный слой для связи frontend с backend
"""

from frontend.services.auth_service import AuthService
from frontend.services.goods_service import GoodsService
from frontend.services.orders_service import OrdersService

__all__ = ["AuthService", "GoodsService", "OrdersService"]
