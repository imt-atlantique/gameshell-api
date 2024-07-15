from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class PlayerBase(BaseModel):
    name: str
    missions_passed: int = 0

class PlayerCreate(PlayerBase):
    pass

class Player(PlayerBase):
    id: int
    updated_at: datetime

    class Config:
        orm_mode = True

class RoomBase(BaseModel):
    name: str

class RoomCreate(RoomBase):
    pass

class Room(RoomBase):
    id: int
    players: List[Player] = []

    class Config:
        orm_mode = True

class SessionBase(BaseModel):
    id: str

class SessionCreate(SessionBase):
    pass

class Session(SessionBase):
    created_at: datetime
    rooms: List[Room] = []

    class Config:
        orm_mode = True
