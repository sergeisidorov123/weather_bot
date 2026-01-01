from aiogram.types import Message
from geopy import Nominatim
from aiogram import F
from src.db.models import Users
from src.db.setup_db import session_factory, Base, engine


geolocator = Nominatim(user_agent='weather_bot')

def create_db():
    Base.metadata.create_all(bind=engine)

async def insert_user(user_id: int, location: F.location):
    location = geolocator.reverse(f"{location.latitude}, {location.longitude}")
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

async def city_change(user_id: int, city: Message):
    user = await get_user_by_id(user_id)
    location = geolocator.geocode(city.text)
    print(location)
    with session_factory() as session:
        if user:
            user.latitude = location.latitude
            user.longitude = location.longitude
            user.city = city.text
        else:
            user = Users(
                user_id=user_id,
                latitude=location.latitude,
                longitude=location.longitude,
                city=city.text
            )
    session.add(user)
    session.commit()

async def get_user_by_id(user_id: int):
    with session_factory() as session:
        user = session.query(Users).filter(Users.user_id == user_id).first()
        return user