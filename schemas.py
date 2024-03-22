from pydantic import BaseModel
from typing import Optional, List

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    user_id: int
    room_id: int

    class Config:
        orm_mode = True

class RoomCreate(BaseModel):
    title: str
    status: str

class Room(BaseModel):
    id: int
    title: str
    status: str
    owner_id: int
    guest_id: Optional[int] = None
    messages: List[Message] = []

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    nickname: str
    photo: Optional[str] = None
    status: Optional[str] = None

class UserShow(UserBase):
    id: int
    is_active: bool
    nickname: str
    photo: Optional[str]
    status: Optional[str]
    messages: List[Message] = []

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    email: Optional[str] = None
    nickname: Optional[str] = None
    photo: Optional[str] = None
    status: Optional[str] = None
