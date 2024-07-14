from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime

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

# In-memory storage
sessions: Dict[str, Session] = {}

# Endpoints
@app.post("/sessions", response_model=Session)
def create_session(id: str):
    if id in sessions:
        raise HTTPException(status_code=400, detail="Session already exists")
    session = Session(id=id)
    sessions[id] = session
    return session

@app.post("/sessions/{id}/rooms", response_model=Room)
def add_room_to_session(id: str, room: Room):
    if id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    session = sessions[id]
    for r in session.rooms:
        if r.name == room.name:
            raise HTTPException(status_code=400, detail="Room with this name already exists in the session")
    session.rooms.append(room)
    return room

@app.post("/sessions/{id}/rooms/{room_name}/players", response_model=Player)
def add_player_to_room(id: str, room_name: str, player: Player):
    if id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    session = sessions[id]
    for room in session.rooms:
        if room.name == room_name:
            player.updated_at = datetime.utcnow()
            room.players.append(player)
            return player
    raise HTTPException(status_code=404, detail="Room not found")

@app.patch("/sessions/{id}/rooms/{room_name}/players/{player_name}", response_model=Player)
def update_player(id: str, room_name: str, player_name: str, updated_player: Player):
    if id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    session = sessions[id]
    for room in session.rooms:
        if room.name == room_name:
            for player in room.players:
                if player.name == player_name:
                    player.name = updated_player.name
                    player.missions_passed = updated_player.missions_passed
                    player.updated_at = datetime.utcnow()
                    return player
    raise HTTPException(status_code=404, detail="Player not found")

@app.get("/sessions", response_model=List[Session])
def list_sessions():
    return list(sessions.values())

@app.get("/sessions/{id}", response_model=Session)
def get_session(id: str):
    if id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[id]

@app.get("/sessions/{id}/rooms/{room_name}", response_model=Room)
def get_room(id: str, room_name: str):
    if id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    session = sessions[id]
    for room in session.rooms:
        if room.name == room_name:
            return room
    raise HTTPException(status_code=404, detail="Room not found")

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, id: str):
    if id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    session = sessions[id]
    
    # Find the player with the latest updated_at field
    latest_player = None
    for room in session.rooms:
        for player in room.players:
            if latest_player is None or player.updated_at > latest_player.updated_at:
                latest_player = player
    
    now = datetime.utcnow()
    rooms = []
    for room in session.rooms:
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
        "session": session,
        "rooms": rooms,
        "now": now,
        "NB_MISSIONS": NB_MISSIONS,
    })

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
