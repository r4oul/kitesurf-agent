from backend.models.beach import Beach
from backend.services.tides import get_tide_state

DIRECTION_NEIGHBOURS = {
    "N":  ["N", "NNE", "NNW", "NE", "NW"],
    "NE": ["NE", "NNE", "ENE", "N", "E"],
    "E":  ["E", "ENE", "ESE", "NE", "SE"],
    "SE": ["SE", "ESE", "SSE", "E", "S"],
    "S":  ["S", "SSE", "SSW", "SE", "SW"],
    "SW": ["SW", "SSW", "WSW", "S", "W"],
    "W":  ["W", "WSW", "WNW", "SW", "NW"],
    "NW": ["NW", "WNW", "NNW", "W", "N"],
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

    if beach.wind_speed_min <= wind_speed <= beach.wind_speed_max:
        score += 50
        reasons.append(f"{wind_speed}kts is within ideal range ({beach.wind_speed_min}-{beach.wind_speed_max}kts)")
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
    if wind_direction in beach.wind_directions:
        score += 25
        reasons.append(f"Wind direction {wind_direction} is ideal")
    elif any(n in beach.wind_directions for n in neighbours):
        score += 10
        reasons.append(f"Wind direction {wind_direction} is marginal")
    else:
        warnings.append(f"Wind direction {wind_direction} not ideal for this beach")

    # --- Tide state (15 points) ---
    if tide_state in beach.tide_states:
        score += 15
        reasons.append(f"Tide state ({tide_state}) is good")
    else:
        warnings.append(f"Tide state ({tide_state}) not ideal")

    # --- Tide direction (7 points) ---
    if tide_direction in beach.tide_directions:
        score += 7
        reasons.append(f"Tide direction ({tide_direction}) is good")
    else:
        warnings.append(f"Tide direction ({tide_direction}) not ideal")

    # --- Rider level (3 points) ---
    if rider_level in beach.rider_levels:
        score += 3
        reasons.append(f"Suitable for {rider_level} riders")
    else:
        warnings.append(f"Not recommended for {rider_level} riders")

    # --- Hard cap: unrideable wind caps score at 25 ---
    if wind_too_light or wind_too_strong:
        score = min(score, 25)

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
