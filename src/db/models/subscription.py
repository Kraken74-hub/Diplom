from sqlalchemy import ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from src.db.base import Base

class Subscription(Base):
    """Таблица подписок (связывает пользователя и конкретный товар)"""
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    check_interval: Mapped[int] = mapped_column(Integer, default=3)        # Интервал проверки в часах (3, 6, 8)
    last_checked: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow) # Время последней проверки

    user = relationship("User", back_populates="subscriptions")
    product = relationship("Product", back_populates="subscriptions")