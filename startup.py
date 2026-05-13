"""Runs on startup: creates tables and seeds beaches if empty."""
from backend.database import engine, Base, SessionLocal
from backend.models.beach import Beach
from sqlalchemy.orm.attributes import flag_modified

Base.metadata.create_all(bind=engine)

db = SessionLocal()
if db.query(Beach).count() == 0:
    print("Seeding beaches...")
    import subprocess, sys
    subprocess.run([sys.executable, "seed_beaches.py"])
    db = SessionLocal()

# One-time fix: remove W and NW from Exmouth's wind directions
exmouth = db.query(Beach).filter(Beach.name == "Exmouth").first()
if exmouth and any(d in (exmouth.wind_directions or []) for d in ["W", "NW"]):
    exmouth.wind_directions = [d for d in exmouth.wind_directions if d not in ("W", "NW")]
    flag_modified(exmouth, "wind_directions")
    db.commit()
    print("Fixed Exmouth wind directions.")

db.close()
print("Startup complete.")
