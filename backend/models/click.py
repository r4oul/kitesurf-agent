from sqlalchemy import Column, Integer, String, DateTime, Index
from datetime import datetime, timezone
from backend.database import Base


class OutboundClick(Base):
    """A click on an outbound link from a guide page (e.g. a local kite school)."""
    __tablename__ = "outbound_clicks"

    id = Column(Integer, primary_key=True, index=True)
    page_slug = Column(String, nullable=False)      # e.g. "duckpond-exmouth"
    link_label = Column(String, nullable=True)       # e.g. "Edge Watersports"
    link_url = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_outbound_clicks_page_created", "page_slug", "created_at"),
    )
