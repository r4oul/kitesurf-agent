"""
Tidal prediction using local harmonic constituents — no external API required.
Falls back to the nearest reference station if a beach has no stored constituents.
"""
from datetime import datetime, timezone
from backend.services.tidal_predictor import predict_heights, predict_extremes
from backend.services.tidal_stations import find_nearest_station


async def get_tides(lat: float, lon: float, days: int = 5, constituents: dict = None) -> dict:
    """
    Return tide heights and extremes for the given location.

    If constituents are provided (stored on a Beach record), use them directly.
    Otherwise, find the nearest reference station and use its constituents.
    """
    if not constituents:
        station = find_nearest_station(lat, lon)
        constituents = station["constituents"]

    # Start from midnight UTC so heights align with wind forecast data (which starts at 00:00)
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    heights = predict_heights(constituents, today, days=days)
    extremes = predict_extremes(constituents, today, days=days)

    return {"heights": heights, "extremes": extremes}


def get_tide_state(height_m: float, extremes: list[dict], at_time: datetime = None) -> dict:
    """
    Given a height and list of extremes, return tide state and direction.
    at_time: the forecast time to evaluate (defaults to now).
    """
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

    if at_time is None:
        at_time = datetime.now(timezone.utc)
    ref_str = at_time.replace(tzinfo=None).isoformat()
    future = [e for e in extremes if e["time"] > ref_str]
    if future:
        direction = "incoming" if future[0]["type"] == "High" else "outgoing"
    else:
        direction = "slack"

    return {"state": state, "direction": direction}
