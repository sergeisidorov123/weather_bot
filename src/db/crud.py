from geopy import Nominatim
from aiogram import F
from src.db.models import Users
from src.db.setup_db import session_factory, Base, engine

def create_db():
    Base.metadata.create_all(bind=engine)

def insert_user(user_id: int, location: F.location):
    geolocator = Nominatim(user_agent='weather_bot')
    location = geolocator.reverse(f"{location.latitude}, {location.longitude}")
    print(location.raw)
    try:
        city = location.raw["address"]["city"]
    except KeyError:
        city = location.raw["address"]["village"]
    with session_factory() as session:
        user = Users(
            user_id=user_id,
            latitude=location.latitude,
            longitude=location.longitude,
            city=city
        )
    session.add(user)
    session.commit()

def get_user_by_id(user_id: int):
    with session_factory() as session:
        user = session.query(Users).filter(Users.user_id == user_id).first()
        return user