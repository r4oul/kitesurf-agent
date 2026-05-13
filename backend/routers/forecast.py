import asyncio
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.beach import Beach
from backend.services.windy import get_wind_forecast
from backend.services.tides import get_tides, get_tide_state
from backend.services.recommender import score_beach
from backend.services.forecast_windows import get_beach_windows
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

    windows = await get_beach_windows(beach, rider_level)
    tides = await get_tides(beach.latitude, beach.longitude)

    return {
        "beach_id": beach.id,
        "beach_name": beach.name,
        "windows": windows,
        "tide_extremes": tides["extremes"][:12],
    }


async def _score_beach_with_local_weather(beach: Beach, rider_level: str) -> dict:
    """Fetch weather at the beach's own coordinates and score it."""
    wind_data, tide_data = await asyncio.gather(
        get_wind_forecast(beach.latitude, beach.longitude),
        get_tides(beach.latitude, beach.longitude),
    )
    if not wind_data:
        return None

    current_wind = wind_data[0]
    current_height = tide_data["heights"][0]["height_m"] if tide_data["heights"] else 1.5
    tide_info = get_tide_state(current_height, tide_data["extremes"])

    result = score_beach(
        beach=beach,
        wind_speed=current_wind["wind_speed_knots"],
        wind_direction=current_wind["wind_direction"],
        tide_state=tide_info["state"],
        tide_direction=tide_info["direction"],
        rider_level=rider_level,
    )
    result["local_wind_speed_knots"] = current_wind["wind_speed_knots"]
    result["local_wind_gust_knots"] = current_wind["wind_gust_knots"]
    result["local_wind_direction"] = current_wind["wind_direction"]
    return result


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

    # Fetch user's local conditions for the header card
    if lat is not None and lon is not None:
        ref_lat, ref_lon = lat, lon
    else:
        reference = beaches[len(beaches) // 2]
        ref_lat, ref_lon = reference.latitude, reference.longitude

    # Fetch user conditions + all beach conditions in parallel
    user_wind_task = get_wind_forecast(ref_lat, ref_lon)
    user_tide_task = get_tides(ref_lat, ref_lon)
    beach_tasks = [_score_beach_with_local_weather(b, rider_level) for b in beaches]

    user_wind, user_tide, *beach_results = await asyncio.gather(
        user_wind_task, user_tide_task, *beach_tasks
    )

    if not user_wind:
        return {"error": "Could not fetch wind forecast"}

    now_utc = datetime.now(timezone.utc).isoformat()
    current_wind = user_wind[0]
    current_height = user_tide["heights"][0]["height_m"] if user_tide["heights"] else 1.5
    tide_info = get_tide_state(current_height, user_tide["extremes"])

    recommendations = [r for r in beach_results if r is not None]
    recommendations.sort(key=lambda x: x["score"], reverse=True)

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
