from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import beaches
from backend.routers.forecast import router as forecast_router
from admin.router import router as admin_router

app = FastAPI(title="South Coast Kitesurf Agent", version="0.1.0")

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
