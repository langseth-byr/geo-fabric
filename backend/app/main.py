from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.db import engine

app = FastAPI(title="GeoFabric", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Health check — verifies the API is running and PostGIS is reachable."""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT PostGIS_Version()"))
            postgis_version = result.scalar()
        return {"status": "ok", "postgis": postgis_version}
    except Exception:
        return {"status": "degraded", "postgis": None}
