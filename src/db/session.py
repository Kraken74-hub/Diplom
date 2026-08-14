from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config.settings import settings

# Асинхронный движок SQLAlchemy для работы с PostgreSQL через asyncpg
engine = create_async_engine(settings.DB_URL, echo=False)

# Фабрика для создания асинхронных сессий базы данных
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)