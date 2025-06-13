from typing import Dict, Optional
import random
import logging
import asyncio
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Player:
    def __init__(self, name: str, client_type: str):
        self.name = name
        self.client_type = client_type
        self.score = 0
        self.is_drawer = False
        self.is_connected = True
        self.last_seen = datetime.now()

class GameState:
    def __init__(self):
        self.players: Dict[str, Player] = {}
        self.current_word: Optional[str] = None
        self.game_started = True  # Iniciar el juego automáticamente
        self.game_paused = False
        self.current_drawer: Optional[str] = None
        self.disconnect_timeout = timedelta(seconds=30)
        self._lock = asyncio.Lock()
        self.words = [
            "casa", "árbol", "sol", "luna", "estrella", "mar", "montaña",
            "río", "nube", "flor", "perro", "gato", "pájaro", "pez",
            "coche", "tren", "avión", "barco", "bicicleta", "moto"
        ]
        self.frontend_connected = False
        self.desktop_connected = False
        
        # Crear jugadores por defecto
        self.default_players = {
            "desktop": Player("Jugador Desktop", "desktop"),
            "frontend": Player("Jugador Web", "frontend")
        }
        
        # Añadir jugadores por defecto al estado del juego
        for player in self.default_players.values():
            self.players[player.name] = player
            if player.client_type == "frontend":
                self.frontend_connected = True
            elif player.client_type == "desktop":
                self.desktop_connected = True
        
        # Seleccionar el primer drawer (jugador desktop)
        self.current_drawer = "Jugador Desktop"
        self.players["Jugador Desktop"].is_drawer = True
        self.current_word = random.choice(self.words)
        logger.info("Juego iniciado automáticamente con jugadores por defecto")

    async def add_player(self, name: str, client_type: str) -> bool:
        """Añade o reconecta un jugador al juego"""
        async with self._lock:
            try:
                logger.info(f"Intentando añadir jugador: {name} ({client_type})")
                logger.info(f"Jugadores actuales: {[p.name for p in self.players.values()]}")
                
                # Verificar si ya existe un jugador del mismo tipo
                if client_type == "frontend" and self.frontend_connected:
                    # Si es un jugador frontend, reemplazar el jugador por defecto
                    default_player = self.default_players["frontend"]
                    if default_player.name in self.players:
                        # Si el jugador por defecto era el drawer, transferir el rol
                        if self.players[default_player.name].is_drawer:
                            self.current_drawer = name
                        del self.players[default_player.name]
                    self.frontend_connected = False
                elif client_type == "desktop" and self.desktop_connected:
                    # Si es un jugador desktop, reemplazar el jugador por defecto
                    default_player = self.default_players["desktop"]
                    if default_player.name in self.players:
                        # Si el jugador por defecto era el drawer, transferir el rol
                        if self.players[default_player.name].is_drawer:
                            self.current_drawer = name
                        del self.players[default_player.name]
                    self.desktop_connected = False
                
                if name in self.players:
                    # Reconexión de jugador existente
                    player = self.players[name]
                    if player.is_connected:
                        logger.warning(f"Jugador {name} ya está conectado")
                        return False
                    player.is_connected = True
                    player.last_seen = datetime.now()
                    logger.info(f"Jugador {name} reconectado")
                else:
                    # Nuevo jugador
                    self.players[name] = Player(name, client_type)
                    logger.info(f"Nuevo jugador {name} añadido")
                    
                    # Actualizar estado de conexión por tipo
                    if client_type == "frontend":
                        self.frontend_connected = True
                    elif client_type == "desktop":
                        self.desktop_connected = True
                
                # Asegurar que siempre haya un drawer cuando hay dos jugadores
                if self.frontend_connected and self.desktop_connected:
                    connected_players = [p for p in self.players.values() if p.is_connected]
                    if len(connected_players) == 2:
                        # Verificar si hay un drawer
                        has_drawer = any(p.is_drawer for p in connected_players)
                        if not has_drawer:
                            # Si no hay drawer, seleccionar uno
                            new_drawer = random.choice(connected_players)
                            new_drawer.is_drawer = True
                            self.current_drawer = new_drawer.name
                            self.current_word = random.choice(self.words)
                            logger.info(f"Nuevo drawer seleccionado: {new_drawer.name}")
                
                logger.info(f"Estado final después de añadir jugador: {self.get_state()}")
                return True
            except Exception as e:
                logger.error(f"Error al añadir jugador {name}: {e}")
                return False

    def mark_player_disconnected(self, player_name: str):
        """Marca un jugador como desconectado"""
        if player_name in self.players:
            player = self.players[player_name]
            player.is_connected = False
            player.last_seen = datetime.now()
            logger.info(f"Jugador {player_name} marcado como desconectado")
            
            # Actualizar estado de conexión por tipo
            if player.client_type == "frontend":
                self.frontend_connected = False
            elif player.client_type == "desktop":
                self.desktop_connected = False
            
            # Si el drawer se desconecta, seleccionar nuevo drawer
            if player_name == self.current_drawer:
                player.is_drawer = False
                self.current_drawer = None
                self.current_word = None
                
                # Si hay otro jugador conectado, hacerlo drawer
                connected_players = [p for p in self.players.values() if p.is_connected]
                if connected_players:
                    new_drawer = connected_players[0]
                    new_drawer.is_drawer = True
                    self.current_drawer = new_drawer.name
                    self.current_word = random.choice(self.words)
                    logger.info(f"Nuevo drawer seleccionado después de desconexión: {new_drawer.name}")
                else:
                    logger.info("No hay jugadores conectados para seleccionar nuevo drawer")
            
            # Pausar el juego si falta algún jugador
            if not (self.frontend_connected and self.desktop_connected):
                self.game_paused = True
                logger.info("Juego pausado por falta de jugadores")

    def get_connected_players_count(self) -> int:
        """Obtiene el número de jugadores conectados"""
        return sum(1 for player in self.players.values() if player.is_connected)

    async def cleanup_disconnected_players(self):
        """Limpia jugadores desconectados después del timeout"""
        async with self._lock:
            now = datetime.now()
            to_remove = []
            
            for name, player in list(self.players.items()):
                if not player.is_connected and (now - player.last_seen) > self.disconnect_timeout:
                    to_remove.append(name)
            
            for name in to_remove:
                del self.players[name]
                logger.info(f"Jugador {name} removido por timeout de desconexión")
            
            # Si quedan menos de 2 jugadores, pausar el juego
            if self.get_connected_players_count() < 2 and self.game_started:
                self.game_paused = True
                logger.info("Juego pausado por falta de jugadores")

    async def select_new_drawer(self):
        """Selecciona un nuevo drawer entre los jugadores conectados"""
        async with self._lock:
            connected_players = [name for name, player in self.players.items() 
                              if player.is_connected]
            
            if not connected_players:
                logger.warning("No hay jugadores conectados para seleccionar drawer")
                return
            
            # Resetear el estado de drawer para todos
            for player in self.players.values():
                player.is_drawer = False
            
            # Seleccionar nuevo drawer
            new_drawer = random.choice(connected_players)
            self.players[new_drawer].is_drawer = True
            self.current_drawer = new_drawer
            logger.info(f"Nuevo drawer seleccionado: {new_drawer}")
            
            # Asignar nueva palabra
            self.current_word = random.choice(self.words)
            logger.info(f"Nueva palabra asignada: {self.current_word}")

    async def handle_guess(self, player_name: str, guess: str) -> bool:
        """Maneja un intento de adivinanza"""
        async with self._lock:
            if not self.game_started or self.game_paused:
                logger.warning(f"Intento de adivinar con juego no activo: {player_name}")
                return False
                
            if player_name not in self.players:
                logger.error(f"Jugador no encontrado: {player_name}")
                return False
                
            player = self.players[player_name]
            if not player.is_connected:
                logger.warning(f"Jugador desconectado intentando adivinar: {player_name}")
                return False
                
            if player.is_drawer:
                logger.warning(f"Drawer intentando adivinar: {player_name}")
                return False
                
            if guess.lower() == self.current_word.lower():
                player.score += 1
                # Dar punto al drawer
                if self.current_drawer in self.players:
                    self.players[self.current_drawer].score += 1
                
                await self.select_new_drawer()
                logger.info(f"Palabra adivinada por {player_name}")
                return True
                
            return False

    def get_state(self):
        """Obtiene el estado actual del juego"""
        return {
            "players": {
                name: {
                    "name": player.name,
                    "score": player.score,
                    "is_drawer": player.is_drawer,
                    "is_connected": player.is_connected,
                    "client_type": player.client_type
                }
                for name, player in self.players.items()
            },
            "current_word": self.current_word if self.current_drawer else None,
            "game_started": self.game_started,
            "game_paused": self.game_paused,
            "current_drawer": self.current_drawer
        }

game_state = GameState() 