from aiogram.types import Message
from geopy import Nominatim
from aiogram import F
from src.db.models import Users
from src.db.setup_db import session_factory, Base, engine
import asyncio

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

async def city_change_by_name(user_id: int, city_name: str):
    location = await asyncio.to_thread(geolocator.geocode, city_name)
    if not location:
        raise ValueError("City not found")

    with session_factory() as session:
        user = session.query(Users).filter(Users.user_id == user_id).first()
        if user:
            user.latitude = location.latitude
            user.longitude = location.longitude
            user.city = city_name
        else:
            user = Users(
                user_id=user_id,
                latitude=location.latitude,
                longitude=location.longitude,
                city=city_name
            )
        session.add(user)
        session.commit()

async def city_change_by_location(user_id: int, location_msg: Message):
    geo = geolocator.reverse(
        f"{location_msg.location.latitude}, {location_msg.location.longitude}"
    )

    city = (
        geo.raw["address"].get("city")
        or geo.raw["address"].get("village")
        or "Unknown"
    )

    with session_factory() as session:
        user = session.query(Users).filter(Users.user_id == user_id).first()
        if user:
            user.latitude = location_msg.location.latitude
            user.longitude = location_msg.location.longitude
            user.city = city
        else:
            user = Users(
                user_id=user_id,
                latitude=location_msg.location.latitude,
                longitude=location_msg.location.longitude,
                city=city
            )
        session.add(user)
        session.commit()


async def get_user_by_id(user_id: int):
    with session_factory() as session:
        user = session.query(Users).filter(Users.user_id == user_id).first()
        return user