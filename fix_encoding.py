"""Fix em-dash encoding in stored beach notes and hazards."""
from backend.database import SessionLocal
from backend.models.beach import Beach

db = SessionLocal()
beaches = db.query(Beach).all()
fixed = 0
for beach in beaches:
    changed = False
    if beach.notes and '\u2014' in beach.notes:
        beach.notes = beach.notes.replace('\u2014', '-')
        changed = True
    if beach.notes and '\u2013' in beach.notes:
        beach.notes = beach.notes.replace('\u2013', '-')
        changed = True
    if beach.hazards and '\u2014' in beach.hazards:
        beach.hazards = beach.hazards.replace('\u2014', '-')
        changed = True
    if beach.hazards and '\u2013' in beach.hazards:
        beach.hazards = beach.hazards.replace('\u2013', '-')
        changed = True
    if changed:
        fixed += 1

db.commit()
db.close()
print(f"Fixed {fixed} beaches.")
