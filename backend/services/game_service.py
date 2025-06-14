from fastapi.websockets import WebSocket
from models.game import GameState, Player
from api.v1.game_state import game_state
from typing import List, Dict
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Cliente {client_id} conectado")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Cliente {client_id} desconectado")

    async def broadcast(self, message: dict):
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error enviando mensaje a {client_id}: {e}")

    async def handle_message(self, websocket: WebSocket, data: dict, client_id: str):
        try:
            message_type = data.get("type")
            
            if message_type == "join":
                name = data.get("name")
                client_type = data.get("client_type", "web")
                success = await game_state.add_player(name, client_type)
                if success:
                    await self.broadcast({
                        "type": "state",
                        "state": game_state.get_state()
                    })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": "No se pudo unir al juego"
                    })
            
            elif message_type == "draw":
                if game_state.current_drawer == client_id:
                    await self.broadcast({
                        "type": "draw",
                        "x": data.get("x"),
                        "y": data.get("y"),
                        "isStart": data.get("isStart", False)
                    })
            
            elif message_type == "guess":
                guess = data.get("guess")
                name = data.get("name")
                if await game_state.handle_guess(name, guess):
                    await self.broadcast({
                        "type": "correct",
                        "player": name,
                        "word": game_state.current_word
                    })
                    await self.broadcast({
                        "type": "state",
                        "state": game_state.get_state()
                    })
            
            elif message_type == "clear":
                if game_state.current_drawer == client_id:
                    await self.broadcast({
                        "type": "clear"
                    })
            
            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})
                
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            await websocket.send_json({
                "type": "error",
                "message": "Error procesando mensaje"
            })

manager = ConnectionManager()
