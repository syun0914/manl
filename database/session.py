from config import DB_SETTING
from sqlalchemy import create_engine

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker


SQLALCHEMY_DATABASE_URL = 'mysql+asyncmy://{user}:{password}@{host}:{port}/{database}'.format(**DB_SETTING)
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, pool_recycle=3550, pool_pre_ping=True
)

async_session_factory = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
Base = declarative_base()


async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
	    yield session