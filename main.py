from fastapi import FastAPI, Depends, HTTPException, status, WebSocket
from sqlalchemy.orm import Session
import models, schemas, crud, security, database
from database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from starlette.websockets import WebSocketDisconnect
import openai
from threading import Timer
import asyncio

openai.api_key = ''
active_connections: dict[int, list[WebSocket]] = {}

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.UserShow)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(security.oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email = security.verify_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
@app.get("/users/{user_id}", response_model=schemas.UserShow)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/users/{user_id}", response_model=schemas.UserShow)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = crud.update_user(db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/users/{user_id}", response_model=schemas.UserShow)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.delete_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/rooms/", response_model=schemas.Room)
def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db), current_user: int = 1): 
    return crud.create_room(db=db, room=room, owner_id=current_user)

@app.websocket("/ws/rooms/{room_id}")

async def websocket_endpoint(websocket: WebSocket, room_id: int):
    await connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_text()
            for connection in active_connections[room_id]:
                await connection.send_text(f"Message from room {room_id}: {data}")
    except WebSocketDisconnect:
        disconnect(websocket, room_id)
    finally:
        disconnect(websocket, room_id)


async def connect(websocket: WebSocket, room_id: int):
    await websocket.accept()
    if room_id not in active_connections:
        active_connections[room_id] = []
    active_connections[room_id].append(websocket)

def disconnect(websocket: WebSocket, room_id: int):
    if room_id in active_connections:
        active_connections[room_id].remove(websocket)
        if not active_connections[room_id]:
            del active_connections[room_id]


def generate_task():
    response = openai.Completion.create(
        engine="davinci",
        prompt="Создайте задачу на Python для практики алгоритмов.",
        temperature=0.7,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].text.strip()

room_ready_state: dict[int, list[int]] = {}

def all_ready(room_id: int, db: Session) -> bool:
    room_users = crud.get_room_users(room_id, db)
    ready_users = room_ready_state.get(room_id, [])
    
    return all(user.id in ready_users for user in room_users)

room_ready_state = {}
@app.post("/rooms/{room_id}/ready")
async def mark_ready(room_id: int, db: Session = Depends(get_db), current_user: schemas.UserBase = Depends(get_current_user)):
    if not room_id in room_ready_state:
        room_ready_state[room_id] = []
    if current_user.id not in room_ready_state[room_id]:
        room_ready_state[room_id].append(current_user.id)
    
    if all_ready(room_id):
        task = generate_task()
        for connection in active_connections[room_id]:
            await connection.send_text(f"Начало задачи: {task}")
        timer = Timer(15 * 60, lambda: end_task(room_id))
        timer.start()
    return {"message": "marked as ready"}

async def end_task(room_id: int):
    for connection in active_connections[room_id]:
        await connection.send_text("Время вышло. Проверка решений...")
