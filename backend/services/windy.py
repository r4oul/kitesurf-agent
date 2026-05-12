import httpx
import os
import math
from datetime import datetime

WINDY_URL = "https://api.windy.com/api/point-forecast/v2"

WIND_DIRECTIONS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                   "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]

def degrees_to_compass(degrees: float) -> str:
    index = round(degrees / 22.5) % 16
    return WIND_DIRECTIONS[index]

def ms_to_knots(ms: float) -> float:
    return round(ms * 1.94384, 1)

async def get_wind_forecast(lat: float, lon: float) -> list[dict]:
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
        response.raise_for_status()
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

    return forecasts
