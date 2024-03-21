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