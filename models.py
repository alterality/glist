from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    status = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'))
    guest_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    messages = relationship("Message", back_populates="room")
    owner = relationship("User", foreign_keys=[owner_id])
    guest = relationship("User", foreign_keys=[guest_id])
    
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    nickname = Column(String, index=True) 
    photo = Column(String)  
    status = Column(String)
    messages = relationship("Message", back_populates="user")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)

    user = relationship("User", back_populates="messages")
    room = relationship("Room", back_populates="messages")