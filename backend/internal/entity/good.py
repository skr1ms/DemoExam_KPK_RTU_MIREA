"""
ORM модель для товаров
"""

from sqlalchemy import Column, Integer, String, Numeric, Text
from backend.pkg.postgres.postgres import Base


class Good(Base):
    __tablename__ = "Goods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    article = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    unit_of_measurement = Column(String(10), nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    provider = Column(String(100), nullable=True)
    manufacturer = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)
    discount = Column(Numeric(5, 2), nullable=True)
    count = Column(Integer, nullable=False, default=0)
    description = Column(Text, nullable=True)
    image = Column(String(255), nullable=True)

    def __init__(
        self,
        article: str,
        name: str,
        unit_of_measurement: str,
        price: float,
        provider: str = None,
        manufacturer: str = None,
        category: str = None,
        discount: float = None,
        count: int = 0,
        description: str = None,
        image: str = None,
    ):
        self.article = article
        self.name = name
        self.unit_of_measurement = unit_of_measurement
        self.price = price
        self.provider = provider
        self.manufacturer = manufacturer
        self.category = category
        self.discount = discount
        self.count = count
        self.description = description
        self.image = image
