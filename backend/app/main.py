from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import init_db
from app.services.ingestion.scheduler import start_scheduler, stop_scheduler
from app.routers import (
    health,
    auth,
    providers,
    pricing,
    reserved,
    kubernetes,
    network,
    calculations,
    budgets,
    recommendations,
    admin,
    export,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager — startup and shutdown."""
    # Startup
    await init_db()
    await start_scheduler()
    yield
    # Shutdown
    await stop_scheduler()


app = FastAPI(
    title="JADE Cloud Matrix API",
    description="JADE Cloud Matrix — Cloud Pricing Intelligence Engine",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# All routes under /api prefix
app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(providers.router, prefix="/api/v1/providers", tags=["providers"])
app.include_router(pricing.router, prefix="/api/v1/pricing", tags=["pricing"])
app.include_router(reserved.router, prefix="/api/v1/reserved", tags=["reserved"])
app.include_router(kubernetes.router, prefix="/api/v1/kubernetes", tags=["kubernetes"])
app.include_router(network.router, prefix="/api/v1/network", tags=["network"])
app.include_router(calculations.router, prefix="/api/v1/calculations", tags=["calculations"])
app.include_router(budgets.router, prefix="/api/v1/budgets", tags=["budgets"])
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["recommendations"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(export.router, prefix="/api/v1/export", tags=["export"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "JADE Cloud Matrix API",
        "version": "1.0.0",
        "description": "Cloud Pricing Intelligence Engine",
        "client": "Jade Global Software Pvt Ltd — Infra BU",
    }
