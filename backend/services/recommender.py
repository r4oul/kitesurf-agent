from backend.models.beach import Beach
from backend.services.tides import get_tide_state

DIRECTION_NEIGHBOURS = {
    "N":   ["N",   "NNE", "NNW"],
    "NNE": ["NNE", "N",   "NE"],
    "NE":  ["NE",  "NNE", "ENE"],
    "ENE": ["ENE", "NE",  "E"],
    "E":   ["E",   "ENE", "ESE"],
    "ESE": ["ESE", "E",   "SE"],
    "SE":  ["SE",  "ESE", "SSE"],
    "SSE": ["SSE", "SE",  "S"],
    "S":   ["S",   "SSE", "SSW"],
    "SSW": ["SSW", "S",   "SW"],
    "SW":  ["SW",  "SSW", "WSW"],
    "WSW": ["WSW", "SW",  "W"],
    "W":   ["W",   "WSW", "WNW"],
    "WNW": ["WNW", "W",   "NW"],
    "NW":  ["NW",  "WNW", "NNW"],
    "NNW": ["NNW", "NW",  "N"],
}

def score_beach(
    beach: Beach,
    wind_speed: float,
    wind_direction: str,
    tide_state: str,
    tide_direction: str,
    rider_level: str,
) -> dict:
    score = 0
    reasons = []
    warnings = []

    # --- Wind speed (50 points) — most important factor ---
    wind_too_light = False
    wind_too_strong = False
    SWEET_SPOT_MIN = 15
    SWEET_SPOT_MAX = 25

    if beach.wind_speed_min <= wind_speed <= beach.wind_speed_max:
        if SWEET_SPOT_MIN <= wind_speed <= SWEET_SPOT_MAX:
            score += 50
            reasons.append(f"{wind_speed}kts is in the sweet spot ({SWEET_SPOT_MIN}-{SWEET_SPOT_MAX}kts)")
        elif wind_speed < SWEET_SPOT_MIN:
            score += 35
            reasons.append(f"{wind_speed}kts is in range but light - bigger kite needed")
        else:
            score += 40
            reasons.append(f"{wind_speed}kts is in range but strong - smaller kite needed")
    elif wind_speed < beach.wind_speed_min:
        diff = beach.wind_speed_min - wind_speed
        if diff <= 3:
            score += 20
            warnings.append(f"Wind slightly light ({wind_speed}kts), min is {beach.wind_speed_min}kts")
        else:
            wind_too_light = True
            warnings.append(f"Wind too light ({wind_speed}kts), need {beach.wind_speed_min}kts+")
    else:
        diff = wind_speed - beach.wind_speed_max
        if diff <= 5:
            score += 20
            warnings.append(f"Wind strong ({wind_speed}kts), max recommended is {beach.wind_speed_max}kts")
        else:
            wind_too_strong = True
            warnings.append(f"Wind too strong ({wind_speed}kts), max recommended is {beach.wind_speed_max}kts")

    # --- Wind direction (25 points) ---
    neighbours = DIRECTION_NEIGHBOURS.get(wind_direction, [wind_direction])
    direction_no_match = False
    if wind_direction in beach.wind_directions:
        score += 25
        reasons.append(f"Wind direction {wind_direction} is ideal")
    elif any(n in beach.wind_directions for n in neighbours):
        score += 10
        reasons.append(f"Wind direction {wind_direction} is marginal")
    else:
        direction_no_match = True
        warnings.append(f"Wind direction {wind_direction} not ideal for this beach")

    # --- Tide state (15 points) ---
    tide_state_no_match = False
    if tide_state in beach.tide_states:
        score += 15
        reasons.append(f"Tide state ({tide_state}) is good")
    else:
        tide_state_no_match = True
        warnings.append(f"Tide state ({tide_state}) not ideal")

    # --- Tide direction (7 points) ---
    tide_direction_no_match = False
    if tide_direction in beach.tide_directions:
        score += 7
        reasons.append(f"Tide direction ({tide_direction}) is good")
    else:
        tide_direction_no_match = True
        warnings.append(f"Tide direction ({tide_direction}) not ideal")

    # --- Rider level (3 points) ---
    level_no_match = False
    if rider_level in beach.rider_levels:
        score += 3
        reasons.append(f"Suitable for {rider_level} riders")
    else:
        level_no_match = True
        warnings.append(f"Not recommended for {rider_level} riders")

    # --- Hard caps ---
    # Unrideable wind speed: cap at 25 (Poor)
    if wind_too_light or wind_too_strong:
        score = min(score, 25)
    # Wrong wind direction: cap at 40 (top of Marginal) — never "Good" with wrong direction
    if direction_no_match:
        score = min(score, 40)
    # Wrong tide state: cap at 64 (top of Marginal) — never "Good" on wrong tide
    if tide_state_no_match:
        score = min(score, 64)
    # Wrong tide direction: cap at 50 (Marginal) — e.g. lagoon beaches on outgoing tide
    if tide_direction_no_match:
        score = min(score, 50)
    # Wrong rider level: cap at 15 — unsuitable beaches must never outrank suitable ones.
    # A beginner should never see an advanced-only beach ahead of a suitable one.
    if level_no_match:
        score = min(score, 15)

    return {
        "beach_id": beach.id,
        "beach_name": beach.name,
        "score": score,
        "reasons": reasons,
        "warnings": warnings,
        "hazards": beach.hazards,
        "notes": beach.notes,
        "whatsapp_groups": beach.whatsapp_groups,
        "latitude": beach.latitude,
        "longitude": beach.longitude,
    }


def recommend_beaches(
    beaches: list[Beach],
    wind_speed: float,
    wind_direction: str,
    tide_state: str,
    tide_direction: str,
    rider_level: str,
    top_n: int = 5,
) -> list[dict]:
    scored = [
        score_beach(beach, wind_speed, wind_direction, tide_state, tide_direction, rider_level)
        for beach in beaches
    ]
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_n]
