import httpx
import math
import json
from datetime import datetime, timezone, timedelta

ENDPOINTS = {
    "sww": "https://services-eu1.arcgis.com/OMdMOtfhATJPcHe3/arcgis/rest/services/NEH_outlets_PROD/FeatureServer/0/query",
    "southern": "https://services-eu1.arcgis.com/6qJmARkS2dt2IjVA/arcgis/rest/services/SouthernWater_StormOverflowActivity_PROD_view/FeatureServer/0/query",
    "wessex": "https://services.arcgis.com/3SZ6e0uCvPROr4mS/arcgis/rest/services/Wessex_Water_Storm_Overflow_Activity/FeatureServer/0/query",
}

CACHE_TTL_MINUTES = 15
SEARCH_RADIUS_M       = 8000  # find monitors within 8km (for coverage + nearest_overflow_m)
FLAG_RADIUS_ACTIVE_M  = 8000  # raise 'discharging' alert for active (status=1) within 8km
FLAG_RADIUS_RECENT_M  = 2000  # raise 'recent_spill' alert for stopped (status=0) within 2km only
BBOX_DEG = 0.08               # ~8km bounding box half-width (fetched from ArcGIS)
RECENT_HOURS = 48

# Per-location cache keyed by (company, rounded_lat, rounded_lon)
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
    for key in keys:
        if key in attrs:
            return attrs[key]
    return None


async def _fetch_nearby(company: str, lat: float, lon: float) -> list:
    """Fetch overflows within BBOX_DEG of the given location, with per-location caching."""
    cache_key = (company, round(lat, 2), round(lon, 2))
    now = datetime.now(timezone.utc)

    if cache_key in _cache:
        fetched_at, features = _cache[cache_key]
        if now - fetched_at < timedelta(minutes=CACHE_TTL_MINUTES):
            return features

    bbox = {
        "xmin": lon - BBOX_DEG,
        "ymin": lat - BBOX_DEG,
        "xmax": lon + BBOX_DEG,
        "ymax": lat + BBOX_DEG,
    }
    params = {
        "where": "1=1",
        "geometry": json.dumps(bbox),
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "status,Status,latitude,Latitude,longitude,Longitude,latestEventStart,LatestEventStart,latestEventEnd,LatestEventEnd",
        "f": "json",
        "returnGeometry": "false",
        "resultRecordCount": 200,
    }
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; SouthWestKitesurf/1.0; +https://southwestkitesurf.co.uk)"}
        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            resp = await client.get(ENDPOINTS[company], params=params)
            if resp.status_code != 200:
                return _cache.get(cache_key, (None, []))[1] or []
            data = resp.json()
        features = [f["attributes"] for f in data.get("features", [])]
        _cache[cache_key] = (now, features)
        return features
    except Exception as e:
        print(f"Sewage fetch failed ({company} near {lat},{lon}): {e}")
        return _cache.get(cache_key, (None, []))[1] or []


async def get_sewage_status(lat: float, lon: float) -> dict:
    """Return sewage status for overflows near the beach.

    Three-tier radius system:
    - SEARCH_RADIUS_M (8km): finds monitors to confirm coverage exists.
    - FLAG_RADIUS_ACTIVE_M (8km): raises 'discharging' for any status=1 within 8km.
      Active discharges affect water quality over a wide area via tidal/river flow.
    - FLAG_RADIUS_RECENT_M (2km): raises 'recent_spill' for stopped status=0 within 2km only.
      Tight radius avoids false positives from inland streams 2-5km away.
    - 'clear'   = monitors found within 8km, none flagged.
    - 'unknown' = no monitors at all within 8km (no data for this area).
    """
    company = _water_company(lon)
    features = await _fetch_nearby(company, lat, lon)

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

    active_discharge = False
    recent_spill = False
    discharge_started = None
    discharge_ended = None

    for dist, f in nearby:
        status = _attr(f, "status", "Status")
        event_start = _attr(f, "latestEventStart", "LatestEventStart")
        event_end = _attr(f, "latestEventEnd", "LatestEventEnd")

        if status == 1 and dist <= FLAG_RADIUS_ACTIVE_M:
            active_discharge = True
            if event_start:
                discharge_started = datetime.fromtimestamp(event_start / 1000, tz=timezone.utc).isoformat()
        elif status == 0 and dist <= FLAG_RADIUS_RECENT_M:
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
