from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from backend.database import get_db
from backend.models.click import OutboundClick
from backend.limiter import limiter

router = APIRouter(prefix="/api/track", tags=["tracking"])


class ClickIn(BaseModel):
    page: str = Field(..., max_length=100)
    url: str = Field(..., max_length=500)
    label: Optional[str] = Field(None, max_length=200)


@router.post("/click", status_code=204)
@limiter.limit("30/minute")
def track_click(request: Request, click: ClickIn, db: Session = Depends(get_db)):
    """Log a click on an outbound link from a guide page (e.g. a kite school link).
    Public, write-only — called via sendBeacon from the static guide pages."""
    db.add(OutboundClick(
        page_slug=click.page[:100],
        link_url=click.url[:500],
        link_label=(click.label or None),
    ))
    db.commit()
    return Response(status_code=204)
