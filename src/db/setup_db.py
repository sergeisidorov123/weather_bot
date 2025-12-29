from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import relationship, declarative_base, DeclarativeBase, sessionmaker
from src.config import settings

engine = create_engine(
    url=settings.DATABASE_URL,
    echo=True
)

session_factory = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass
