from backend.services.windy import get_wind_forecast
from backend.services.tides import get_tides, get_tide_state
from backend.services.recommender import score_beach
from backend.models.beach import Beach
from datetime import datetime, timezone


async def get_beach_windows(beach: Beach, rider_level: str) -> list[dict]:
    """Return scored forecast windows for a beach over the next 5 days."""
    wind_forecast = await get_wind_forecast(beach.latitude, beach.longitude)
    tide_data = await get_tides(beach.latitude, beach.longitude, days=5)

    # Build a lookup of tide height by truncated timestamp (first 16 chars = YYYY-MM-DDTHH:MM)
    height_by_time = {h["time"][:16]: h["height_m"] for h in tide_data["heights"]}
    extremes = tide_data["extremes"]

    windows = []
    for entry in wind_forecast:
        time_str = entry["time"]
        height = height_by_time.get(time_str[:16])
        if height is None:
            height = 1.5  # fallback mid-tide

        tide_info = get_tide_state(height, extremes)
        scored = score_beach(
            beach=beach,
            wind_speed=entry["wind_speed_knots"],
            wind_direction=entry["wind_direction"],
            tide_state=tide_info["state"],
            tide_direction=tide_info["direction"],
            rider_level=rider_level,
        )

        windows.append({
            "time": time_str,
            "wind_speed_knots": entry["wind_speed_knots"],
            "wind_gust_knots": entry["wind_gust_knots"],
            "wind_direction": entry["wind_direction"],
            "tide_state": tide_info["state"],
            "tide_direction": tide_info["direction"],
            "score": scored["score"],
            "score_label": _score_label(scored["score"]),
        })

    return windows


def _score_label(score: int) -> str:
    if score >= 88: return "Excellent"
    if score >= 65: return "Good"
    if score >= 40: return "Marginal"
    return "Poor"
