from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Position(BaseModel):
    lat: float
    lng: float
    time: Optional[datetime] = None
    track_id: Optional[str] = "live"

positions: List[Position] = []


@app.post("/api/position")
def add_position(pos: Position):
    """Reçoit une nouvelle position envoyée par le bateau."""
    if pos.time is None:
        pos.time = datetime.utcnow()
    positions.append(pos)

    # On garde les 2000 derniers points max
    if len(positions) > 2000:
        del positions[0 : len(positions) - 2000]

    return {"status": "ok", "count": len(positions)}


@app.get("/api/live-track")
def get_live_track(track_id: str = "live"):
    """Retourne la trace pour un track_id donné."""
    pts = [p for p in positions if p.track_id == track_id]
    return {
        "track_id": track_id,
        "points": [
            {"lat": p.lat, "lng": p.lng, "time": p.time.isoformat()} for p in pts
        ],
    }

@app.get("/api/position_simple")
def add_position_simple(lat: float, lng: float, track_id: str = "live"):
    """Version simple pour téléphone : tout en paramètres d'URL."""
    pos = Position(lat=lat, lng=lng, track_id=track_id, time=datetime.utcnow())
    positions.append(pos)
    if len(positions) > 2000:
        del positions[0 : len(positions) - 2000]
    return {"status": "ok", "count": len(positions)}

##enlever le test, traits jaunes## enelver au moment du depart de Benjamin!!!!!!!!!!!!!!!!!!
### acces à url API : http://127.0.0.1:8000/docs#/default/add_position_api_position_post

@app.post("/api/reset-track")
def reset_track(track_id: str = "live"):
    global positions
    positions = [p for p in positions if p.track_id != track_id]
    return {"status": "cleared"}


