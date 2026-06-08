from dotenv import load_dotenv
load_dotenv()

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import beaches
from backend.routers.forecast import router as forecast_router
from admin.router import router as admin_router
from backend.database import SessionLocal
from backend.models.beach import Beach
from backend.services.marine import get_marine


async def _warm_marine_cache():
    """Pre-fetch marine data for all beaches so cold-start doesn't serve blank chips."""
    try:
        db = SessionLocal()
        all_beaches = db.query(Beach).all()
        db.close()
        await asyncio.gather(*[get_marine(b.latitude, b.longitude) for b in all_beaches])
        print(f"Marine cache warmed for {len(all_beaches)} beaches.")
    except Exception as e:
        print(f"Marine cache warm-up failed (non-fatal): {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(_warm_marine_cache())
    yield


app = FastAPI(title="South Coast Kitesurf Agent", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(beaches.router)
app.include_router(forecast_router)
app.include_router(admin_router)

@app.get("/")
def root():
    return {"status": "ok", "message": "South Coast Kitesurf Agent API"}

@app.get("/_ea_test")
async def ea_test():
    """Temporary: check if Railway can reach the EA bathing water API."""
    import httpx
    url = "https://environment.data.gov.uk/doc/bathing-water-quality/advice-against-bathing/situations.json?_limit=3"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            return {"status": r.status_code, "body_preview": r.text[:500]}
    except Exception as e:
        return {"error": str(e)}
