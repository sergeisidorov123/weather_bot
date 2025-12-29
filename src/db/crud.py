from src.db.models import Users
from src.db.dto import UserCreate
from src.db.setup_db import session_factory, Base, engine

def create_db():
    Base.metadata.create_all(bind=engine)

def insert_user(user_data: UserCreate):
    with session_factory() as session:
        user = Users(
            user_id=user_data.user_id,
            latitude=user_data.latitude,
            longitude=user_data.longitude,
            city=user_data.city,
        )
    session.add(user)
    session.commit()

def get_user_by_id(user_id: int):
    with session_factory() as session:
        user = session.query(Users).filter(Users.user_id == user_id).first()
        return user