from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime

from database import SessionLocal, Player as DBPlayer, Room as DBRoom, Session as DBSession
from schemas import PlayerCreate, Player, RoomCreate, Room, SessionCreate, Session

app = FastAPI()
NB_MISSIONS = 43

# Allow CORS for all origins (you can customize this as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Data models
class Player(BaseModel):
    name: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    missions_passed: int = Field(gt=0)

class Room(BaseModel):
    name: str
    players: List[Player] = []

class Session(BaseModel):
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    rooms: List[Room] = []

# Endpoints
@app.post("/sessions", response_model=Session)
def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    db_session = DBSession(id=session.id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@app.post("/sessions/{id}/rooms", response_model=Room)
def add_room_to_session(id: str, room: RoomCreate, db: Session = Depends(get_db)):
    db_session = db.query(DBSession).filter(DBSession.id == id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    db_room = DBRoom(name=room.name, session_id=db_session.id)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

@app.post("/sessions/{id}/rooms/{room_name}/players", response_model=Player)
def add_player_to_room(id: str, room_name: str, player: PlayerCreate, db: Session = Depends(get_db)):
    db_session = db.query(DBSession).filter(DBSession.id == id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    db_room = db.query(DBRoom).filter(DBRoom.session_id == db_session.id, DBRoom.name == room_name).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    db_player = DBPlayer(name=player.name, missions_passed=player.missions_passed, room_id=db_room.id)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

@app.patch("/sessions/{id}/rooms/{room_name}/players/{player_name}", response_model=Player)
def update_player(id: str, room_name: str, player_name: str, updated_player: PlayerCreate, db: Session = Depends(get_db)):
    db_session = db.query(DBSession).filter(DBSession.id == id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    db_room = db.query(DBRoom).filter(DBRoom.session_id == db_session.id, DBRoom.name == room_name).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    db_player = db.query(DBPlayer).filter(DBPlayer.room_id == db_room.id, DBPlayer.name == player_name).first()
    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")
    db_player.name = updated_player.name
    db_player.missions_passed = updated_player.missions_passed
    db_player.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_player)
    return db_player

@app.get("/sessions", response_model=List[Session])
def list_sessions(db: Session = Depends(get_db)):
    return db.query(DBSession).all()

@app.get("/sessions/{id}", response_model=Session)
def get_session(id: str, db: Session = Depends(get_db)):
    db_session = db.query(DBSession).filter(DBSession.id == id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session

@app.get("/sessions/{id}/rooms/{room_name}", response_model=Room)
def get_room(id: str, room_name: str, db: Session = Depends(get_db)):
    db_session = db.query(DBSession).filter(DBSession.id == id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    db_room = db.query(DBRoom).filter(DBRoom.session_id == db_session.id, DBRoom.name == room_name).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    return db_room

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, id: str, db: Session = Depends(get_db)):
    db_session = db.query(DBSession).filter(DBSession.id == id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Find the player with the latest updated_at field
    latest_player = None
    for room in db_session.rooms:
        for player in room.players:
            if latest_player is None or player.updated_at > latest_player.updated_at:
                latest_player = player
    
    now = datetime.utcnow()
    rooms = []
    for room in db_session.rooms:
        top_player = None
        latest_player = None
        for player in room.players:
            if top_player is None or player.missions_passed > top_player.missions_passed:
                top_player = player
            if latest_player is None or player.updated_at > latest_player.updated_at:
                latest_player = player
        rooms.append({"name": room.name, "top_player": top_player if top_player else None, "players": len(room.players), "last_update": latest_player.updated_at if latest_player else None})

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "session": db_session,
        "rooms": rooms,
        "now": now,
        "NB_MISSIONS": NB_MISSIONS,
    })

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/imt", response_class=HTMLResponse)
def imt(request: Request):
    return templates.TemplateResponse("imt.html", {"request": request})


# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
