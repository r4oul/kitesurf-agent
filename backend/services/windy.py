import httpx
import os
import math
from datetime import datetime, timezone, timedelta

WINDY_URL = "https://api.windy.com/api/point-forecast/v2"
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


def ms_to_knots(ms: float) -> float:
    return round(ms * 1.94384, 1)


async def get_wind_forecast(lat: float, lon: float) -> list[dict]:
    key = _cache_key(lat, lon)

    if key in _cache:
        fetched_at, forecasts = _cache[key]
        if _is_fresh(fetched_at):
            return forecasts

    payload = {
        "lat": lat,
        "lon": lon,
        "model": "gfs",
        "parameters": ["wind", "windGust"],
        "levels": ["surface"],
        "key": os.getenv("WINDY_API_KEY"),
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(WINDY_URL, json=payload)
        if response.status_code != 200:
            print(f"Windy API error {response.status_code}: {response.text[:200]}")
            if key in _cache:
                _, forecasts = _cache[key]
                return forecasts
            return []
        data = response.json()

    timestamps = data.get("ts", [])
    u_values = data.get("wind_u-surface", [])
    v_values = data.get("wind_v-surface", [])
    gust_values = data.get("gust-surface", [])

    forecasts = []
    for i, ts in enumerate(timestamps):
        u = u_values[i] if i < len(u_values) else 0
        v = v_values[i] if i < len(v_values) else 0
        gust = gust_values[i] if i < len(gust_values) else 0

        speed_ms = math.sqrt(u**2 + v**2)
        direction_deg = math.degrees(math.atan2(-u, -v)) % 360

        forecasts.append({
            "time": datetime.utcfromtimestamp(ts / 1000).isoformat(),
            "wind_speed_knots": ms_to_knots(speed_ms),
            "wind_gust_knots": ms_to_knots(gust),
            "wind_direction": degrees_to_compass(direction_deg),
            "wind_direction_degrees": round(direction_deg, 1),
        })

    _cache[key] = (datetime.now(timezone.utc), forecasts)
    return forecasts
