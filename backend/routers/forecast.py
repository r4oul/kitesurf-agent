import asyncio
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.beach import Beach
from backend.services.windy import get_wind_forecast
import backend.services.windy as windy_service
from backend.services.tides import get_tides, get_tide_state
from backend.services.recommender import score_beach
from backend.services.forecast_windows import get_beach_windows
from backend.services.sewage import get_sewage_status
from datetime import datetime, timezone

router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.get("/beach/{beach_id}")
async def beach_forecast(
    beach_id: int,
    rider_level: str = Query("intermediate"),
    db: Session = Depends(get_db),
):
    beach = db.query(Beach).filter(Beach.id == beach_id).first()
    if not beach:
        return {"error": "Beach not found"}

    windows, tides, sewage = await asyncio.gather(
        get_beach_windows(beach, rider_level),
        get_tides(beach.latitude, beach.longitude),
        get_sewage_status(beach.latitude, beach.longitude),
    )

    return {
        "beach_id": beach.id,
        "beach_name": beach.name,
        "windows": windows,
        "tide_extremes": tides["extremes"][:12],
        **sewage,
    }


@router.get("/recommend")
async def get_recommendations(
    rider_level: str = Query(..., description="beginner, intermediate, or advanced"),
    lat: float = Query(None, description="User latitude"),
    lon: float = Query(None, description="User longitude"),
    db: Session = Depends(get_db),
):
    beaches = db.query(Beach).all()
    if not beaches:
        return {"recommendations": []}

    # Reference location for the conditions card (user's position or midpoint)
    if lat is not None and lon is not None:
        ref_lat, ref_lon = lat, lon
    else:
        reference = beaches[len(beaches) // 2]
        ref_lat, ref_lon = reference.latitude, reference.longitude

    # Fetch reference conditions + per-beach wind + per-beach tide — all in parallel.
    # Tide is local harmonic computation (free). Wind is cached per location.
    all_results = await asyncio.gather(
        get_wind_forecast(ref_lat, ref_lon),                          # ref conditions card
        get_tides(ref_lat, ref_lon),                                  # ref conditions card
        *[get_wind_forecast(b.latitude, b.longitude) for b in beaches],
        *[get_tides(b.latitude, b.longitude, constituents=b.tide_constituents) for b in beaches],
    )

    ref_wind_data = all_results[0]
    ref_tide_data = all_results[1]
    n = len(beaches)
    beach_wind_data = all_results[2:2 + n]
    beach_tide_data = all_results[2 + n:]

    if not ref_wind_data:
        return {"error": "Could not fetch wind forecast"}

    now_utc = datetime.now(timezone.utc).isoformat()
    ref_wind = ref_wind_data[0]
    now_hour = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:00")
    height_entry = next((h for h in ref_tide_data["heights"] if h["time"].startswith(now_hour)), None)
    ref_height = height_entry["height_m"] if height_entry else 1.5
    ref_tide_info = get_tide_state(ref_height, ref_tide_data["extremes"])

    # Score each beach against its own local wind and tide
    recommendations = []
    for beach, wind_data, tide_data in zip(beaches, beach_wind_data, beach_tide_data):
        if not wind_data:
            continue
        current_wind = wind_data[0]
        h_entry = next((h for h in tide_data["heights"] if h["time"].startswith(now_hour)), None)
        height = h_entry["height_m"] if h_entry else 1.5
        tide_info = get_tide_state(height, tide_data["extremes"])
        rec = score_beach(
            beach=beach,
            wind_speed=current_wind["wind_speed_knots"],
            wind_direction=current_wind["wind_direction"],
            tide_state=tide_info["state"],
            tide_direction=tide_info["direction"],
            rider_level=rider_level,
        )
        recommendations.append(rec)

    recommendations.sort(key=lambda x: x["score"], reverse=True)

    # Fetch sewage status for all beaches in parallel
    sewage_results = await asyncio.gather(
        *[get_sewage_status(r["latitude"], r["longitude"]) for r in recommendations]
    )
    for rec, sewage in zip(recommendations, sewage_results):
        rec.update(sewage)

    return {
        "conditions": {
            "wind_speed_knots": ref_wind["wind_speed_knots"],
            "wind_gust_knots": ref_wind["wind_gust_knots"],
            "wind_direction": ref_wind["wind_direction"],
            "tide_state": ref_tide_info["state"],
            "tide_direction": ref_tide_info["direction"],
            "fetched_at": now_utc,
            "wind_model": windy_service.wind_model_label,
        },
        "recommendations": recommendations,
    }
