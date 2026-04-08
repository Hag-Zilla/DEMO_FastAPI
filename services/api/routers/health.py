"""Health check router."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..database.session import get_db

router = APIRouter(tags=["Main"])


@router.get("/health/startup", name="Startup Check")
def get_startup(request: Request):
    """Check whether the application startup phase is complete."""
    startup_complete = getattr(request.app.state, "startup_complete", False)
    if not startup_complete:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Application startup is not complete",
        )
    return {
        "status": "ok",
        "check": "startup",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health/live", name="Liveness Check")
def get_liveness():
    """Check whether the API process is alive."""
    return {
        "status": "ok",
        "check": "liveness",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health/ready", name="Readiness Check")
def get_readiness(db: Session = Depends(get_db)):
    """Check whether the API is ready to serve traffic."""
    db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "check": "readiness",
        "dependencies": {"database": "ok"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health", name="Health check of the API")
def get_health():
    """Backward-compatible health endpoint (alias of liveness)."""
    return {
        "status": "ok",
        "check": "liveness",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
