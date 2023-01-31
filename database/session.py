from config import DB_SETTING
from sqlalchemy import create_engine

from sqlalchemy.orm import declarative_base, sessionmaker


SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'.format(**DB_SETTING)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


async def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()