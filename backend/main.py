from dotenv import load_dotenv
load_dotenv()

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from backend.limiter import limiter
from backend.routers import beaches
from backend.routers.forecast import router as forecast_router
from admin.router import router as admin_router
from backend.database import SessionLocal
from backend.models.beach import Beach
from backend.services.marine import get_marine
from backend.services.windy import get_wind_forecast


async def _warm_caches():
    """Pre-fetch wind and marine data in small batches to avoid Open-Meteo 429 rate limits."""
    try:
        db = SessionLocal()
        all_beaches = db.query(Beach).all()
        db.close()

        batch_size = 5
        for i in range(0, len(all_beaches), batch_size):
            batch = all_beaches[i:i + batch_size]
            await asyncio.gather(
                *[get_wind_forecast(b.latitude, b.longitude) for b in batch],
                *[get_marine(b.latitude, b.longitude) for b in batch],
            )
            if i + batch_size < len(all_beaches):
                await asyncio.sleep(1)

        print(f"Wind + marine caches warmed for {len(all_beaches)} beaches.")
    except Exception as e:
        print(f"Cache warm-up failed (non-fatal): {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(_warm_caches())
    yield


app = FastAPI(title="South Coast Kitesurf Agent", version="0.1.0", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
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


@app.get("/healthz", include_in_schema=False)
def healthz():
    return {"status": "ok"}
