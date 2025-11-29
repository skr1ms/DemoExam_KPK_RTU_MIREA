"""
Репозитории для работы с БД
"""

from backend.internal.repo.persistent.goods_postgres import GoodsPostgres
from backend.internal.repo.persistent.user_postgres import UserPostgres
from backend.internal.repo.persistent.order_postgres import OrderPostgres
from backend.internal.repo.persistent.pick_up_point_postgres import PickUpPointPostgres

__all__ = ["GoodsPostgres", "UserPostgres", "OrderPostgres", "PickUpPointPostgres"]
