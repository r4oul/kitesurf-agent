"""Runs on startup: creates tables and seeds beaches if empty."""
from backend.database import engine, Base, SessionLocal
from backend.models.beach import Beach
from backend.models.event import ApiEvent  # noqa: F401 — ensures table is created
from sqlalchemy.orm.attributes import flag_modified

Base.metadata.create_all(bind=engine)

import subprocess, sys
print("Seeding beaches (skips existing)...")
subprocess.run([sys.executable, "seed_beaches.py"])

db = SessionLocal()

# One-time fix: remove W and NW from Exmouth's wind directions
exmouth = db.query(Beach).filter(Beach.name == "Exmouth").first()
if exmouth and any(d in (exmouth.wind_directions or []) for d in ["W", "NW"]):
    exmouth.wind_directions = [d for d in exmouth.wind_directions if d not in ("W", "NW")]
    flag_modified(exmouth, "wind_directions")
    db.commit()
    print("Fixed Exmouth wind directions.")

# One-time fix: remove outgoing from Duckpond's tide_directions (lagoon drains on ebb)
duckpond = db.query(Beach).filter(Beach.name == "Duckpond (Exmouth)").first()
if duckpond and "outgoing" in (duckpond.tide_directions or []):
    duckpond.tide_directions = [d for d in duckpond.tide_directions if d != "outgoing"]
    flag_modified(duckpond, "tide_directions")
    db.commit()
    print("Fixed Duckpond tide directions.")

# One-time fix: correct Hayling Island wind/tide/level data based on research
hayling = db.query(Beach).filter(Beach.name == "Hayling Island").first()
if hayling and set(hayling.tide_states or []) == {"mid", "high"}:
    hayling.wind_directions = ["E", "SE", "S", "SW"]
    hayling.tide_states = ["low", "mid"]
    hayling.rider_levels = ["beginner", "intermediate", "advanced"]
    hayling.hazards = "Concrete blocks, groynes and submerged rocks to the east. Portsmouth-Hayling ferry crossing to east. High tide shrinks beach significantly — leave 3hr gap either side of HW."
    hayling.notes = "East Winner sandbar appears ~4hrs either side of low tide creating 1km+ flat shallow lagoon — excellent for beginners. Wide wind arc E-SW. CBK is sole school, can run in most directions. Best Apr–Oct."
    flag_modified(hayling, "wind_directions")
    flag_modified(hayling, "tide_states")
    flag_modified(hayling, "rider_levels")
    db.commit()
    print("Fixed Hayling Island data.")

# Follow-up fix: ensure 'mid' is present in Hayling Island tide_states
# (previous patch was skipped if tides had already been partially changed via admin)
if hayling and "mid" not in (hayling.tide_states or []):
    hayling.tide_states = ["low", "mid"]
    flag_modified(hayling, "tide_states")
    db.commit()
    print("Fixed Hayling Island: added missing 'mid' tide state.")

# One-time fix: correct West Wittering wind/tide/level data based on research
west_wittering = db.query(Beach).filter(Beach.name == "West Wittering").first()
if west_wittering and set(west_wittering.tide_states or []) == {"mid", "high"}:
    west_wittering.wind_directions = ["E", "SW", "W", "NW"]
    west_wittering.tide_states = ["low", "mid", "high"]
    west_wittering.rider_levels = ["beginner", "intermediate", "advanced"]
    west_wittering.hazards = "Timber groynes on east side — stay upwind on approach. Easterly wind on outgoing tide creates strong current toward groynes. Very busy in summer."
    west_wittering.notes = "All tides work but differently: low tide exposes flat sandbar lagoon (beginners/freestyle), mid is all-round, high produces waves (advanced). SW is classic sideonshore. E (port tack) is excellent on incoming tide. NW is cross-offshore — experienced only. Pre-book car park."
    flag_modified(west_wittering, "wind_directions")
    flag_modified(west_wittering, "tide_states")
    flag_modified(west_wittering, "rider_levels")
    db.commit()
    print("Fixed West Wittering data.")

