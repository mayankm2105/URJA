"""
Net Zero Progress & Carbon Intelligence Tracker
FastAPI Backend — Main Entry Point
"""
import sys
import os
from contextlib import asynccontextmanager

# Ensure the backend package is importable regardless of CWD
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _BACKEND_DIR)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routers import dashboard, emissions, fleet, routes, ai_agent
from seed import seed_database


# ─── Lifespan (replaces deprecated @app.on_event) ────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and seed data
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield
    # Shutdown: nothing to clean up


app = FastAPI(
    title="Net Zero Carbon Intelligence Tracker API",
    description="Geospatial AI layer for fleet electrification & carbon tracking",
    version="1.0.0",
    lifespan=lifespan,
)

allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if allowed_origins_env:
    origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
else:
    origins = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(emissions.router, prefix="/api", tags=["Emissions"])
app.include_router(fleet.router, prefix="/api", tags=["Fleet"])
app.include_router(routes.router, prefix="/api", tags=["Routes"])
app.include_router(ai_agent.router, prefix="/api", tags=["AI Agent"])

@app.get("/health")
def health():
    return {"status": "ok"}


# Mount static files for the frontend - MUST be declared last to avoid hijacking specific paths
from fastapi.staticfiles import StaticFiles
_FRONTEND_DIR = os.path.join(os.path.dirname(_BACKEND_DIR), "frontend")
app.mount("/", StaticFiles(directory=_FRONTEND_DIR, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    # Port is configurable via the PORT env var so the unified platform launcher
    # can run this alongside the other modules without collisions.
    _port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=_port, reload=True)
