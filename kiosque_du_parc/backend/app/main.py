"""
KIOSQUE DU PARC - FastAPI Backend
Main application entry point.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path

from app.db import init_db, SessionLocal
from app.seed import seed_database
from app.settings import BASE_DIR, FRONTEND_DIR, DEBUG
from app.routers import api, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("[STARTUP] Initializing database...")
    init_db()

    # Seed database with initial data
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    print("[STARTUP] Application ready!")
    print(f"[STARTUP] Frontend: http://127.0.0.1:8000/")
    print(f"[STARTUP] Admin: http://127.0.0.1:8000/admin")

    yield

    # Shutdown
    print("[SHUTDOWN] Application stopped.")


# Create FastAPI app
app = FastAPI(
    title="KIOSQUE DU PARC",
    description="Backend API for the KIOSQUE DU PARC foodtruck website",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None
)

# Include routers
app.include_router(api.router)
app.include_router(admin.router)

# Mount static files for admin CSS
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Mount frontend assets (images, css, js from the frontend)
frontend_assets = FRONTEND_DIR / "assets"
if frontend_assets.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_assets)), name="frontend_assets")


@app.get("/", response_class=FileResponse)
def serve_frontend():
    """Serve the frontend index.html."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"error": "Frontend not found. Place index.html in the parent directory."}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "app": "KIOSQUE DU PARC"}


# For running with: python -m app.main
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=DEBUG)
