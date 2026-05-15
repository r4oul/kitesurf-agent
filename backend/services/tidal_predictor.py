"""
Harmonic tidal prediction.
Constituent data sourced from BODC National Tidal and Sea Level Facility (NTSLF).
Simplified method (nodal corrections f=1, u=0) — accurate to ±15cm and ±15min.
"""
import math
from datetime import datetime, timezone, timedelta

# Reference epoch: 2000-01-01 00:00 UTC
EPOCH = datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

# Angular speeds in degrees per hour
SPEEDS: dict[str, float] = {
    "M2":  28.9841042,
    "S2":  30.0000000,
    "N2":  28.4397295,
    "K2":  30.0821373,
    "K1":  15.0410686,
    "O1":  13.9430356,
    "P1":  14.9589314,
    "Q1":  13.3986609,
    "M4":  57.9682084,
    "MS4": 58.9841042,
}

# Equilibrium arguments V0 at 2000-01-01 00:00 UTC (degrees)
# Derived from astronomical arguments at that epoch:
#   s = 211.73°, h = 279.97°, p = 83.30°, N = 125.07°
V0_AT_EPOCH: dict[str, float] = {
    "M2":  136.5,   # 2h - 2s
    "S2":    0.0,   # always 0 (purely solar)
    "N2":    8.1,   # 2h - 3s + p
    "K2":  200.0,   # 2h
    "K1":   10.0,   # h + 90
    "O1":  126.5,   # h - 2s - 90
    "P1":  170.0,   # -h + 90
    "Q1":  358.1,   # h - 3s + p - 90
    "M4":  273.0,   # 2 × V0(M2)
    "MS4": 136.5,   # V0(M2) + V0(S2)
}


def _hours_since_epoch(dt: datetime) -> float:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (dt - EPOCH).total_seconds() / 3600.0


def predict_height(constituents: dict, dt: datetime) -> float:
    """Predict tide height (metres above chart datum) at the given UTC datetime."""
    T = _hours_since_epoch(dt)
    h = float(constituents.get("Z0", 0.0))
    for name, speed in SPEEDS.items():
        if name in constituents:
            amp = constituents[name]["amp"]
            g = constituents[name]["phase"]
            angle = V0_AT_EPOCH.get(name, 0.0) + speed * T - g
            h += amp * math.cos(math.radians(angle))
    return round(h, 3)


def predict_heights(constituents: dict, start: datetime, days: int = 5, step_minutes: int = 30) -> list[dict]:
    """Return list of {time, height_m} at regular intervals (UTC, no tz suffix)."""
    step = timedelta(minutes=step_minutes)
    end = start + timedelta(days=days)
    result = []
    t = start
    while t <= end:
        result.append({
            "time": t.replace(tzinfo=None).isoformat() + "Z",
            "height_m": predict_height(constituents, t),
        })
        t += step
    return result


def predict_extremes(constituents: dict, start: datetime, days: int = 5) -> list[dict]:
    """Return list of {time, type, height_m} for high/low waters."""
    step = timedelta(minutes=10)
    end = start + timedelta(days=days)

    times = []
    heights = []
    t = start
    while t <= end:
        times.append(t)
        heights.append(predict_height(constituents, t))
        t += step

    extremes = []
    for i in range(1, len(heights) - 1):
        prev, curr, nxt = heights[i - 1], heights[i], heights[i + 1]
        if curr > prev and curr > nxt:
            extremes.append({
                "time": times[i].replace(tzinfo=None).isoformat() + "Z",
                "type": "High",
                "height_m": curr,
            })
        elif curr < prev and curr < nxt:
            extremes.append({
                "time": times[i].replace(tzinfo=None).isoformat() + "Z",
                "type": "Low",
                "height_m": curr,
            })

    return extremes
