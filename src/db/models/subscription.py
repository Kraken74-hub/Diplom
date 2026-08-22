from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    check_interval: Mapped[int] = mapped_column(Integer, default=3)
    user = relationship("src.db.models.user.User", back_populates="subscriptions")
    product = relationship("src.db.models.product.Product", back_populates="subscriptions")