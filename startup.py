"""Runs on startup: creates tables and seeds beaches if empty."""
from backend.database import engine, Base, SessionLocal
from backend.models.beach import Beach

Base.metadata.create_all(bind=engine)

db = SessionLocal()
if db.query(Beach).count() == 0:
    print("Seeding beaches...")
    import subprocess, sys
    subprocess.run([sys.executable, "seed_beaches.py"])
db.close()
print("Startup complete.")
