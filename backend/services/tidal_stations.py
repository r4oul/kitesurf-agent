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
        # [computed] Grid-searched against tidetimes.org.uk 2026-06-29 BST→UTC:
        #   L 05:20, H 12:10, L 17:30; RMS 2.9 min.
        "constituents": {
            "Z0": 2.65,
            "M2":  {"amp": 1.55, "phase": 322.0},
            "S2":  {"amp": 0.55, "phase": 340.0},
            "N2":  {"amp": 0.29, "phase": 292.0},
            "K2":  {"amp": 0.15, "phase": 340.0},
            "K1":  {"amp": 0.07, "phase": 258.0},
            "O1":  {"amp": 0.05, "phase": 265.0},
            "M4":  {"amp": 0.10, "phase": 40.0},
        },
    },
    {
        "name": "Portsmouth",
        "lat": 50.80,
        "lon": -1.11,
        # Admiralty: MHWS 4.7, MHWN 3.8, MLWN 1.9, MLWS 0.8
        # [computed] Grid-searched against tidetimes.org.uk 2026-07-13 BST→UTC.
        # Jul-19 correction (+44 min) overshot: 2026-08-25 check showed predictions
        # running +22 to +39 min LATE (avg +29) vs tidetimes.org.uk across all 4
        # daily extremes. Phases shifted -29 min to compensate.
        # -29 min → M2-14.0°, S2-14.5°, N2-13.7°, K2-14.5°, K1-7.3°, O1-6.7°,
        # M4-28.0°, MS4-28.5°. Single-day snapshot — second data point pending.
        "constituents": {
            "Z0": 2.80,
            "M2":  {"amp": 1.45, "phase": 319.3},
            "S2":  {"amp": 0.50, "phase": 344.5},
            "N2":  {"amp": 0.28, "phase": 296.2},
            "K2":  {"amp": 0.14, "phase": 344.6},
            "K1":  {"amp": 0.07, "phase": 343.7},
            "O1":  {"amp": 0.05, "phase": 303.5},
            "M4":  {"amp": 0.10, "phase": 44.5},
            "MS4": {"amp": 0.06, "phase": 330.8},
        },
    },
    {
        "name": "Southampton",
        "lat": 50.90,
        "lon": -1.40,
        # Admiralty: MHWS 4.5, MHWN 3.7, MLWN 2.0, MLWS 1.1
        # Double HW — large M4/MS4 terms create 5-extreme/day pattern our model can't fully
        # reproduce. g=37° derived from observed HW 01:31 BST Jun29 (M2-only fit).
        # S2/N2/K2/M4/MS4 phases kept from original calibration (changing only M2).
        # Gives HW ±10 min; LW ~2.5h off (inherent limitation without M6/2MN4 harmonics).
        "constituents": {
            "Z0": 2.83,
            "M2":  {"amp": 1.28, "phase": 37.0},
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
        # [computed] Grid-searched against tidetimes.org.uk 2026-06-29 BST→UTC:
        #   L 04:40, H 11:19, L 16:58, H 23:24; RMS 5.5 min (errs 0,-9,+2,+6).
        "constituents": {
            "Z0": 1.78,
            "M2":  {"amp": 0.93, "phase": 314.0},
            "S2":  {"amp": 0.33, "phase": 263.0},
            "N2":  {"amp": 0.18, "phase": 219.0},
            "K1":  {"amp": 0.06, "phase": 255.0},
            "O1":  {"amp": 0.04, "phase": 262.0},
            "M4":  {"amp": 0.08, "phase": 300.0},
        },
    },
    {
        "name": "Poole",
        "lat": 50.72,
        "lon": -1.99,
        # Admiralty: MHWS 2.0, MHWN 1.5, MLWN 1.0, MLWS 0.6
        # Double HW — large M4 term relative to M2
        # [computed] Grid-searched against tidetimes.org.uk 2026-06-29 BST→UTC;
        #   HW-only matching (double HW complex); RMS 19.4 min.
        "constituents": {
            "Z0": 1.28,
            "M2":  {"amp": 0.45, "phase": 244.0},
            "S2":  {"amp": 0.13, "phase": 242.0},
            "N2":  {"amp": 0.09, "phase": 197.0},
            "K1":  {"amp": 0.05, "phase": 250.0},
            "O1":  {"amp": 0.04, "phase": 260.0},
            "M4":  {"amp": 0.08, "phase": 150.0},
            "MS4": {"amp": 0.08, "phase": 245.0},
        },
    },
    {
        "name": "Swanage",
        "lat": 50.61,
        "lon": -1.95,
        # Admiralty: MHWS 2.1, MHWN 1.6, MLWN 0.8, MLWS 0.4
        # [computed] Grid-searched against tidetimes.org.uk 2026-07-13 BST→UTC:
        #   L 01:57, H 07:49, L 14:20, H 20:01; RMS 13.9 min (errs -17,+11,0,+19).
        # Previous M2=263°/S2=206° gave 26 min RMS. LW asymmetry inherently limits accuracy.
        "constituents": {
            "Z0": 1.23,
            "M2":  {"amp": 0.53, "phase": 258.0},
            "S2":  {"amp": 0.19, "phase": 290.0},
            "N2":  {"amp": 0.10, "phase": 235.0},
            "K1":  {"amp": 0.06, "phase": 340.0},
            "O1":  {"amp": 0.04, "phase": 300.0},
            "M4":  {"amp": 0.10, "phase": 60.0},
        },
    },
    {
        "name": "Portland",
        "lat": 50.57,
        "lon": -2.44,
        # Admiralty Standard Port: MHWS 2.1, MHWN 1.4, MLWN 0.5, MLWS 0.1
        # [computed] Grid-searched against tidetimes.org.uk 2026-07-13 BST→UTC: RMS 3.4 min.
        # Single-day +30 min correction (Jul 19) was reverted: oscillated to +62 min on Jul 21.
        # Spring-neap S2 beat causes ±30 min natural oscillation — M2 phase is correct on average.
        "constituents": {
            "Z0": 1.03,
            "M2":  {"amp": 0.73, "phase": 165.0},
            "S2":  {"amp": 0.24, "phase": 200.0},
            "N2":  {"amp": 0.14, "phase": 142.0},
            "K2":  {"amp": 0.06, "phase": 200.0},
            "K1":  {"amp": 0.07, "phase": 340.0},
            "O1":  {"amp": 0.04, "phase": 300.0},
            "M4":  {"amp": 0.15, "phase": 90.0},
        },
    },
    {
        "name": "Lyme Regis",
        "lat": 50.72,
        "lon": -2.94,
        # Admiralty: MHWS 4.1, MHWN 2.9, MLWN 1.3, MLWS 0.5
        # [computed] Grid-searched against tidetimes.org.uk 2026-06-29 BST→UTC.
        # Three-point calibration (Jul-19 -36, Jul-21 back-calc +13, Aug-01 -51):
        # midpoint systematic bias = -19 min → +19 min correction applied.
        # Irreducible spring-neap S2 beat residual = ±32 min (BODC constants needed for fix).
        "constituents": {
            "Z0": 2.20,
            "M2":  {"amp": 1.30, "phase": 179.2},
            "S2":  {"amp": 0.50, "phase": 191.5},
            "N2":  {"amp": 0.25, "phase": 147.0},
            "K2":  {"amp": 0.14, "phase": 191.5},
            "K1":  {"amp": 0.07, "phase": 272.8},
            "O1":  {"amp": 0.05, "phase": 276.4},
            "M4":  {"amp": 0.10, "phase": 138.4},
        },
    },
    {
        "name": "Exmouth",
        "lat": 50.62,
        "lon": -3.42,
        # Admiralty: MHWS 4.4, MHWN 3.3, MLWN 1.5, MLWS 0.5
        # Jul-17 correction (+72 min) overshot badly: 2026-08-25 check showed
        # predictions running +58 to +85 min LATE (avg +68.5) vs tidetimes.org.uk
        # (Exmouth Dock) across all 4 daily extremes — the original single-point
        # fix looks to have been based on a bad reading. Phases shifted -68.5 min.
        # -68.5 min → M2-33.1°, S2-34.2°, N2-32.5°, K2-34.3°, K1-17.2°, O1-15.9°,
        # M4-66.2°. Single-day snapshot — second data point pending; also feeds
        # Dawlish Warren and Duckpond (Exmouth) via nearest-station fallback.
        "constituents": {
            "Z0": 2.43,
            "M2":  {"amp": 1.43, "phase": 170.7},
            "S2":  {"amp": 0.53, "phase": 201.8},
            "N2":  {"amp": 0.27, "phase": 157.6},
            "K2":  {"amp": 0.14, "phase": 201.8},
            "K1":  {"amp": 0.08, "phase": 262.9},
            "O1":  {"amp": 0.05, "phase": 267.8},
            "M4":  {"amp": 0.07, "phase": 160.4},
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
        # [computed] M2 phase recalibrated against tidetimes.org.uk 2026-06-29 (BST→UTC).
        # Single-day +38 min correction (Jul 19) was reverted: oscillated to +85 min on Jul 21.
        # Spring-neap S2 beat causes ±47 min natural oscillation — M2 phase is correct on average.
        "constituents": {
            "Z0": 2.85,
            "M2":  {"amp": 1.55, "phase": 169.0},
            "S2":  {"amp": 0.60, "phase": 162.0},
            "N2":  {"amp": 0.29, "phase": 117.0},
            "K1":  {"amp": 0.08, "phase": 255.0},
            "O1":  {"amp": 0.05, "phase": 260.0},
            "M4":  {"amp": 0.07, "phase": 175.0},
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
    {
        "name": "Padstow",
        "lat": 50.54,
        "lon": -4.94,
        # Admiralty: MHWS 6.5, MHWN 5.0, MLWN 2.4, MLWS 0.8
        # [computed] Grid-searched against tidetimes.org.uk 2026-07-13 BST→UTC:
        #   H 03:55, L 10:25, H 16:22, L 22:59; RMS 10.2 min (errs +5,-5,-2,-19).
        # Covers Daymer Bay, Watergate Bay, Fistral Beach, Perranporth (N Cornwall).
        # Replaces Plymouth [estimated] which was potentially 45+ min out for these spots.
        "constituents": {
            "Z0": 3.675,
            "M2":  {"amp": 2.075, "phase": 144.0},
            "S2":  {"amp": 0.775, "phase": 176.0},
            "N2":  {"amp": 0.394, "phase": 121.0},
            "K2":  {"amp": 0.209, "phase": 176.0},
            "K1":  {"amp": 0.10,  "phase": 340.0},
            "O1":  {"amp": 0.07,  "phase": 300.0},
        },
    },
    {
        "name": "St Ives",
        "lat": 50.21,
        "lon": -5.48,
        # Admiralty: MHWS 6.2, MHWN 4.7, MLWN 2.2, MLWS 0.7
        # [computed] Grid-searched against tidetimes.org.uk 2026-07-13 BST→UTC:
        #   H 03:41, L 10:11, H 16:06, L 22:42; RMS 9.5 min (errs +9,-11,+4,-12).
        # Covers Gwithian, The Bluff (Hayle), Marazion, Praa Sands (W Cornwall).
        # Replaces Plymouth [estimated] which was potentially 45+ min out for these spots.
        "constituents": {
            "Z0": 3.45,
            "M2":  {"amp": 2.0,    "phase": 140.0},
            "S2":  {"amp": 0.75,   "phase": 164.0},
            "N2":  {"amp": 0.38,   "phase": 117.0},
            "K2":  {"amp": 0.2025, "phase": 164.0},
            "K1":  {"amp": 0.09,   "phase": 340.0},
            "O1":  {"amp": 0.06,   "phase": 300.0},
        },
    },
    {
        "name": "Weston-super-Mare",
        "lat": 51.35,
        "lon": -2.97,
        # Admiralty: MHWS 12.3, MHWN 9.1, MLWN 3.6, MLWS 0.9  (second largest range in world)
        # Z0 = (12.3+9.1+3.6+0.9)/4 = 6.725m
        # M2/S2 from tidal range formula; N2 = M2×0.19, K2 = S2×0.27.
        # [computed] Grid-searched against tidetimes.org.uk 2026-06-29 BST→UTC.
        # Two-point averaged correction (+45.5 min) applied Jul 21 didn't hold:
        # 2026-08-25 check showed predictions running +45 to +64 min LATE (avg
        # +51.75) again — either continued drift or a wider beat swing than the
        # ±30-47 min assumed elsewhere. Phases shifted a further -51.75 min.
        # -51.75 min → M2-25.0°, S2-25.9°, N2-24.5°, K2-25.9°, K1-13.0°, O1-12.0°,
        # M4-50.0°. Single-day snapshot — second data point pending.
        "constituents": {
            "Z0": 6.725,
            "M2":  {"amp": 4.225, "phase": 171.0},
            "S2":  {"amp": 1.475, "phase": 216.9},
            "N2":  {"amp": 0.803, "phase": 148.0},
            "K2":  {"amp": 0.398, "phase": 216.9},
            "K1":  {"amp": 0.120, "phase": 332.4},
            "O1":  {"amp": 0.080, "phase": 306.6},
            "M4":  {"amp": 0.300, "phase": 184.0},
        },
    },
    {
        "name": "Ilfracombe",
        "lat": 51.21,
        "lon": -4.12,
        # Admiralty: MHWS 8.3, MHWN 6.1, MLWN 2.9, MLWS 1.0
        # Z0 = (MHWS+MHWN+MLWN+MLWS)/4 = 4.575m
        # M2/S2 from tidal range formula; N2 = M2×0.19, K2 = S2×0.27.
        # [computed] M2 phase grid-searched against tidetimes 2026-06-28 (BST→UTC).
        # Two-point averaged correction (+24.5 min) applied Jul 21 didn't hold:
        # 2026-08-25 check showed predictions running +20 to +31 min LATE (avg
        # +27.5) again in the same direction. Phases shifted a further -27.5 min.
        # -27.5 min → M2-13.3°, S2-13.8°, N2-13.0°, K2-13.8°, K1-6.9°, O1-6.4°,
        # M4-26.6°. Single-day snapshot — second data point pending.
        "constituents": {
            "Z0": 4.575,
            "M2":  {"amp": 2.625, "phase": 157.5},
            "S2":  {"amp": 1.025, "phase": 185.6},
            "N2":  {"amp": 0.499, "phase": 134.6},
            "K2":  {"amp": 0.277, "phase": 185.5},
            "K1":  {"amp": 0.10,  "phase": 336.2},
            "O1":  {"amp": 0.07,  "phase": 289.3},
            "M4":  {"amp": 0.06,  "phase": 197.1},
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
