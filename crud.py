from sqlalchemy.orm import Session
from models import User
from security import get_password_hash
from fastapi import HTTPException, status
import models
import security
import schemas
from security import verify_password

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    return user

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=fake_hashed_password,
        nickname=user.nickname,
        photo=user.photo,
        status=user.status
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        update_data = user_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

def create_room(db: Session, room: schemas.RoomCreate, owner_id: int):
    db_room = models.Room(**room.dict(), owner_id=owner_id)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

def get_room(db: Session, room_id: int):
    return db.query(models.Room).filter(models.Room.id == room_id).first()

def get_room_users(room_id: int, db: Session):
    room_users = db.query(models.RoomUser).filter(models.RoomUser.room_id == room_id).all()
    user_ids = [ru.user_id for ru in room_users]
    users = db.query(models.User).filter(models.User.id.in_(user_ids)).all()
    return users

def create_message(db: Session, message_data: schemas.MessageCreate, user_id: int, room_id: int):
    db_message = models.Message(**message_data.dict(), user_id=user_id, room_id=room_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_room_messages(db: Session, room_id: int):
    return db.query(models.Message).filter(models.Message.room_id == room_id).all()