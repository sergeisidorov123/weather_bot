from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from src.config import settings

engine = create_engine(
    url=settings.DATABASE_URL,
    echo=False
)

session_factory = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass
