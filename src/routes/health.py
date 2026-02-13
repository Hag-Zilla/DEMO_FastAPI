from fastapi import APIRouter

router = APIRouter()

@router.get('/health', name="Health check of the API")
async def get_health():
    """_summary_
    \n
    Request to check the API's health
    \n
    Returns:
        JSON : Current state of the API
    \n
    Example Response:
        {
            "state": "API is currently running. Please proceed"
        }
    """
    return {'state': 'API is currently running. Please proceed'}