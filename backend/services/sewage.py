import httpx
import math
from datetime import datetime, timezone, timedelta

ENDPOINTS = {
    "sww": "https://services-eu1.arcgis.com/OMdMOtfhATJPcHe3/arcgis/rest/services/NEH_outlets_PROD/FeatureServer/0/query",
    "southern": "https://services-eu1.arcgis.com/6qJmARkS2dt2IjVA/arcgis/rest/services/SouthernWater_StormOverflowActivity_PROD_view/FeatureServer/0/query",
    "wessex": "https://services.arcgis.com/3SZ6e0uCvPROr4mS/arcgis/rest/services/Wessex_Water_Storm_Overflow_Activity/FeatureServer/0/query",
}

CACHE_TTL_MINUTES = 10
SEARCH_RADIUS_M = 5000  # only consider overflows within 5km of beach

_cache: dict = {}


def _water_company(lon: float) -> str:
    if lon > -1.85:
        return "southern"
    elif lon > -3.1:
        return "wessex"
    else:
        return "sww"


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _attr(attrs: dict, *keys):
    """Try multiple key names to handle PascalCase vs camelCase differences."""
    for key in keys:
        if key in attrs:
            return attrs[key]
    return None


async def _fetch_company(company: str) -> list:
    now = datetime.now(timezone.utc)
    if company in _cache:
        fetched_at, features = _cache[company]
        if now - fetched_at < timedelta(minutes=CACHE_TTL_MINUTES):
            return features

    params = {
        "where": "1=1",
        "outFields": "status,Status,latitude,Latitude,longitude,Longitude,latestEventStart,LatestEventStart,latestEventEnd,LatestEventEnd",
        "f": "json",
        "returnGeometry": "false",
        "resultRecordCount": 2000,
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(ENDPOINTS[company], params=params)
            if resp.status_code != 200:
                return _cache.get(company, (None, []))[1] or []
            data = resp.json()
        features = [f["attributes"] for f in data.get("features", [])]
        _cache[company] = (now, features)
        return features
    except Exception as e:
        print(f"Sewage fetch failed ({company}): {e}")
        return _cache.get(company, (None, []))[1] or []


async def get_sewage_status(lat: float, lon: float) -> dict:
    """Return sewage status for the nearest overflow point within 3km of the beach."""
    company = _water_company(lon)
    features = await _fetch_company(company)

    RECENT_HOURS = 48
    now = datetime.now(timezone.utc)

    nearby = []
    for f in features:
        f_lat = _attr(f, "latitude", "Latitude")
        f_lon = _attr(f, "longitude", "Longitude")
        if f_lat is None or f_lon is None:
            continue
        dist = _haversine_m(lat, lon, f_lat, f_lon)
        if dist <= SEARCH_RADIUS_M:
            nearby.append((dist, f))

    if not nearby:
        return {"sewage_status": "unknown"}

    nearby.sort(key=lambda x: x[0])
    nearest_dist = nearby[0][0]

    # Check all nearby overflows — flag if any is actively discharging or had a recent spill
    active_discharge = False
    recent_spill = False
    discharge_started = None
    discharge_ended = None

    for dist, f in nearby:
        status = _attr(f, "status", "Status")
        event_start = _attr(f, "latestEventStart", "LatestEventStart")
        event_end = _attr(f, "latestEventEnd", "LatestEventEnd")

        if status == 1:
            active_discharge = True
            if event_start:
                discharge_started = datetime.fromtimestamp(event_start / 1000, tz=timezone.utc).isoformat()
        elif status == 0:
            # Check if event ended within the last 48 hours
            ref_ts = event_end if event_end else event_start
            if ref_ts:
                ref_dt = datetime.fromtimestamp(ref_ts / 1000, tz=timezone.utc)
                if (now - ref_dt) < timedelta(hours=RECENT_HOURS):
                    recent_spill = True
                    if event_end:
                        discharge_ended = ref_dt.isoformat()

    if active_discharge:
        sewage_status = "discharging"
    elif recent_spill:
        sewage_status = "recent_spill"
    else:
        sewage_status = "clear"

    result = {
        "sewage_status": sewage_status,
        "nearest_overflow_m": round(nearest_dist),
    }
    if discharge_started and active_discharge:
        result["discharge_started"] = discharge_started
    if discharge_ended and recent_spill:
        result["discharge_ended"] = discharge_ended

    return result
