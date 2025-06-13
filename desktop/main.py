import sys
import json
import asyncio
import websockets
import tkinter as tk
from tkinter import ttk, messagebox
import random
import logging
from asyncio import Queue
import time
import threading
import queue
from datetime import datetime
import signal

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DrawingGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pictionary Desktop")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Segoe UI", 10))
        self.style.configure("TLabel", font=("Segoe UI", 10))
        
        # Variables de estado
        self.connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.player_name = f"Desktop_{datetime.now().strftime('%H%M%S')}"
        self.is_drawer = False
        self.current_word = None
        self.game_started = False
        self.game_paused = False
        
        # Colas para comunicación entre hilos
        self.message_queue = queue.Queue()
        self.command_queue = queue.Queue()
        
        # Variables de control
        self.running = True
        self.ws = None
        self.ws_task = None
        self.ping_task = None
        self.reconnect_task = None
        self.event_loop = None
        
        # Configurar el manejo de señales
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        
        self.setup_ui()
        self.start_async_tasks()

    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Estado de conexión
        self.status_label = ttk.Label(
            main_frame,
            text="Desconectado",
            foreground="red"
        )
        self.status_label.pack(pady=5)
        
        # Estado del juego
        self.game_status_label = ttk.Label(
            main_frame,
            text="",
            font=("Segoe UI", 10, "bold")
        )
        self.game_status_label.pack(pady=5)
        
        # Canvas
        self.canvas = tk.Canvas(
            main_frame,
            width=600,
            height=400,
            bg="white",
            highlightthickness=1,
            highlightbackground="#cccccc"
        )
        self.canvas.pack(pady=10)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=5)
        
        self.clear_button = ttk.Button(
            button_frame,
            text="Limpiar",
            command=self.clear_canvas,
            state=tk.DISABLED
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Entrada de texto
        self.guess_var = tk.StringVar()
        self.guess_entry = ttk.Entry(
            main_frame,
            textvariable=self.guess_var,
            width=40
        )
        self.guess_entry.pack(pady=5)
        
        self.guess_button = ttk.Button(
            main_frame,
            text="Adivinar",
            command=self.send_guess,
            state=tk.DISABLED
        )
        self.guess_button.pack(pady=5)
        
        # Lista de jugadores
        self.players_listbox = tk.Listbox(
            main_frame,
            width=40,
            height=10
        )
        self.players_listbox.pack(pady=5)
        
        # Configurar eventos del canvas
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)
        
        # Configurar evento de cierre
        self.root.protocol("WM_DELETE_WINDOW", self.handle_shutdown)

    def start_async_tasks(self):
        """Inicia las tareas asíncronas en un hilo separado"""
        def run_async_tasks():
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)
            
            try:
                self.event_loop.run_until_complete(self.async_main())
            except Exception as e:
                logger.error(f"Error en el loop asíncrono: {e}")
            finally:
                self.event_loop.close()
        
        self.async_thread = threading.Thread(target=run_async_tasks, daemon=True)
        self.async_thread.start()

    async def async_main(self):
        """Función principal asíncrona"""
        try:
            await self.connect_websocket()
            
            # Iniciar tareas de mantenimiento
            self.ping_task = asyncio.create_task(self.keep_alive())
            
            # Procesar mensajes
            while self.running:
                try:
                    # Procesar comandos de la UI
                    while not self.command_queue.empty():
                        cmd = self.command_queue.get_nowait()
                        if cmd == "shutdown":
                            await self.cleanup()
                            return
                    
                    # Procesar mensajes del WebSocket
                    if self.ws:
                        try:
                            message = await asyncio.wait_for(
                                self.ws.recv(),
                                timeout=0.1
                            )
                            self.message_queue.put(message)
                        except asyncio.TimeoutError:
                            continue
                        except websockets.exceptions.ConnectionClosed:
                            logger.warning("Conexión WebSocket cerrada")
                            break
                    
                    # Actualizar UI
                    self.root.after(100, self.process_messages)
                    
                    await asyncio.sleep(0.1)
                except Exception as e:
                    logger.error(f"Error en el loop principal: {e}")
                    break
        except Exception as e:
            logger.error(f"Error en async_main: {e}")
        finally:
            await self.cleanup()

    async def connect_websocket(self):
        """Establece la conexión WebSocket"""
        while self.running and self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                self.ws = await websockets.connect(
                    "ws://localhost:8000/api/v1/ws",
                    extra_headers={"User-Agent": "PictionaryDesktop"}
                )
                
                # Enviar mensaje de unión
                await self.ws.send(json.dumps({
                    "type": "join",
                    "name": self.player_name
                }))
                
                self.connected = True
                self.reconnect_attempts = 0
                self.update_ui_state()
                logger.info("Conectado al servidor")
                return
                
            except Exception as e:
                logger.error(f"Error al conectar: {e}")
                self.reconnect_attempts += 1
                if self.reconnect_attempts < self.max_reconnect_attempts:
                    await asyncio.sleep(5)
                else:
                    logger.error("Máximo número de intentos de reconexión alcanzado")
                    self.running = False

    async def keep_alive(self):
        """Mantiene la conexión WebSocket activa"""
        while self.running and self.ws:
            try:
                await asyncio.sleep(15)  # Reducir el intervalo a 15 segundos
                if self.ws:
                    try:
                        await self.ws.ping()
                        logger.debug("Ping enviado al servidor")
                    except Exception as e:
                        logger.error(f"Error al enviar ping: {e}")
                        break
            except Exception as e:
                logger.error(f"Error en keep_alive: {e}")
                break

    async def cleanup(self):
        """Limpia recursos y cierra conexiones"""
        logger.info("Iniciando limpieza de recursos...")
        
        # Cancelar tareas pendientes
        if self.ping_task:
            self.ping_task.cancel()
            try:
                await self.ping_task
            except asyncio.CancelledError:
                pass
        
        if self.reconnect_task:
            self.reconnect_task.cancel()
            try:
                await self.reconnect_task
            except asyncio.CancelledError:
                pass
        
        # Cerrar WebSocket
        if self.ws:
            try:
                await self.ws.close()
            except Exception as e:
                logger.error(f"Error al cerrar WebSocket: {e}")
        
        self.connected = False
        self.update_ui_state()
        logger.info("Limpieza completada")

    def handle_shutdown(self, *args):
        """Maneja el cierre de la aplicación"""
        logger.info("Iniciando cierre de la aplicación...")
        self.running = False
        self.command_queue.put("shutdown")
        
        # Esperar a que se complete la limpieza
        if self.async_thread and self.async_thread.is_alive():
            self.async_thread.join(timeout=5)
        
        self.root.destroy()
        sys.exit(0)

    def update_ui_state(self):
        """Actualiza el estado de la UI según el estado del juego"""
        if not self.connected:
            self.status_label.config(text="Desconectado", foreground="red")
            self.canvas.config(state=tk.DISABLED)
            self.clear_button.config(state=tk.DISABLED)
            self.guess_entry.config(state=tk.DISABLED)
            self.guess_button.config(state=tk.DISABLED)
            return

        self.status_label.config(text="Conectado", foreground="green")
        
        if not self.game_started or self.game_paused:
            self.game_status_label.config(text="Esperando a que comience el juego...")
            self.canvas.config(state=tk.DISABLED)
            self.clear_button.config(state=tk.DISABLED)
            self.guess_entry.config(state=tk.DISABLED)
            self.guess_button.config(state=tk.DISABLED)
            return

        if self.is_drawer:
            self.game_status_label.config(text=f"Tu palabra: {self.current_word}")
            self.canvas.config(state=tk.NORMAL)
            self.clear_button.config(state=tk.NORMAL)
            self.guess_entry.config(state=tk.DISABLED)
            self.guess_button.config(state=tk.DISABLED)
        else:
            self.game_status_label.config(text="Es tu turno de adivinar")
            self.canvas.config(state=tk.DISABLED)
            self.clear_button.config(state=tk.DISABLED)
            self.guess_entry.config(state=tk.NORMAL)
            self.guess_button.config(state=tk.NORMAL)

    def handle_game_state(self, state):
        """Maneja las actualizaciones del estado del juego"""
        try:
            self.game_started = state.get("game_started", False)
            self.game_paused = state.get("game_paused", False)
            
            # Actualizar lista de jugadores
            self.players_listbox.delete(0, tk.END)
            for player_name, player_data in state.get("players", {}).items():
                status = "🖌️" if player_data.get("is_drawer") else "👀"
                score = player_data.get("score", 0)
                self.players_listbox.insert(tk.END, f"{status} {player_name}: {score} puntos")
            
            # Actualizar estado del jugador actual
            current_player = state.get("players", {}).get(self.player_name, {})
            self.is_drawer = current_player.get("is_drawer", False)
            
            # Actualizar palabra si es el dibujante
            if self.is_drawer:
                self.current_word = state.get("current_word")
            
            self.update_ui_state()
            
        except Exception as e:
            logger.error(f"Error al procesar estado del juego: {e}")

    def draw(self, event):
        """Maneja el evento de dibujo"""
        if not self.is_drawer or not self.game_started or self.game_paused:
            return
            
        x, y = event.x, event.y
        if hasattr(self, 'last_x') and hasattr(self, 'last_y'):
            self.canvas.create_line(
                self.last_x, self.last_y, x, y,
                fill="black", width=2, capstyle=tk.ROUND, smooth=tk.TRUE
            )
            
            # Enviar línea al servidor
            if self.ws and self.connected:
                asyncio.run_coroutine_threadsafe(
                    self.ws.send(json.dumps({
                        "type": "draw",
                        "x1": self.last_x,
                        "y1": self.last_y,
                        "x2": x,
                        "y2": y
                    })),
                    self.event_loop
                )
        
        self.last_x, self.last_y = x, y

    def stop_drawing(self, event):
        """Maneja el evento de soltar el botón del mouse"""
        if hasattr(self, 'last_x'):
            del self.last_x
        if hasattr(self, 'last_y'):
            del self.last_y

    def clear_canvas(self):
        """Limpia el canvas"""
        if not self.is_drawer or not self.game_started or self.game_paused:
            return
            
        self.canvas.delete("all")
        if self.ws and self.connected:
            asyncio.run_coroutine_threadsafe(
                self.ws.send(json.dumps({"type": "clear"})),
                self.event_loop
            )

    def send_guess(self):
        """Envía una adivinanza"""
        if self.is_drawer or not self.game_started or self.game_paused:
            return
            
        guess = self.guess_var.get().strip()
        if not guess:
            return
            
        if self.ws and self.connected:
            asyncio.run_coroutine_threadsafe(
                self.ws.send(json.dumps({
                    "type": "guess",
                    "guess": guess
                })),
                self.event_loop
            )
            self.guess_var.set("")

    def process_messages(self):
        """Procesa mensajes de la cola"""
        try:
            while not self.message_queue.empty():
                message = self.message_queue.get_nowait()
                data = json.loads(message)
                
                if data["type"] == "state":
                    self.handle_game_state(data["state"])
                elif data["type"] == "error":
                    messagebox.showerror("Error", data["message"])
                
        except Exception as e:
            logger.error(f"Error al procesar mensajes: {e}")

    def run(self):
        """Inicia la aplicación"""
        self.root.mainloop()

if __name__ == "__main__":
    game = DrawingGame()
    game.run() 