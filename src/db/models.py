from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, func, text, DateTime, Text, Float
from src.db.setup_db import Base

class Users(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    latitude = Column(Float)
    longitude = Column(Float)
    city = Column(String)
