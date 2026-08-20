from sqlalchemy import BigInteger, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base

class Product(Base):
    """Таблица отслеживаемых товаров Wildberries"""
    __tablename__ = "products"

    class Product(Base):
        __tablename__ = "products"

        id: Mapped[int] = mapped_column(primary_key=True)
        nm_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
        title: Mapped[str] = mapped_column(String)
        current_price: Mapped[int | None] = mapped_column(Integer, nullable=True)
        image_url: Mapped[str | None] = mapped_column(String, nullable=True)

    # Связи с подписками и историей цен
    subscriptions = relationship("Subscription", back_populates="product")
    history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")