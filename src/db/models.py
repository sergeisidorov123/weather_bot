from sqlalchemy import Column, Integer, String, Float
from src.db.setup_db import Base

class Users(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    latitude = Column(Float)
    longitude = Column(Float)
    city = Column(String, nullable=True)
