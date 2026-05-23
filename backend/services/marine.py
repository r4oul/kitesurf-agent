import httpx
from datetime import datetime, timezone, timedelta

MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"
CACHE_TTL_MINUTES = 60

_cache: dict = {}

COMPASS = ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]


def _cache_key(lat: float, lon: float) -> str:
    return f"{round(lat, 2)},{round(lon, 2)}"


def _is_fresh(fetched_at: datetime) -> bool:
    return datetime.now(timezone.utc) - fetched_at < timedelta(minutes=CACHE_TTL_MINUTES)


def _degrees_to_compass(degrees: float) -> str:
    return COMPASS[round(degrees / 22.5) % 16]


async def get_marine(lat: float, lon: float) -> dict:
    key = _cache_key(lat, lon)
    if key in _cache:
        fetched_at, data = _cache[key]
        if _is_fresh(fetched_at):
            return data

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "wave_height,wave_direction,wave_period,sea_surface_temperature",
        "timezone": "UTC",
        "forecast_days": 2,
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(MARINE_URL, params=params)
            if response.status_code != 200:
                return {}
            data = response.json()
    except Exception as e:
        print(f"Marine API error: {e}")
        return {}

    hourly = data.get("hourly", {})
    times      = hourly.get("time", [])
    heights    = hourly.get("wave_height", [])
    directions = hourly.get("wave_direction", [])
    periods    = hourly.get("wave_period", [])
    temps      = hourly.get("sea_surface_temperature", [])

    if not times:
        return {}

    now_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H")
    idx = next((i for i, t in enumerate(times) if t.startswith(now_prefix)), None)
    if idx is None:
        return {}

    def _safe(lst, i):
        return lst[i] if i < len(lst) and lst[i] is not None else None

    result = {
        "wave_height_m":  round(_safe(heights, idx), 1)    if _safe(heights, idx)    is not None else None,
        "wave_direction": _degrees_to_compass(_safe(directions, idx)) if _safe(directions, idx) is not None else None,
        "wave_period_s":  round(_safe(periods, idx))        if _safe(periods, idx)    is not None else None,
        "water_temp_c":   round(_safe(temps, idx), 1)       if _safe(temps, idx)      is not None else None,
    }

    _cache[key] = (datetime.now(timezone.utc), result)
    return result
