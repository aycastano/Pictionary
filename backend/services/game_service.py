from fastapi.websockets import WebSocket
from models.game import GameState, Player
from typing import List
import json

game_state = GameState()
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

    async def handle_message(self, websocket: WebSocket, data: dict):
        action = data.get("action")
        if action == "join":
            name = data.get("name")
            game_state.players.append(Player(name=name))
            await self.broadcast({"type": "players", "players": [p.name for p in game_state.players]})
        elif action == "draw":
            await self.broadcast({"type": "draw", "stroke": data.get("stroke")})
        elif action == "guess":
            guess = data.get("guess")
            if guess.lower() == game_state.word.lower():
                game_state.scores[data["name"]] = game_state.scores.get(data["name"], 0) + 1
                await self.broadcast({"type": "correct", "player": data["name"]})
        # puedes extender con turnos, cambio de palabra, etc.

manager = ConnectionManager()
