from sqlalchemy import Column, Integer, String, Float, JSON
from backend.database import Base

class Beach(Base):
    __tablename__ = "beaches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    wind_directions = Column(JSON)        # e.g. ["SW", "W", "NW"]
    wind_speed_min = Column(Integer)      # knots
    wind_speed_max = Column(Integer)      # knots
    tide_states = Column(JSON)            # e.g. ["mid", "high"]
    tide_directions = Column(JSON)        # e.g. ["incoming", "slack"]
    rider_levels = Column(JSON)           # e.g. ["beginner", "intermediate"]
    hazards = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    whatsapp_groups = Column(JSON)        # e.g. [{"name": "...", "invite_link": "..."}]
    tide_station = Column(String, nullable=True)   # nearest BODC reference station name
    tide_constituents = Column(JSON, nullable=True) # harmonic constants for local prediction
