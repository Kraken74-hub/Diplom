from sqlalchemy import BigInteger, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from src.db.base import Base

class User(Base):
    """Таблица пользователей Telegram"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)  # Telegram ID
    username: Mapped[str | None] = mapped_column(String, nullable=True)     # Имя пользователя @username
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Связь "один-ко-многим" с подписками (при удалении юзера удаляются и подписки)
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")