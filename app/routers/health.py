"""Health check router."""

from fastapi import APIRouter

router = APIRouter(tags=["Main"])


@router.get('/health', name="Health check of the API")
async def get_health():
    """Check the API's health status."""
    return {'state': 'API is currently running. Please proceed'}
