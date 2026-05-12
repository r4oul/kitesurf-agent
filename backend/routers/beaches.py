from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from backend.database import get_db
from backend.models.beach import Beach

router = APIRouter(prefix="/beaches", tags=["beaches"])


class WhatsAppGroup(BaseModel):
    name: str
    invite_link: str


class BeachCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    wind_directions: List[str]
    wind_speed_min: int
    wind_speed_max: int
    tide_states: List[str]
    tide_directions: List[str]
    rider_levels: List[str]
    hazards: Optional[str] = None
    notes: Optional[str] = None
    whatsapp_groups: Optional[List[WhatsAppGroup]] = []


class BeachResponse(BeachCreate):
    id: int

    class Config:
        from_attributes = True


@router.get("/", response_model=List[BeachResponse])
def list_beaches(db: Session = Depends(get_db)):
    return db.query(Beach).all()


@router.get("/{beach_id}", response_model=BeachResponse)
def get_beach(beach_id: int, db: Session = Depends(get_db)):
    beach = db.query(Beach).filter(Beach.id == beach_id).first()
    if not beach:
        raise HTTPException(status_code=404, detail="Beach not found")
    return beach


@router.post("/", response_model=BeachResponse)
def create_beach(beach: BeachCreate, db: Session = Depends(get_db)):
    db_beach = Beach(
        **beach.model_dump(exclude={"whatsapp_groups"}),
        whatsapp_groups=[g.model_dump() for g in (beach.whatsapp_groups or [])]
    )
    db.add(db_beach)
    db.commit()
    db.refresh(db_beach)
    return db_beach


@router.put("/{beach_id}", response_model=BeachResponse)
def update_beach(beach_id: int, beach: BeachCreate, db: Session = Depends(get_db)):
    db_beach = db.query(Beach).filter(Beach.id == beach_id).first()
    if not db_beach:
        raise HTTPException(status_code=404, detail="Beach not found")
    for key, value in beach.model_dump(exclude={"whatsapp_groups"}).items():
        setattr(db_beach, key, value)
    db_beach.whatsapp_groups = [g.model_dump() for g in (beach.whatsapp_groups or [])]
    db.commit()
    db.refresh(db_beach)
    return db_beach


@router.delete("/{beach_id}")
def delete_beach(beach_id: int, db: Session = Depends(get_db)):
    db_beach = db.query(Beach).filter(Beach.id == beach_id).first()
    if not db_beach:
        raise HTTPException(status_code=404, detail="Beach not found")
    db.delete(db_beach)
    db.commit()
    return {"message": f"{db_beach.name} deleted"}
