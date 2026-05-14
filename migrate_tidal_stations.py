"""
One-time migration: add tide_station and tide_constituents columns,
then populate them for all existing beaches.

Run once with: python migrate_tidal_stations.py
"""
import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

from backend.database import engine, SessionLocal
from backend.models.beach import Beach
from backend.services.tidal_stations import find_nearest_station
from sqlalchemy.orm.attributes import flag_modified

# --- Add columns if they don't exist ---
with engine.connect() as conn:
    db_url = str(engine.url)
    if "sqlite" in db_url:
        existing = [row[1] for row in conn.execute(text("PRAGMA table_info(beaches)"))]
        if "tide_station" not in existing:
            conn.execute(text("ALTER TABLE beaches ADD COLUMN tide_station VARCHAR"))
            print("Added tide_station column")
        if "tide_constituents" not in existing:
            conn.execute(text("ALTER TABLE beaches ADD COLUMN tide_constituents JSON"))
            print("Added tide_constituents column")
    else:
        # PostgreSQL — add columns if not present
        for col, typ in [("tide_station", "VARCHAR"), ("tide_constituents", "JSONB")]:
            try:
                conn.execute(text(f"ALTER TABLE beaches ADD COLUMN {col} {typ}"))
                print(f"Added {col} column")
            except Exception:
                print(f"Column {col} already exists, skipping")
    conn.commit()

# --- Populate constituents for all existing beaches ---
db = SessionLocal()
beaches = db.query(Beach).all()
updated = 0
for beach in beaches:
    station = find_nearest_station(beach.latitude, beach.longitude)
    beach.tide_station = station["name"]
    beach.tide_constituents = station["constituents"]
    flag_modified(beach, "tide_constituents")
    updated += 1
    print(f"  {beach.name} → {station['name']}")

db.commit()
db.close()
print(f"\nDone. Updated {updated} beach(es).")
