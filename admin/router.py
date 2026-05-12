from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models.beach import Beach
import os

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))


@router.get("/", response_class=HTMLResponse)
def admin_home(request: Request, db: Session = Depends(get_db)):
    beaches = db.query(Beach).all()
    return templates.TemplateResponse("beach_list.html", {"request": request, "beaches": beaches})


@router.get("/beach/new", response_class=HTMLResponse)
def new_beach_form(request: Request):
    return templates.TemplateResponse("beach_form.html", {"request": request, "beach": None})


@router.post("/beach/new")
async def create_beach(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    wind_speed_min: int = Form(...),
    wind_speed_max: int = Form(...),
    hazards: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
):
    form = await request.form()
    wind_directions = form.getlist("wind_directions")
    tide_states = form.getlist("tide_states")
    tide_directions = form.getlist("tide_directions")
    rider_levels = form.getlist("rider_levels")
    wa_names = form.getlist("wa_name")
    wa_links = form.getlist("wa_link")

    if not wind_directions or not tide_states or not tide_directions or not rider_levels:
        return templates.TemplateResponse("beach_form.html", {
            "request": request, "beach": None,
            "error": "Please select at least one option for wind directions, tide states, tide directions, and rider levels."
        })

    whatsapp_groups = [
        {"name": n, "invite_link": l}
        for n, l in zip(wa_names, wa_links) if n.strip() and l.strip()
    ]

    beach = Beach(
        name=name, latitude=latitude, longitude=longitude,
        wind_directions=wind_directions, wind_speed_min=wind_speed_min,
        wind_speed_max=wind_speed_max, tide_states=tide_states,
        tide_directions=tide_directions, rider_levels=rider_levels,
        hazards=hazards, notes=notes, whatsapp_groups=whatsapp_groups
    )
    db.add(beach)
    db.commit()
    return RedirectResponse("/admin/", status_code=303)


@router.get("/beach/{beach_id}/edit", response_class=HTMLResponse)
def edit_beach_form(beach_id: int, request: Request, db: Session = Depends(get_db)):
    beach = db.query(Beach).filter(Beach.id == beach_id).first()
    return templates.TemplateResponse("beach_form.html", {"request": request, "beach": beach})


@router.post("/beach/{beach_id}/edit")
async def update_beach(
    beach_id: int,
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    wind_speed_min: int = Form(...),
    wind_speed_max: int = Form(...),
    hazards: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
):
    form = await request.form()
    wind_directions = form.getlist("wind_directions")
    tide_states = form.getlist("tide_states")
    tide_directions = form.getlist("tide_directions")
    rider_levels = form.getlist("rider_levels")
    wa_names = form.getlist("wa_name")
    wa_links = form.getlist("wa_link")

    beach = db.query(Beach).filter(Beach.id == beach_id).first()
    beach.name = name
    beach.latitude = latitude
    beach.longitude = longitude
    beach.wind_directions = wind_directions
    beach.wind_speed_min = wind_speed_min
    beach.wind_speed_max = wind_speed_max
    beach.tide_states = tide_states
    beach.tide_directions = tide_directions
    beach.rider_levels = rider_levels
    beach.hazards = hazards
    beach.notes = notes
    beach.whatsapp_groups = [
        {"name": n, "invite_link": l}
        for n, l in zip(wa_names, wa_links) if n.strip() and l.strip()
    ]
    db.commit()
    return RedirectResponse("/admin/", status_code=303)


@router.post("/beach/{beach_id}/delete")
def delete_beach(beach_id: int, db: Session = Depends(get_db)):
    beach = db.query(Beach).filter(Beach.id == beach_id).first()
    if beach:
        db.delete(beach)
        db.commit()
    return RedirectResponse("/admin/", status_code=303)
