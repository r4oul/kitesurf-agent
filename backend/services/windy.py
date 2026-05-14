import httpx
import math
from datetime import datetime, timezone, timedelta

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
CACHE_TTL_MINUTES = 30

WIND_DIRECTIONS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                   "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]

# In-memory cache: key = (lat, lon), value = (fetched_at, forecasts)
_cache: dict = {}


def _cache_key(lat: float, lon: float) -> str:
    return f"{round(lat, 2)},{round(lon, 2)}"


def _is_fresh(fetched_at: datetime) -> bool:
    return datetime.now(timezone.utc) - fetched_at < timedelta(minutes=CACHE_TTL_MINUTES)


def degrees_to_compass(degrees: float) -> str:
    index = round(degrees / 22.5) % 16
    return WIND_DIRECTIONS[index]


def kmh_to_knots(kmh: float) -> float:
    return round(kmh * 0.539957, 1)


async def get_wind_forecast(lat: float, lon: float) -> list[dict]:
    key = _cache_key(lat, lon)

    if key in _cache:
        fetched_at, forecasts = _cache[key]
        if _is_fresh(fetched_at):
            return forecasts

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "windspeed_10m,winddirection_10m,windgusts_10m",
        "windspeed_unit": "kmh",
        "forecast_days": 5,
        "timezone": "UTC",
        "models": "best_match",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(OPEN_METEO_URL, params=params)
        if response.status_code != 200:
            print(f"Open-Meteo error {response.status_code}: {response.text[:200]}")
            if key in _cache:
                _, forecasts = _cache[key]
                return forecasts
            return []
        data = response.json()

    times = data.get("hourly", {}).get("time", [])
    speeds = data.get("hourly", {}).get("windspeed_10m", [])
    directions = data.get("hourly", {}).get("winddirection_10m", [])
    gusts = data.get("hourly", {}).get("windgusts_10m", [])

    forecasts = []
    for i, t in enumerate(times):
        speed_kmh = speeds[i] if i < len(speeds) else 0
        direction_deg = directions[i] if i < len(directions) else 0
        gust_kmh = gusts[i] if i < len(gusts) else None
        # ECMWF IFS doesn't provide gusts — fall back to speed as minimum estimate
        if gust_kmh is None:
            gust_kmh = speed_kmh

        forecasts.append({
            "time": t,  # already ISO format from Open-Meteo
            "wind_speed_knots": kmh_to_knots(speed_kmh),
            "wind_gust_knots": kmh_to_knots(gust_kmh),
            "wind_direction": degrees_to_compass(direction_deg),
            "wind_direction_degrees": round(direction_deg, 1),
        })

    _cache[key] = (datetime.now(timezone.utc), forecasts)
    return forecasts
