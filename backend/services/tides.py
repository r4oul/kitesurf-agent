import httpx
import os
from datetime import datetime, timezone, timedelta

WORLDTIDES_URL = "https://www.worldtides.info/api/v3"
CACHE_TTL_HOURS = 24

# In-memory cache: key = (lat, lon, days), value = (fetched_at, data)
_cache: dict = {}


def _cache_key(lat: float, lon: float, days: int) -> str:
    return f"{round(lat, 2)},{round(lon, 2)},{days}"


def _is_fresh(fetched_at: datetime) -> bool:
    return datetime.now(timezone.utc) - fetched_at < timedelta(hours=CACHE_TTL_HOURS)


async def get_tides(lat: float, lon: float, days: int = 5) -> dict:
    key = _cache_key(lat, lon, days)

    if key in _cache:
        fetched_at, data = _cache[key]
        if _is_fresh(fetched_at):
            return data

    params = {
        "heights": "",
        "extremes": "",
        "lat": lat,
        "lon": lon,
        "days": days,
        "step": 1800,  # 30 min intervals
        "key": os.getenv("WORLDTIDES_API_KEY"),
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(WORLDTIDES_URL, params=params)
        if response.status_code != 200:
            # Return cached data if available, even if stale
            if key in _cache:
                _, data = _cache[key]
                return data
            return {"extremes": [], "heights": []}
        raw = response.json()

    extremes = []
    for e in raw.get("extremes", []):
        extremes.append({
            "time": datetime.utcfromtimestamp(e["dt"]).isoformat(),
            "type": e["type"],
            "height_m": round(e["height"], 2),
        })

    heights = []
    for h in raw.get("heights", []):
        heights.append({
            "time": datetime.utcfromtimestamp(h["dt"]).isoformat(),
            "height_m": round(h["height"], 2),
        })

    data = {"extremes": extremes, "heights": heights}
    _cache[key] = (datetime.now(timezone.utc), data)
    return data


def get_tide_state(height_m: float, extremes: list[dict]) -> dict:
    """Given a height and list of extremes, return tide state and direction."""
    if not extremes:
        return {"state": "unknown", "direction": "unknown"}

    highs = [e["height_m"] for e in extremes if e["type"] == "High"]
    lows = [e["height_m"] for e in extremes if e["type"] == "Low"]

    if not highs or not lows:
        return {"state": "unknown", "direction": "unknown"}

    max_high = max(highs)
    min_low = min(lows)
    tidal_range = max_high - min_low

    if tidal_range == 0:
        return {"state": "mid", "direction": "slack"}

    relative = (height_m - min_low) / tidal_range

    if relative < 0.25:
        state = "low"
    elif relative < 0.75:
        state = "mid"
    else:
        state = "high"

    now_str = datetime.now(timezone.utc).isoformat()
    future = [e for e in extremes if e["time"] > now_str]
    if future:
        next_extreme = future[0]
        direction = "incoming" if next_extreme["type"] == "High" else "outgoing"
    else:
        direction = "slack"

    return {"state": state, "direction": direction}
