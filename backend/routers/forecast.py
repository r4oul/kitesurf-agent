import asyncio
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.beach import Beach
from backend.services.windy import get_wind_forecast
from backend.services.tides import get_tides, get_tide_state
from backend.services.recommender import recommend_beaches
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

    # Use user's location if provided, otherwise central beach (Portland area)
    if lat is not None and lon is not None:
        ref_lat, ref_lon = lat, lon
    else:
        reference = beaches[len(beaches) // 2]
        ref_lat, ref_lon = reference.latitude, reference.longitude

    # Single wind + tide fetch for recommendations (GFS is 25km resolution anyway)
    wind_data, tide_data = await asyncio.gather(
        get_wind_forecast(ref_lat, ref_lon),
        get_tides(ref_lat, ref_lon),
    )

    if not wind_data:
        return {"error": "Could not fetch wind forecast"}

    now_utc = datetime.now(timezone.utc).isoformat()
    current_wind = wind_data[0]
    current_height = tide_data["heights"][0]["height_m"] if tide_data["heights"] else 1.5
    tide_info = get_tide_state(current_height, tide_data["extremes"])

    recommendations = recommend_beaches(
        beaches=beaches,
        wind_speed=current_wind["wind_speed_knots"],
        wind_direction=current_wind["wind_direction"],
        tide_state=tide_info["state"],
        tide_direction=tide_info["direction"],
        rider_level=rider_level,
        top_n=len(beaches),
    )

    # Fetch sewage status for all beaches in parallel
    sewage_results = await asyncio.gather(
        *[get_sewage_status(r["latitude"], r["longitude"]) for r in recommendations]
    )
    for rec, sewage in zip(recommendations, sewage_results):
        rec.update(sewage)

    return {
        "conditions": {
            "wind_speed_knots": current_wind["wind_speed_knots"],
            "wind_gust_knots": current_wind["wind_gust_knots"],
            "wind_direction": current_wind["wind_direction"],
            "tide_state": tide_info["state"],
            "tide_direction": tide_info["direction"],
            "fetched_at": now_utc,
        },
        "recommendations": recommendations,
    }
