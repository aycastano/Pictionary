from fastapi import WebSocket, WebSocketDisconnect, APIRouter, HTTPException
from typing import Dict, Set, Optional
import json
import logging
import asyncio
from datetime import datetime, timedelta
from .game_state import game_state

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
players = []  # Global y compartido

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.player_connections: Dict[str, str] = {}  # player_name -> client_id
        self.connection_states: Dict[str, bool] = {}  # client_id -> is_connected
        self.last_ping: Dict[str, datetime] = {}  # client_id -> last_ping_time
        self.ping_timeout = timedelta(seconds=30)
        self._lock = asyncio.Lock()
        self._cleanup_task = None
        self.frontend_client = None
        self.desktop_client = None

    async def start_cleanup_task(self):
        """Inicia la tarea de limpieza periódica"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def _cleanup_loop(self):
        """Loop de limpieza periódica de conexiones muertas"""
        while True:
            try:
                await self.cleanup_dead_connections()
                await asyncio.sleep(10)  # Revisar cada 10 segundos
            except Exception as e:
                logger.error(f"Error en cleanup loop: {e}")

    async def cleanup_dead_connections(self):
        """Limpia conexiones que no han respondido al ping"""
        async with self._lock:
            now = datetime.now()
            to_remove = []
            
            for client_id, last_ping in list(self.last_ping.items()):
                if now - last_ping > self.ping_timeout:
                    logger.warning(f"Cliente {client_id} no responde desde {last_ping}")
                    to_remove.append(client_id)
            
            for client_id in to_remove:
                await self.disconnect(client_id)

    async def connect(self, websocket: WebSocket, client_id: str, client_type: str):
        """Establece una nueva conexión WebSocket"""
        logger.info(f"Nueva conexión WebSocket recibida: {client_id} ({client_type})")
        try:
            # Verificar si ya existe una conexión del mismo tipo
            if client_type == "frontend" and self.frontend_client is not None:
                logger.warning("Ya existe una conexión frontend")
                return False
            elif client_type == "desktop" and self.desktop_client is not None:
                logger.warning("Ya existe una conexión desktop")
                return False

            await websocket.accept()
            logger.info(f"Conexión aceptada: {client_id}")
            async with self._lock:
                self.active_connections[client_id] = websocket
                self.connection_states[client_id] = True
                self.last_ping[client_id] = datetime.now()
                
                # Guardar referencia al tipo de cliente
                if client_type == "frontend":
                    self.frontend_client = client_id
                elif client_type == "desktop":
                    self.desktop_client = client_id
                
            return True
        except Exception as e:
            logger.error(f"Error al aceptar conexión: {e}")
            return False

    async def disconnect(self, client_id: str):
        """Maneja la desconexión de un cliente"""
        logger.info(f"Desconexión de WebSocket: {client_id}")
        async with self._lock:
            # Cerrar WebSocket si está abierto
            if client_id in self.active_connections:
                try:
                    await self.active_connections[client_id].close()
                except Exception as e:
                    logger.error(f"Error cerrando WebSocket {client_id}: {e}")
                finally:
                    del self.active_connections[client_id]
            
            # Limpiar estados
            if client_id in self.connection_states:
                del self.connection_states[client_id]
            if client_id in self.last_ping:
                del self.last_ping[client_id]
            
            # Encontrar y marcar como desconectado al jugador asociado
            player_name = None
            for name, cid in list(self.player_connections.items()):
                if cid == client_id:
                    player_name = name
                    break
            
            if player_name:
                logger.info(f"Marcando jugador {player_name} como desconectado")
                game_state.mark_player_disconnected(player_name)
                # Limpiar la conexión del jugador
                if player_name in self.player_connections:
                    del self.player_connections[player_name]

    async def send_game_state(self, websocket: WebSocket, player_name: str = None):
        """Envía el estado del juego a un cliente específico con mensajes personalizados"""
        try:
            state = game_state.get_state()
            logger.info(f"Enviando estado a {player_name or 'todos los clientes'}: {state}")
            
            # Preparar mensaje base
            message = {
                "type": "state",
                "state": state
            }
            
            # Agregar mensaje personalizado si se proporciona el nombre del jugador
            if player_name and player_name in state["players"]:
                player = state["players"][player_name]
                if player["is_drawer"]:
                    message["status_message"] = f"Es tu turno para dibujar: {state['current_word']}"
                else:
                    message["status_message"] = "Es tu turno para adivinar"
            
            await websocket.send_json(message)
            logger.info(f"Estado enviado exitosamente a {player_name or 'todos los clientes'}")
        except Exception as e:
            logger.error(f"Error al enviar estado: {e}")
            raise

    async def broadcast_state(self):
        """Envía el estado del juego a todos los clientes conectados"""
        state = game_state.get_state()
        logger.info(f"Enviando estado a todos los clientes: {state}")
        disconnected_clients = []
        
        # Usar list() para evitar modificar el diccionario durante la iteración
        for client_id, connection in list(self.active_connections.items()):
            try:
                if self.connection_states.get(client_id, False):
                    # Encontrar el jugador asociado a este cliente
                    player_name = None
                    for name, cid in list(self.player_connections.items()):
                        if cid == client_id:
                            player_name = name
                            break
                    
                    await self.send_game_state(connection, player_name)
                    # Actualizar último ping exitoso
                    self.last_ping[client_id] = datetime.now()
            except Exception as e:
                logger.error(f"Error al enviar estado a {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Limpiar conexiones desconectadas después de terminar el envío
        for client_id in disconnected_clients:
            await self.disconnect(client_id)

    def get_client_type(self, headers: dict) -> str:
        """Determina el tipo de cliente basado en los headers"""
        user_agent = headers.get("user-agent", "").lower()
        origin = headers.get("origin", "").lower()
        
        logger.info(f"Headers recibidos - User-Agent: {user_agent}, Origin: {origin}")
        
        if "pictionarydesktop" in user_agent:
            return "desktop"
        elif "localhost:5173" in origin or "localhost:8000" in origin:
            return "frontend"
        return "desktop"  # Por defecto

    def is_connected(self, client_id: str) -> bool:
        """Verifica si un cliente está conectado"""
        return self.connection_states.get(client_id, False)

manager = ConnectionManager()

@router.websocket("/ws")

async def websocket_endpoint(websocket: WebSocket):
    client_id = f"client_{len(manager.active_connections)}"
    
    # Iniciar tarea de limpieza si no está corriendo
    if manager._cleanup_task is None:
        await manager.start_cleanup_task()
    
    # Determinar el tipo de cliente
    client_type = manager.get_client_type(dict(websocket.headers))
    logger.info(f"Tipo de cliente detectado: {client_type}")
    
    # Intentar conectar
    if not await manager.connect(websocket, client_id, client_type):
        return
    
    try:
        # Enviar estado inicial
        await manager.send_game_state(websocket)
        logger.info(f"Estado inicial enviado a {client_id}")

        while True:
            try:
                data = await websocket.receive_text()
                logger.info(f"Datos recibidos: {data}")
                
                try:
                    message = json.loads(data)
                    logger.info(f"Mensaje recibido de {client_id}: {message}")

                    if not manager.is_connected(client_id):
                        logger.warning(f"Cliente {client_id} no está conectado")
                        break

                    # Actualizar último ping
                    manager.last_ping[client_id] = datetime.now()

                    if message["type"] == "join":
                        player_name = message.get("name")
                        if not player_name:
                            logger.error("Error: nombre de jugador no proporcionado")
                            await websocket.send_json({
                                "type": "error",
                                "message": "Nombre de jugador requerido"
                            })
                            continue

                        client_type = manager.get_client_type(dict(websocket.headers))
                        logger.info(f"Jugador {player_name} uniéndose como {client_type}")
                        
                        # Verificar si el jugador ya existe
                        if player_name in manager.player_connections:
                            old_client_id = manager.player_connections[player_name]
                            if old_client_id in manager.active_connections:
                                logger.info(f"Jugador {player_name} reconectando desde {old_client_id} a {client_id}")
                                await manager.active_connections[old_client_id].close()
                                await manager.disconnect(old_client_id)
                        
                        if await game_state.add_player(player_name, client_type):
                            manager.player_connections[player_name] = client_id
                            logger.info(f"Jugador {player_name} añadido/actualizado")
                            # Enviar estado personalizado al jugador reconectado
                            await manager.send_game_state(websocket, player_name)
                            await manager.broadcast_state()
                        else:
                            await websocket.send_json({
                                "type": "error",
                                "message": "No se pudo unir al juego"
                            })

                    elif message["type"] == "guess":
                        if not game_state.game_started or game_state.game_paused:
                            await websocket.send_json({
                                "type": "error",
                                "message": "El juego no está activo"
                            })
                            continue
                            
                        player_name = None
                        for name, cid in list(manager.player_connections.items()):
                            if cid == client_id:
                                player_name = name
                                break
                        
                        if not player_name:
                            logger.error("Error: jugador no encontrado para adivinar")
                            continue
                            
                        if await game_state.handle_guess(player_name, message["guess"]):
                            await manager.broadcast_state()

                    elif message["type"] == "draw":
                        player_name = None
                        for name, cid in list(manager.player_connections.items()):
                            if cid == client_id:
                                player_name = name
                                break
                        
                        if not player_name:
                            logger.error("Error: jugador no encontrado para dibujar")
                            continue
                            
                        if player_name == game_state.current_drawer:
                            await manager.broadcast_state()
                        else:
                            await websocket.send_json({
                                "type": "error",
                                "message": "No es tu turno para dibujar"
                            })

                    elif message["type"] == "clear":
                        player_name = None
                        for name, cid in list(manager.player_connections.items()):
                            if cid == client_id:
                                player_name = name
                                break
                        
                        if not player_name:
                            logger.error("Error: jugador no encontrado para limpiar")
                            continue
                            
                        if player_name == game_state.current_drawer:
                            await manager.broadcast_state()
                        else:
                            await websocket.send_json({
                                "type": "error",
                                "message": "No es tu turno para dibujar"
                            })
                    else:
                        logger.warning(f"Tipo de mensaje desconocido: {message['type']}")

                except json.JSONDecodeError as e:
                    logger.error(f"Error decodificando mensaje: {data}, Error: {e}")
                    continue

            except WebSocketDisconnect:
                logger.info(f"Cliente {client_id} desconectado")
                await manager.disconnect(client_id)
                break
            except Exception as e:
                logger.error(f"Error en el loop principal: {e}")
                break

    finally:
        logger.info(f"Cerrando conexión de {client_id}")
        await manager.disconnect(client_id)
        await manager.broadcast_state()
