from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from backend.database import Base


class ApiEvent(Base):
    __tablename__ = "api_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)   # "beach_forecast" | "recommend"
    beach_id = Column(Integer, nullable=True)
    beach_name = Column(String, nullable=True)
    rider_level = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