# One-time fix: correct Calshot wind/tide data based on research (W removed, NE/SE added)
calshot = db.query(Beach).filter(Beach.name == "Calshot").first()
if calshot and "W" in (calshot.wind_directions or []):
    calshot.wind_directions = ["NE", "SE", "S", "SW"]
    calshot.tide_states = ["low", "mid"]
    calshot.hazards = "Active shipping lane through Southampton Water — never kite in the channel. Strong tidal flow around spit tip, especially on ebb. NW and W winds are offshore/unsafe here."
    calshot.notes = "Shingle spit at mouth of Southampton Water. Sheltered flat water on inside (Southampton Water side), choppier outside (Solent). One of the only Solent spots that works in NE/N. SW funnelled by IoW can be very strong in afternoon. NW and W do not work. Calshot Activities Centre membership/day pass required."
    flag_modified(calshot, "wind_directions")
    flag_modified(calshot, "tide_states")
    db.commit()
    print("Fixed Calshot data.")

# One-time fix: correct Bantham tide states — low & mid, not mid & high
bantham = db.query(Beach).filter(Beach.name == "Bantham").first()
if bantham and "high" in (bantham.tide_states or []):
    bantham.tide_states = ["low", "mid"]
    bantham.hazards = "River Avon mouth rip — strong tidal current on ebb · High tide shrinks beach, avoid last 2hrs of flood · Rocks to south of bay · No lifeguard cover"
    bantham.notes = "Expert wave spot. Low to mid tide essential — at high water the beach narrows and river mouth becomes turbulent. SW 20-30kt with 2-3ft swell produces excellent right-handers. Check tide tables carefully."
    flag_modified(bantham, "tide_states")
    db.commit()
    print("Fixed Bantham tide states.")

# One-time fix: correct Dawlish Warren wind directions — W, NW, N only (not SW or S)
dawlish = db.query(Beach).filter(Beach.name == "Dawlish Warren").first()
if dawlish and any(d in (dawlish.wind_directions or []) for d in ["SW", "S"]):
    dawlish.wind_directions = ["W", "NW", "N"]
    dawlish.hazards = "National Nature Reserve SSSI — kite only in designated zone, no launching over dune vegetation · Sandbanks dry at low tide · Strong tidal current in Exe channel · Ferries cross estuary mouth"
    dawlish.notes = "NW funnelled by Exe estuary gives clean side-shore conditions. W and N also work. Best 2hrs either side of high tide. Quieter and less crowded than Exmouth beach."
    flag_modified(dawlish, "wind_directions")
    db.commit()
    print("Fixed Dawlish Warren wind directions.")

# Fix: remove WhatsApp group incorrectly added to Portland Harbour
portland = db.query(Beach).filter(Beach.name == "Portland Harbour").first()
if portland and any(g.get("invite_link", "").startswith("https://chat.whatsapp.com/KKUAkjNw5zYKkmPmkpTcE4") for g in (portland.whatsapp_groups or [])):
    portland.whatsapp_groups = []
    flag_modified(portland, "whatsapp_groups")
    db.commit()
    print("Removed incorrect WhatsApp group from Portland Harbour.")

# One-time fix: add WhatsApp group for Westward Ho!
westward_ho = db.query(Beach).filter(Beach.name == "Westward Ho!").first()
if westward_ho and not any(g.get("invite_link", "").startswith("https://chat.whatsapp.com/KKUAkjNw5zYKkmPmkpTcE4") for g in (westward_ho.whatsapp_groups or [])):
    westward_ho.whatsapp_groups = [{"name": "Westward Ho! Kiters", "invite_link": "https://chat.whatsapp.com/KKUAkjNw5zYKkmPmkpTcE4"}]
    flag_modified(westward_ho, "whatsapp_groups")
    db.commit()
    print("Added Westward Ho! WhatsApp group.")

db.close()
print("Startup complete.")
