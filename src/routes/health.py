from fastapi import APIRouter
from src.response_manager import ResponseManager

router = APIRouter()

@router.get('/health', name="Health check of the API", responses=ResponseManager.responses)
async def get_health():
    """_summary_
    \n
    Request to check the API's health
    \n
    Returns:
        JSON : Current state of the API
    """
    return {'state': 'API is currently running. Please proceed'}