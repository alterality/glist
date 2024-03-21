from pydantic import BaseModel

class RoomCreate(BaseModel):
    title: str
    status: str
    guest_id: int = None

class Room(BaseModel):
    id: int
    title: str
    status: str
    owner_id: int
    guest_id: int = None

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    nickname: str
    photo: str = None  
    status: str = None

class UserShow(UserBase):
    id: int
    is_active: bool
    nickname: str
    photo: str
    status: str

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    email: str | None = None
    nickname: str | None = None
    photo: str | None = None
    status: str | None = None