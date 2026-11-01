"""
Harmonic tidal prediction.
Constituent data sourced from BODC National Tidal and Sea Level Facility (NTSLF).
Includes standard first-order nodal corrections (f, u) for the 18.6-year lunar
nodal cycle — see nodal_factors() below. Still a simplified method relative to
full Doodson/Schureman harmonic analysis — accurate to roughly ±15cm and ±15min
even with nodal correction applied; per-station phase drift beyond that is a
calibration issue (see tidal_stations.py comments), not something nodal
correction fixes.
"""
import math
from datetime import datetime, timezone, timedelta

# Reference epoch: 2000-01-01 00:00 UTC
EPOCH = datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
JULIAN_CENTURY_DAYS = 36525.0

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


def _lunar_node_longitude(T_hours: float) -> float:
    """Longitude of the Moon's ascending node N (degrees), at T hours since EPOCH.

    N regresses ~19.34°/year (full cycle 18.6 years). Standard formula
    (e.g. Meeus, Schureman): N = 125.04452 - 1934.136261° per Julian century,
    T in Julian centuries since J2000.0. The ~12hr offset between our EPOCH
    (2000-01-01 00:00 UTC) and the standard J2000.0 epoch (2000-01-01 12:00 TT)
    is negligible for an 18.6-year-period quantity.
    """
    T_centuries = (T_hours / 24.0) / JULIAN_CENTURY_DAYS
    N = 125.04452 - 1934.136261 * T_centuries
    return N % 360.0


# Standard first-order nodal factor coefficients (Schureman 1958-style linear
# approximation in cos(N)/sin(N)) for the constituents in this model.
# f = amplitude scale factor, u = phase adjustment in degrees.
# S2 and P1 are purely solar — no lunar nodal modulation (f=1, u=0).
def nodal_factors(name: str, N_deg: float) -> tuple[float, float]:
    """Return (f, u_degrees) nodal correction for constituent `name` at node
    longitude N_deg. M4/MS4 (compound shallow-water terms) derive from M2/S2."""
    n = math.radians(N_deg)
    cos_n, sin_n = math.cos(n), math.sin(n)

    if name in ("M2", "N2"):
        return 1.0 - 0.037 * cos_n, -2.1 * sin_n
    if name == "K2":
        return 1.024 + 0.286 * cos_n, -17.7 * sin_n
    if name == "K1":
        return 1.006 + 0.115 * cos_n, -8.9 * sin_n
    if name in ("O1", "Q1"):
        return 1.009 + 0.187 * cos_n, 10.8 * sin_n
    if name == "M4":
        f_m2, u_m2 = nodal_factors("M2", N_deg)
        return f_m2 * f_m2, 2.0 * u_m2
    if name == "MS4":
        f_m2, u_m2 = nodal_factors("M2", N_deg)
        return f_m2, u_m2  # MS4 = M2 + S2; S2 contributes f=1, u=0
    return 1.0, 0.0  # S2, P1 — purely solar, no nodal modulation


def predict_height(constituents: dict, dt: datetime) -> float:
    """Predict tide height (metres above chart datum) at the given UTC datetime."""
    T = _hours_since_epoch(dt)
    N_deg = _lunar_node_longitude(T)
    h = float(constituents.get("Z0", 0.0))
    for name, speed in SPEEDS.items():
        if name in constituents:
            amp = constituents[name]["amp"]
            g = constituents[name]["phase"]
            f, u = nodal_factors(name, N_deg)
            angle = V0_AT_EPOCH.get(name, 0.0) + speed * T + u - g
            h += f * amp * math.cos(math.radians(angle))
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
    n = len(heights)
    i = 1
    while i < n - 1:
        curr = heights[i]
        prev = heights[i - 1]

        # Advance j past any flat plateau (M4 shallow-water constituent can
        # produce a near-flat peak that rounds to equal heights at 10-min steps)
        j = i
        while j + 1 < n - 1 and heights[j + 1] == curr:
            j += 1
        nxt = heights[j + 1] if j + 1 < n else curr

        mid = (i + j) // 2  # midpoint of plateau → best time estimate
        if curr > prev and curr > nxt:
            extremes.append({
                "time": times[mid].replace(tzinfo=None).isoformat() + "Z",
                "type": "High",
                "height_m": curr,
            })
        elif curr < prev and curr < nxt:
            extremes.append({
                "time": times[mid].replace(tzinfo=None).isoformat() + "Z",
                "type": "Low",
                "height_m": curr,
            })
        i = j + 1  # jump past plateau

    return extremes
