from fastapi import APIRouter
from services.game_service import game_state

router = APIRouter(prefix="/api/v1")

@router.get("/state")
async def get_game_state():
    return game_state.dict()
