import httpx
import math
from datetime import datetime, timezone, timedelta

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
METNO_URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
METNO_HEADERS = {"User-Agent": "KitesurfAgent/1.0 github.com/r4oul/kitesurf-agent"}

CACHE_TTL_MINUTES = 30

PRIMARY_MODEL = "icon_eu"
PRIMARY_LABEL = "DWD ICON EU"
FALLBACK_MODEL = "gfs_seamless"
FALLBACK_LABEL = "GFS (ICON unavailable)"
METNO_LABEL = "Met.no (GFS unavailable)"

WIND_DIRECTIONS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                   "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]

# In-memory cache: key = (lat, lon), value = (fetched_at, forecasts, model_label)
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


def _has_gusts(gusts: list) -> bool:
    """Return True if the gust list contains at least some real values."""
    return any(g is not None for g in gusts)


async def _fetch_model(lat: float, lon: float, model: str) -> tuple[list, bool]:
    """Fetch from Open-Meteo for a given model. Returns (forecasts, success)."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "windspeed_10m,winddirection_10m,windgusts_10m",
        "windspeed_unit": "kmh",
        "forecast_days": 5,
        "timezone": "UTC",
        "models": model,
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(OPEN_METEO_URL, params=params)
            if response.status_code != 200:
                print(f"Open-Meteo {model} error {response.status_code}: {response.text[:200]}")
                return [], False
            data = response.json()
    except Exception as e:
        print(f"Open-Meteo {model} exception: {e}")
        return [], False

    times = data.get("hourly", {}).get("time", [])
    speeds = data.get("hourly", {}).get("windspeed_10m", [])
    directions = data.get("hourly", {}).get("winddirection_10m", [])
    gusts = data.get("hourly", {}).get("windgusts_10m", [])

    if not times:
        return [], False

    # If gusts are all null (e.g. ECMWF IFS), treat as failure so we fall back
    if not _has_gusts(gusts):
        print(f"Open-Meteo {model}: no gust data, falling back")
        return [], False

    forecasts = []
    for i, t in enumerate(times):
        speed_kmh = speeds[i] if i < len(speeds) else 0
        direction_deg = directions[i] if i < len(directions) else 0
        gust_kmh = gusts[i] if i < len(gusts) else None
        if gust_kmh is None:
            gust_kmh = speed_kmh

        forecasts.append({
            "time": t + "Z",
            "wind_speed_knots": kmh_to_knots(speed_kmh),
            "wind_gust_knots": kmh_to_knots(gust_kmh),
            "wind_direction": degrees_to_compass(direction_deg),
            "wind_direction_degrees": round(direction_deg, 1),
        })

    return forecasts, True


async def _fetch_metno(lat: float, lon: float) -> tuple[list, bool]:
    """Fetch from Met.no Locationforecast 2.0. Returns (forecasts, success)."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                METNO_URL,
                params={"lat": round(lat, 4), "lon": round(lon, 4)},
                headers=METNO_HEADERS,
            )
            if response.status_code != 200:
                print(f"Met.no error {response.status_code}: {response.text[:200]}")
                return [], False
            data = response.json()
    except Exception as e:
        print(f"Met.no exception: {e}")
        return [], False

    timeseries = data.get("properties", {}).get("timeseries", [])
    if not timeseries:
        return [], False

    forecasts = []
    for entry in timeseries:
        time_str = entry["time"][:16] + "Z"  # "2026-05-14T12:00Z"
        details = entry.get("data", {}).get("instant", {}).get("details", {})
        speed_ms = details.get("wind_speed", 0)
        direction_deg = details.get("wind_from_direction", 0)
        gust_ms = details.get("wind_speed_of_gust") or speed_ms * 1.3

        forecasts.append({
            "time": time_str,
            "wind_speed_knots": round(speed_ms * 1.94384, 1),
            "wind_gust_knots": round(gust_ms * 1.94384, 1),
            "wind_direction": degrees_to_compass(direction_deg),
            "wind_direction_degrees": round(direction_deg, 1),
        })

    return forecasts, True


# Module-level label so the router can read which model is active
wind_model_label: str = PRIMARY_LABEL


async def get_wind_forecast(lat: float, lon: float) -> list[dict]:
    global wind_model_label
    key = _cache_key(lat, lon)

    if key in _cache:
        fetched_at, forecasts, label = _cache[key]
        if _is_fresh(fetched_at):
            wind_model_label = label
            return forecasts

    # Try ECMWF → GFS → Met.no
    forecasts, ok = await _fetch_model(lat, lon, PRIMARY_MODEL)
    if ok:
        label = PRIMARY_LABEL
    else:
        forecasts, ok = await _fetch_model(lat, lon, FALLBACK_MODEL)
        if ok:
            label = FALLBACK_LABEL
        else:
            forecasts, ok = await _fetch_metno(lat, lon)
            label = METNO_LABEL if ok else PRIMARY_LABEL

    if forecasts:
        _cache[key] = (datetime.now(timezone.utc), forecasts, label)

    wind_model_label = label
    return forecasts
