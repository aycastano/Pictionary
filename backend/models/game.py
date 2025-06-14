from pydantic import BaseModel
from typing import List, Dict

class Player(BaseModel):
    name: str

class GameState(BaseModel):
    players: List[Player] = []
    word: str = "house"
    scores: Dict[str, int] = {} 