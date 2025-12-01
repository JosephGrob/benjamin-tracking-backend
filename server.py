from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from fastapi import UploadFile, File, Form
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en prod tu peux restreindre à ton domaine
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Token partagé pour sécuriser l'API d'écriture
GPS_TOKEN = os.getenv("GPS_TOKEN")  # défini dans Render

class Position(BaseModel):
    lat: float
    lng: float
    time: Optional[datetime] = None
    track_id: Optional[str] = "live"

positions: List[Position] = []


def check_token(request: Request, token_query: Optional[str] = None):
    """
    Vérifie le token transmis soit :
    - dans l'en-tête HTTP 'X-API-Key'
    - soit dans le paramètre de requête 'token'
    """
    if GPS_TOKEN is None:
        # Si pas de token configuré côté serveur, on considère tout comme autorisé
        return

    header_token = request.headers.get("X-API-Key")
    provided = header_token or token_query

    if provided != GPS_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing token")


@app.post("/api/position")
def add_position(pos: Position, request: Request, token: Optional[str] = None):
    """Reçoit une nouvelle position envoyée par le bateau."""
    check_token(request, token)

    if pos.time is None:
        pos.time = datetime.utcnow()
    positions.append(pos)

    if len(positions) > 2000:
        del positions[0 : len(positions) - 2000]

    return {"status": "ok", "count": len(positions)}


@app.get("/api/live-track")
def get_live_track(track_id: str = "live"):
    """Retourne la trace pour un track_id donné (lecture publique)."""
    pts = [p for p in positions if p.track_id == track_id]
    return {
        "track_id": track_id,
        "points": [
            {"lat": p.lat, "lng": p.lng, "time": p.time.isoformat()} for p in pts
        ],
    }


@app.get("/api/position_simple")
def add_position_simple(
    lat: float,
    lng: float,
    track_id: str = "live",
    request: Request = None,
    token: Optional[str] = None,
):
    """Version simple pour certains clients: tout en paramètres d'URL."""
    check_token(request, token)

    pos = Position(lat=lat, lng=lng, track_id=track_id, time=datetime.utcnow())
    positions.append(pos)

    if len(positions) > 2000:
        del positions[0 : len(positions) - 2000]

    return {"status": "ok", "count": len(positions)}


@app.post("/api/reset-track")
def reset_track(track_id: str = "live", request: Request = None, token: Optional[str] = None):
    check_token(request, token)

    global positions
    positions = [p for p in positions if p.track_id != track_id]
    return {"status": "cleared"}

# ----------------------------------------------------------------------
#  MÉDIAS : upload + listing
# ----------------------------------------------------------------------

# Stockage temporaire en mémoire (à remplacer plus tard par du disque/S3)
MEDIA_DB = []

@app.post("/api/media")
async def upload_media(
    file: UploadFile = File(...),
    title: str = Form(""),
    description: str = Form(""),
    trackId: str = Form(""),
    lat: float = Form(...),
    lng: float = Form(...),
):
    """
    Reçoit un média (image/vidéo) + infos de position.
    Pour le moment, stocke simplement les infos en mémoire.
    """
    # Pour tester, on ne sauvegarde pas physiquement le fichier.
    # On crée une URL factice (sinon ton front casse).
    url = f"/static/uploads/{file.filename}"

    media = {
        "id": len(MEDIA_DB) + 1,
        "title": title,
        "description": description,
        "trackId": trackId,
        "lat": lat,
        "lng": lng,
        "url": url,
        "type": file.content_type,
    }
    MEDIA_DB.append(media)
    return media


@app.get("/api/media")
def list_media():
    """Renvoie tous les médias enregistrés (en mémoire)."""
    return MEDIA_DB



##enlever le test, traits jaunes## enelver au moment du depart de Benjamin!!!!!!!!!!!!!!!!!!
### acces à url API : http://127.0.0.1:8000/docs#/default/add_position_api_position_post
###Available at your primary URL https://benjamin-tracking.onrender.com



