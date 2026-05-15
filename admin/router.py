import os
import secrets
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from typing import List, Optional
from backend.database import get_db
from backend.models.beach import Beach
from backend.services.tidal_stations import find_nearest_station

_security = HTTPBasic()

def _require_admin(credentials: HTTPBasicCredentials = Depends(_security)):
    correct_user = os.getenv("ADMIN_USERNAME", "admin")
    correct_pass = os.getenv("ADMIN_PASSWORD", "changeme")
    ok = (
        secrets.compare_digest(credentials.username, correct_user) and
        secrets.compare_digest(credentials.password, correct_pass)
    )
    if not ok:
        raise HTTPException(
            status_code=401,
            detail="Unauthorised",
            headers={"WWW-Authenticate": "Basic"},
        )

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))


@router.get("/", response_class=HTMLResponse)
def admin_home(request: Request, db: Session = Depends(get_db), _=Depends(_require_admin)):
    beaches = db.query(Beach).all()
    return templates.TemplateResponse("beach_list.html", {"request": request, "beaches": beaches})


@router.get("/beach/new", response_class=HTMLResponse)
def new_beach_form(request: Request, _=Depends(_require_admin)):
    return templates.TemplateResponse("beach_form.html", {"request": request, "beach": None})


@router.post("/beach/new")
async def create_beach(
    request: Request,
    db: Session = Depends(get_db),
    _=Depends(_require_admin),
):
    form = await request.form()

    try:
        name = form.get("name")
        latitude = float(form.get("latitude"))
        longitude = float(form.get("longitude"))
        wind_speed_min = int(form.get("wind_speed_min"))
        wind_speed_max = int(form.get("wind_speed_max"))
        hazards = form.get("hazards") or None
        notes = form.get("notes") or None
    except Exception as e:
        return templates.TemplateResponse("beach_form.html", {
            "request": request, "beach": None,
            "error": f"Form error: {e}"
        })
    wind_directions = form.getlist("wind_directions")
    tide_states = form.getlist("tide_states")
    tide_directions = form.getlist("tide_directions")
    rider_levels = form.getlist("rider_levels")
    wa_names = form.getlist("wa_name")
    wa_links = form.getlist("wa_link")

    missing = []
    if not wind_directions: missing.append("wind directions")
    if not tide_states: missing.append("tide states")
    if not tide_directions: missing.append("tide directions")
    if not rider_levels: missing.append("rider levels")
    if missing:
        return templates.TemplateResponse("beach_form.html", {
            "request": request, "beach": None,
            "error": f"Please tick at least one box for: {', '.join(missing)}."
        })

    whatsapp_groups = [
        {"name": n, "invite_link": l}
        for n, l in zip(wa_names, wa_links) if n.strip() and l.strip()
    ]

    station = find_nearest_station(latitude, longitude)

    beach = Beach(
        name=name, latitude=latitude, longitude=longitude,
        wind_directions=wind_directions, wind_speed_min=wind_speed_min,
        wind_speed_max=wind_speed_max, tide_states=tide_states,
        tide_directions=tide_directions, rider_levels=rider_levels,
        hazards=hazards, notes=notes, whatsapp_groups=whatsapp_groups,
        tide_station=station["name"],
        tide_constituents=station["constituents"],
    )
    db.add(beach)
    db.commit()
    return RedirectResponse("/admin/", status_code=303)


@router.get("/beach/{beach_id}/edit", response_class=HTMLResponse)
def edit_beach_form(beach_id: int, request: Request, db: Session = Depends(get_db), _=Depends(_require_admin)):
    beach = db.query(Beach).filter(Beach.id == beach_id).first()
    return templates.TemplateResponse("beach_form.html", {"request": request, "beach": beach})


@router.post("/beach/{beach_id}/edit")
async def update_beach(
    beach_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _=Depends(_require_admin),
):
    form = await request.form()

    try:
        name = form.get("name")
        latitude = float(form.get("latitude"))
        longitude = float(form.get("longitude"))
        wind_speed_min = int(form.get("wind_speed_min"))
        wind_speed_max = int(form.get("wind_speed_max"))
        hazards = form.get("hazards") or None
        notes = form.get("notes") or None
    except Exception as e:
        beach = db.query(Beach).filter(Beach.id == beach_id).first()
        return templates.TemplateResponse("beach_form.html", {
            "request": request, "beach": beach,
            "error": f"Form error: {e}"
        })

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
    beach.wind_speed_min = wind_speed_min
    beach.wind_speed_max = wind_speed_max
    beach.hazards = hazards
    beach.notes = notes
    beach.wind_directions = wind_directions
    beach.tide_states = tide_states
    beach.tide_directions = tide_directions
    beach.rider_levels = rider_levels

    # Re-derive tidal station if lat/lon changed
    station = find_nearest_station(latitude, longitude)
    beach.tide_station = station["name"]
    beach.tide_constituents = station["constituents"]
    flag_modified(beach, "tide_constituents")

    beach.whatsapp_groups = [
        {"name": n, "invite_link": l}
        for n, l in zip(wa_names, wa_links) if n.strip() and l.strip()
    ]
    flag_modified(beach, "wind_directions")
    flag_modified(beach, "tide_states")
    flag_modified(beach, "tide_directions")
    flag_modified(beach, "rider_levels")
    flag_modified(beach, "whatsapp_groups")
    db.commit()
    return RedirectResponse("/admin/", status_code=303)


@router.post("/beach/{beach_id}/delete")
def delete_beach(beach_id: int, db: Session = Depends(get_db), _=Depends(_require_admin)):
    beach = db.query(Beach).filter(Beach.id == beach_id).first()
    if beach:
        db.delete(beach)
        db.commit()
    return RedirectResponse("/admin/", status_code=303)
