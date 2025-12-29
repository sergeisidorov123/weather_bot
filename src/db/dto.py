from pydantic import BaseModel

class UserCreate(BaseModel):
    user_id: int
    longitude: float
    latitude: float
    city: str

