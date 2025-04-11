from fastapi import APIRouter
from utils import responses

router = APIRouter()

@router.get('/health', name="Health check of the API", tags=['Main'], responses=responses)
async def get_health():
    """_summary_
    \n
    Request to check the API's health
    \n
    Returns:
        JSON : Current state of the API
    """
    return {'state': 'API is currently running. Please proceed'}