"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get('/health', name="Health check of the API")
async def get_health():
    """Check the API's health status.

    Returns:
        JSON: Current state of the API
    """
    return {'state': 'API is currently running. Please proceed'}
