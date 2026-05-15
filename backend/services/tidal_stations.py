"""
Harmonic constituent data for UK south coast tidal reference stations.

Amplitudes (H) and Z0 are calibrated from Admiralty MHWS/MHWN/MLWN/MLWS data:
    Z0  = (MHWS + MHWN + MLWN + MLWS) / 4
    M2  = (spring_range + neap_range) / 4
    S2  = (spring_range - neap_range) / 4

Phase lags (g) — Greenwich convention, degrees — were back-calculated from
real tide times published at tidetimes.org.uk for 2026-05-14 (BST → UTC).
Formula: at time of HW, g = (V0(M2) + ω(M2) × T) mod 360°
where T = hours since 2000-01-01 00:00 UTC, ω(M2) = 28.9841042 °/hr,
V0(M2) = 136.5° at epoch.

Stations marked [computed] used real HW data (±15 min accuracy).
Stations marked [estimated] used interpolation from neighbouring computed ports (±45 min).

S2 g = M2 g + local_S2_offset (≈ 21-31°, consistent across UK south coast).
N2 g ≈ M2 g − 23°.
K1, O1 phases kept from BODC reference values (diurnal, small amplitude, stable).
"""
import math

STATIONS: list[dict] = [
    {
        "name": "Chichester",
        "lat": 50.83,
        "lon": -0.77,
        # Admiralty: MHWS 4.6, MHWN 3.8, MLWN 1.8, MLWS 0.4
        # [estimated] Portsmouth-based + harbour entry delay ~30 min
        "constituents": {
            "Z0": 2.65,
            "M2":  {"amp": 1.55, "phase": 315.0},
            "S2":  {"amp": 0.55, "phase": 340.0},
            "N2":  {"amp": 0.29, "phase": 292.0},
            "K2":  {"amp": 0.15, "phase": 340.0},
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
        # [computed] HW at 09:02 UTC and 21:30 UTC on 2026-05-14 → g=300°
        "constituents": {
            "Z0": 2.80,
            "M2":  {"amp": 1.45, "phase": 300.0},
            "S2":  {"amp": 0.50, "phase": 328.0},
            "N2":  {"amp": 0.28, "phase": 277.0},
            "K2":  {"amp": 0.14, "phase": 328.0},
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
        # [computed] HW at 08:13 UTC and 20:43 UTC on 2026-05-14 → g=276°
        "constituents": {
            "Z0": 2.83,
            "M2":  {"amp": 1.28, "phase": 276.0},
            "S2":  {"amp": 0.43, "phase": 307.0},
            "N2":  {"amp": 0.24, "phase": 253.0},
            "K2":  {"amp": 0.12, "phase": 307.0},
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
        # [estimated] Used for western Solent/Christchurch Bay mainland beaches (Lepe, Mudeford).
        # HW at this longitude on mainland ≈ 2h before Portsmouth → g ≈ 300 - 2×28.98 = 242°.
        # Compromise between Lepe (~264°) and Mudeford/Christchurch (~210°).
        "constituents": {
            "Z0": 1.78,
            "M2":  {"amp": 0.93, "phase": 242.0},
            "S2":  {"amp": 0.33, "phase": 263.0},
            "N2":  {"amp": 0.18, "phase": 219.0},
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
        # [estimated] Interpolated between Portland (164°) and Southampton (276°)
        "constituents": {
            "Z0": 1.28,
            "M2":  {"amp": 0.45, "phase": 220.0},
            "S2":  {"amp": 0.13, "phase": 242.0},
            "N2":  {"amp": 0.09, "phase": 197.0},
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
        # [estimated] Between Portland (164°) and Poole (220°)
        "constituents": {
            "Z0": 1.23,
            "M2":  {"amp": 0.53, "phase": 184.0},
            "S2":  {"amp": 0.19, "phase": 206.0},
            "N2":  {"amp": 0.10, "phase": 161.0},
            "K1":  {"amp": 0.06, "phase": 254.0},
            "O1":  {"amp": 0.04, "phase": 262.0},
        },
    },
    {
        "name": "Portland",
        "lat": 50.57,
        "lon": -2.44,
        # Admiralty Standard Port: MHWS 2.1, MHWN 1.4, MLWN 0.5, MLWS 0.1
        # [computed] HW at 04:13 UTC and 16:55 UTC on 2026-05-14 → g=164°
        "constituents": {
            "Z0": 1.03,
            "M2":  {"amp": 0.73, "phase": 164.0},
            "S2":  {"amp": 0.24, "phase": 184.0},
            "N2":  {"amp": 0.14, "phase": 141.0},
            "K2":  {"amp": 0.06, "phase": 184.0},
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
        # [computed] HW at 04:09 UTC and 16:47 UTC on 2026-05-14 → g=161°
        "constituents": {
            "Z0": 2.20,
            "M2":  {"amp": 1.30, "phase": 161.0},
            "S2":  {"amp": 0.50, "phase": 182.0},
            "N2":  {"amp": 0.25, "phase": 138.0},
            "K2":  {"amp": 0.14, "phase": 182.0},
            "K1":  {"amp": 0.07, "phase": 268.0},
            "O1":  {"amp": 0.05, "phase": 272.0},
        },
    },
    {
        "name": "Exmouth",
        "lat": 50.62,
        "lon": -3.42,
        # Admiralty: MHWS 4.4, MHWN 3.3, MLWN 1.5, MLWS 0.5
        # [computed] User-provided HW at 03:56 UTC and 16:34 UTC → g=179°
        # (Exe estuary adds ~38° delay vs open coast at this longitude)
        "constituents": {
            "Z0": 2.43,
            "M2":  {"amp": 1.43, "phase": 179.0},
            "S2":  {"amp": 0.53, "phase": 200.0},
            "N2":  {"amp": 0.27, "phase": 156.0},
            "K2":  {"amp": 0.14, "phase": 200.0},
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
        # [estimated] Between Dartmouth (141°) and Exmouth (179°), Teign estuary adds delay
        "constituents": {
            "Z0": 2.50,
            "M2":  {"amp": 1.45, "phase": 165.0},
            "S2":  {"amp": 0.55, "phase": 186.0},
            "N2":  {"amp": 0.28, "phase": 142.0},
            "K1":  {"amp": 0.08, "phase": 260.0},
            "O1":  {"amp": 0.05, "phase": 265.0},
        },
    },
    {
        "name": "Dartmouth",
        "lat": 50.35,
        "lon": -3.57,
        # Admiralty: MHWS 4.8, MHWN 3.7, MLWN 1.9, MLWS 0.7
        # [computed] HW at 03:30 UTC and 16:04 UTC on 2026-05-14 → g=141°
        "constituents": {
            "Z0": 2.78,
            "M2":  {"amp": 1.48, "phase": 141.0},
            "S2":  {"amp": 0.58, "phase": 163.0},
            "N2":  {"amp": 0.28, "phase": 118.0},
            "K2":  {"amp": 0.16, "phase": 163.0},
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
        # [computed] HW at 03:26 UTC and 16:05 UTC on 2026-05-14 → g=140°
        "constituents": {
            "Z0": 2.85,
            "M2":  {"amp": 1.55, "phase": 140.0},
            "S2":  {"amp": 0.60, "phase": 162.0},
            "N2":  {"amp": 0.29, "phase": 117.0},
            "K1":  {"amp": 0.08, "phase": 255.0},
            "O1":  {"amp": 0.05, "phase": 260.0},
        },
    },
    {
        "name": "Plymouth",
        "lat": 50.37,
        "lon": -4.14,
        # Admiralty Standard Port: MHWS 5.5, MHWN 4.4, MLWN 2.2, MLWS 0.8
        # [estimated] Similar to Salcombe; Plymouth Sound adds slight delay vs open coast
        "constituents": {
            "Z0": 3.23,
            "M2":  {"amp": 1.73, "phase": 140.0},
            "S2":  {"amp": 0.63, "phase": 161.0},
            "N2":  {"amp": 0.33, "phase": 117.0},
            "K2":  {"amp": 0.17, "phase": 161.0},
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
