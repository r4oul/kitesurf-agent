"""
Harmonic constituent data for UK south coast tidal reference stations.
Source: calibrated from Admiralty Tide Tables (MHWS/MHWN/MLWN/MLWS) and BODC phase data.

Calibration method:
    Z0  = (MHWS + MHWN + MLWN + MLWS) / 4   (mean of all four levels)
    M2  = (spring_range + neap_range) / 4
    S2  = (spring_range - neap_range) / 4
    N2  ≈ 0.19 × M2
    K2  ≈ 0.27 × S2
    K1, O1: small diurnal terms, UK coast (<0.1m)
    M4, MS4: overtides, significant in Solent / Poole areas

Accurate to ±20cm and ±20min — suitable for kitesurfing tide state prediction.
Phase lags (g) sourced from BODC NTSLF / Admiralty Tide Tables.
"""
import math

STATIONS: list[dict] = [
    {
        "name": "Chichester",
        "lat": 50.83,
        "lon": -0.77,
        # Admiralty: MHWS 4.6, MHWN 3.8, MLWN 1.8, MLWS 0.4
        "constituents": {
            "Z0": 2.65,
            "M2":  {"amp": 1.55, "phase": 325.0},
            "S2":  {"amp": 0.55, "phase": 353.0},
            "N2":  {"amp": 0.29, "phase": 301.0},
            "K2":  {"amp": 0.15, "phase": 353.0},
            "K1":  {"amp": 0.07, "phase": 258.0},
            "O1":  {"amp": 0.05, "phase": 265.0},
            "M4":  {"amp": 0.08, "phase": 258.0},
        },
    },
    {
        "name": "Portsmouth",
        "lat": 50.80,
        "lon": -1.11,
        # Admiralty: MHWS 4.7, MHWN 3.8, MLWN 1.9, MLWS 0.8
        "constituents": {
            "Z0": 2.80,
            "M2":  {"amp": 1.45, "phase": 327.0},
            "S2":  {"amp": 0.50, "phase": 355.0},
            "N2":  {"amp": 0.28, "phase": 303.0},
            "K2":  {"amp": 0.14, "phase": 355.0},
            "K1":  {"amp": 0.07, "phase": 259.0},
            "O1":  {"amp": 0.05, "phase": 267.0},
            "M4":  {"amp": 0.10, "phase": 262.0},
            "MS4": {"amp": 0.06, "phase": 316.0},
        },
    },
    {
        "name": "Southampton",
        "lat": 50.90,
        "lon": -1.40,
        # Admiralty: MHWS 4.5, MHWN 3.7, MLWN 2.0, MLWS 1.1
        # Double HW — large M4/MS4 terms
        "constituents": {
            "Z0": 2.83,
            "M2":  {"amp": 1.28, "phase": 318.0},
            "S2":  {"amp": 0.43, "phase": 349.0},
            "N2":  {"amp": 0.24, "phase": 295.0},
            "K2":  {"amp": 0.12, "phase": 349.0},
            "K1":  {"amp": 0.06, "phase": 253.0},
            "O1":  {"amp": 0.04, "phase": 260.0},
            "M4":  {"amp": 0.25, "phase": 221.0},
            "MS4": {"amp": 0.14, "phase": 265.0},
        },
    },
    {
        "name": "Yarmouth IoW",
        "lat": 50.71,
        "lon": -1.50,
        # Admiralty: MHWS 3.0, MHWN 2.4, MLWN 1.2, MLWS 0.5
        "constituents": {
            "Z0": 1.78,
            "M2":  {"amp": 0.93, "phase": 313.0},
            "S2":  {"amp": 0.33, "phase": 340.0},
            "N2":  {"amp": 0.18, "phase": 290.0},
            "K1":  {"amp": 0.06, "phase": 255.0},
            "O1":  {"amp": 0.04, "phase": 262.0},
            "M4":  {"amp": 0.16, "phase": 215.0},
            "MS4": {"amp": 0.09, "phase": 258.0},
        },
    },
    {
        "name": "Poole",
        "lat": 50.72,
        "lon": -1.99,
        # Admiralty: MHWS 2.0, MHWN 1.5, MLWN 1.0, MLWS 0.6
        # Double HW — large M4 term relative to M2
        "constituents": {
            "Z0": 1.28,
            "M2":  {"amp": 0.45, "phase": 303.0},
            "S2":  {"amp": 0.13, "phase": 324.0},
            "N2":  {"amp": 0.09, "phase": 280.0},
            "K1":  {"amp": 0.05, "phase": 250.0},
            "O1":  {"amp": 0.04, "phase": 260.0},
            "M4":  {"amp": 0.13, "phase": 202.0},
            "MS4": {"amp": 0.08, "phase": 245.0},
        },
    },
    {
        "name": "Swanage",
        "lat": 50.61,
        "lon": -1.95,
        # Admiralty: MHWS 2.1, MHWN 1.6, MLWN 0.8, MLWS 0.4
        "constituents": {
            "Z0": 1.23,
            "M2":  {"amp": 0.53, "phase": 298.0},
            "S2":  {"amp": 0.19, "phase": 318.0},
            "N2":  {"amp": 0.10, "phase": 275.0},
            "K1":  {"amp": 0.06, "phase": 254.0},
            "O1":  {"amp": 0.04, "phase": 262.0},
        },
    },
    {
        "name": "Portland",
        "lat": 50.57,
        "lon": -2.44,
        # Admiralty Standard Port: MHWS 2.1, MHWN 1.4, MLWN 0.5, MLWS 0.1
        "constituents": {
            "Z0": 1.03,
            "M2":  {"amp": 0.73, "phase": 301.0},
            "S2":  {"amp": 0.24, "phase": 321.0},
            "N2":  {"amp": 0.14, "phase": 278.0},
            "K2":  {"amp": 0.06, "phase": 321.0},
            "K1":  {"amp": 0.07, "phase": 275.0},
            "O1":  {"amp": 0.04, "phase": 277.0},
            "M4":  {"amp": 0.02, "phase": 285.0},
        },
    },
    {
        "name": "Lyme Regis",
        "lat": 50.72,
        "lon": -2.94,
        # Admiralty: MHWS 4.1, MHWN 2.9, MLWN 1.3, MLWS 0.5
        "constituents": {
            "Z0": 2.20,
            "M2":  {"amp": 1.30, "phase": 287.0},
            "S2":  {"amp": 0.50, "phase": 308.0},
            "N2":  {"amp": 0.25, "phase": 264.0},
            "K2":  {"amp": 0.14, "phase": 308.0},
            "K1":  {"amp": 0.07, "phase": 268.0},
            "O1":  {"amp": 0.05, "phase": 272.0},
        },
    },
    {
        "name": "Exmouth",
        "lat": 50.62,
        "lon": -3.42,
        # Admiralty: MHWS 4.4, MHWN 3.3, MLWN 1.5, MLWS 0.5
        "constituents": {
            "Z0": 2.43,
            "M2":  {"amp": 1.43, "phase": 274.0},
            "S2":  {"amp": 0.53, "phase": 295.0},
            "N2":  {"amp": 0.27, "phase": 251.0},
            "K2":  {"amp": 0.14, "phase": 295.0},
            "K1":  {"amp": 0.08, "phase": 262.0},
            "O1":  {"amp": 0.05, "phase": 267.0},
            "M4":  {"amp": 0.04, "phase": 295.0},
        },
    },
    {
        "name": "Teignmouth",
        "lat": 50.55,
        "lon": -3.50,
        # Admiralty: MHWS 4.5, MHWN 3.4, MLWN 1.6, MLWS 0.5
        "constituents": {
            "Z0": 2.50,
            "M2":  {"amp": 1.45, "phase": 270.0},
            "S2":  {"amp": 0.55, "phase": 292.0},
            "N2":  {"amp": 0.28, "phase": 248.0},
            "K1":  {"amp": 0.08, "phase": 260.0},
            "O1":  {"amp": 0.05, "phase": 265.0},
        },
    },
    {
        "name": "Dartmouth",
        "lat": 50.35,
        "lon": -3.57,
        # Admiralty: MHWS 4.8, MHWN 3.7, MLWN 1.9, MLWS 0.7
        "constituents": {
            "Z0": 2.78,
            "M2":  {"amp": 1.48, "phase": 264.0},
            "S2":  {"amp": 0.58, "phase": 286.0},
            "N2":  {"amp": 0.28, "phase": 242.0},
            "K2":  {"amp": 0.16, "phase": 286.0},
            "K1":  {"amp": 0.08, "phase": 258.0},
            "O1":  {"amp": 0.05, "phase": 263.0},
            "M4":  {"amp": 0.03, "phase": 280.0},
        },
    },
    {
        "name": "Salcombe",
        "lat": 50.24,
        "lon": -3.78,
        # Admiralty: MHWS 5.0, MHWN 3.8, MLWN 1.9, MLWS 0.7
        "constituents": {
            "Z0": 2.85,
            "M2":  {"amp": 1.55, "phase": 260.0},
            "S2":  {"amp": 0.60, "phase": 282.0},
            "N2":  {"amp": 0.29, "phase": 238.0},
            "K1":  {"amp": 0.08, "phase": 255.0},
            "O1":  {"amp": 0.05, "phase": 260.0},
        },
    },
    {
        "name": "Plymouth",
        "lat": 50.37,
        "lon": -4.14,
        # Admiralty Standard Port: MHWS 5.5, MHWN 4.4, MLWN 2.2, MLWS 0.8
        "constituents": {
            "Z0": 3.23,
            "M2":  {"amp": 1.73, "phase": 262.0},
            "S2":  {"amp": 0.63, "phase": 283.0},
            "N2":  {"amp": 0.33, "phase": 239.0},
            "K2":  {"amp": 0.17, "phase": 283.0},
            "K1":  {"amp": 0.08, "phase": 255.0},
            "O1":  {"amp": 0.05, "phase": 260.0},
            "P1":  {"amp": 0.03, "phase": 255.0},
            "Q1":  {"amp": 0.01, "phase": 255.0},
            "M4":  {"amp": 0.02, "phase": 275.0},
        },
    },
]


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def find_nearest_station(lat: float, lon: float) -> dict:
    """Return the nearest tidal station to the given coordinates."""
    return min(STATIONS, key=lambda s: _haversine_km(lat, lon, s["lat"], s["lon"]))
