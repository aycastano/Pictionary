import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  useRef,
} from "react";

interface Player {
  name: string;
  score: number;
  is_drawer: boolean;
  is_connected: boolean;
  client_type: string;
}

interface GameState {
  players: { [key: string]: Player };
  current_word: string | null;
  game_started: boolean;
  game_paused: boolean;
  current_drawer: string | null;
}

interface GameContextType {
  gameState: GameState;
  isDrawer: boolean;
  word: string | null;
  playerName: string;
  socket: WebSocket | null;
  sendGuess: (guess: string) => void;
  clearCanvas: () => void;
  isGameStarted: boolean;
  connectionStatus: "connecting" | "connected" | "disconnected";
  lastError: string | null;
}

const GameContext = createContext<GameContextType | undefined>(undefined);

const WS_URL = "ws://localhost:8000/api/v1/ws";
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY = 3000; // 3 segundos
const INITIAL_CONNECTION_DELAY = 1000; // 1 segundo de espera antes del primer intento

export function GameProvider({ children }: { children: React.ReactNode }) {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<
    "connecting" | "connected" | "disconnected"
  >("disconnected");
  const [gameState, setGameState] = useState<GameState>({
    players: {},
    current_word: null,
    game_started: false,
    game_paused: false,
    current_drawer: null,
  });
  const [playerName] = useState(`Web_${Math.floor(Math.random() * 1000)}`);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const [reconnectTimeout, setReconnectTimeout] = useState<number | null>(null);
  const [lastError, setLastError] = useState<string | null>(null);
  const isConnectingRef = useRef(false);
  const wsRef = useRef<WebSocket | null>(null);
  const connectionTimeoutRef = useRef<number | null>(null);
  const isMountedRef = useRef(true);

  const cleanupWebSocket = useCallback(() => {
    if (wsRef.current) {
      console.log("Limpiando conexión WebSocket existente...");
      const ws = wsRef.current;
      ws.onopen = null;
      ws.onclose = null;
      ws.onerror = null;
      ws.onmessage = null;

      if (
        ws.readyState === WebSocket.OPEN ||
        ws.readyState === WebSocket.CONNECTING
      ) {
        ws.close();
      }
      wsRef.current = null;
    }
    if (connectionTimeoutRef.current) {
      window.clearTimeout(connectionTimeoutRef.current);
      connectionTimeoutRef.current = null;
    }
  }, []);

  const connectWebSocket = useCallback(() => {
    if (!isMountedRef.current) {
      console.log("Componente desmontado, no se intentará conectar");
      return;
    }

    if (isConnectingRef.current) {
      console.log("Ya hay una conexión en progreso, ignorando...");
      return;
    }

    console.log("Iniciando conexión WebSocket...");
    setConnectionStatus("connecting");
    setLastError(null);
    isConnectingRef.current = true;

    // Limpiar cualquier conexión existente
    cleanupWebSocket();

    try {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      // Establecer un timeout para la conexión inicial
      connectionTimeoutRef.current = window.setTimeout(() => {
        if (ws.readyState !== WebSocket.OPEN && isMountedRef.current) {
          console.log("Timeout de conexión inicial alcanzado");
          cleanupWebSocket();
          setConnectionStatus("disconnected");
          setLastError("Timeout de conexión al servidor");
          isConnectingRef.current = false;
        }
      }, 5000); // 5 segundos de timeout

      ws.onopen = () => {
        if (!isMountedRef.current) {
          cleanupWebSocket();
          return;
        }

        console.log("WebSocket conectado, enviando mensaje de unión...");
        if (connectionTimeoutRef.current) {
          window.clearTimeout(connectionTimeoutRef.current);
          connectionTimeoutRef.current = null;
        }
        setConnectionStatus("connected");
        setReconnectAttempts(0);
        setLastError(null);
        isConnectingRef.current = false;
        setSocket(ws);

        // Pequeño delay antes de enviar el mensaje de unión
        setTimeout(() => {
          if (ws.readyState === WebSocket.OPEN && isMountedRef.current) {
            ws.send(
              JSON.stringify({
                type: "join",
                name: playerName,
                client_type: "web",
              })
            );
          }
        }, 100);
      };

      ws.onmessage = (event) => {
        if (!isMountedRef.current) return;

        try {
          const data = JSON.parse(event.data);
          console.log("Mensaje recibido:", data);

          if (data.type === "state") {
            console.log("Estado del juego actualizado:", data.state);
            setGameState(data.state);
          } else if (data.type === "error") {
            console.error("Error del servidor:", data.message);
            setLastError(data.message);
          }
        } catch (error) {
          console.error("Error al procesar mensaje:", error);
          setLastError("Error al procesar mensaje del servidor");
        }
      };

      ws.onerror = (error) => {
        console.error("Error en WebSocket:", error);
        // No actualizamos el estado aquí, esperamos al onclose
      };

      ws.onclose = (event) => {
        if (!isMountedRef.current) return;

        console.log("Conexión WebSocket cerrada", event.code, event.reason);
        cleanupWebSocket();
        setConnectionStatus("disconnected");
        setSocket(null);
        isConnectingRef.current = false;

        // Manejar diferentes códigos de cierre
        switch (event.code) {
          case 1000: // Cierre normal
            console.log("Conexión cerrada normalmente");
            break;
          case 1006: // Cierre anormal
            console.log(
              "Conexión cerrada anormalmente - Verificando servidor..."
            );
            setLastError(
              "No se pudo conectar al servidor. Verifica que el servidor esté en ejecución."
            );
            break;
          default:
            console.log(`Conexión cerrada con código ${event.code}`);
            setLastError(`Conexión cerrada (código ${event.code})`);
        }

        // Solo intentar reconectar si no fue un cierre normal y no hemos alcanzado el máximo de intentos
        if (
          event.code !== 1000 &&
          reconnectAttempts < MAX_RECONNECT_ATTEMPTS &&
          isMountedRef.current
        ) {
          const delay =
            reconnectAttempts === 0
              ? INITIAL_CONNECTION_DELAY
              : RECONNECT_DELAY;
          console.log(
            `Intentando reconectar en ${delay / 1000} segundos... (Intento ${
              reconnectAttempts + 1
            }/${MAX_RECONNECT_ATTEMPTS})`
          );
          const timeout = window.setTimeout(() => {
            if (isMountedRef.current) {
              setReconnectAttempts((prev) => prev + 1);
              connectWebSocket();
            }
          }, delay);
          setReconnectTimeout(timeout);
        } else if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
          console.error("Se alcanzó el máximo de intentos de reconexión");
          setLastError(
            "No se pudo establecer conexión después de varios intentos. Por favor, recarga la página."
          );
        }
      };
    } catch (error) {
      console.error("Error al crear WebSocket:", error);
      cleanupWebSocket();
      setConnectionStatus("disconnected");
      setLastError("Error al crear conexión WebSocket");
      isConnectingRef.current = false;
    }
  }, [playerName, reconnectAttempts, cleanupWebSocket]);

  // Efecto para la conexión inicial
  useEffect(() => {
    isMountedRef.current = true;

    // Pequeño delay antes del primer intento de conexión
    const initialTimeout = window.setTimeout(() => {
      if (isMountedRef.current) {
        connectWebSocket();
      }
    }, INITIAL_CONNECTION_DELAY);

    return () => {
      isMountedRef.current = false;
      window.clearTimeout(initialTimeout);
      if (reconnectTimeout) {
        window.clearTimeout(reconnectTimeout);
      }
      cleanupWebSocket();
    };
  }, [connectWebSocket, cleanupWebSocket]);

  // Efecto para limpiar la conexión al desmontar
  useEffect(() => {
    return () => {
      if (socket) {
        console.log("Cerrando conexión WebSocket al desmontar...");
        socket.close();
      }
    };
  }, [socket]);

  const isDrawer = gameState.current_drawer === playerName;

  const sendGuess = (guess: string) => {
    if (
      !socket ||
      isDrawer ||
      !gameState.game_started ||
      gameState.game_paused ||
      socket.readyState !== WebSocket.OPEN
    ) {
      console.log("No se puede enviar adivinanza:", {
        socket: !!socket,
        socketState: socket?.readyState,
        isDrawer,
        gameStarted: gameState.game_started,
        gamePaused: gameState.game_paused,
      });
      return;
    }
    console.log("Enviando adivinanza:", guess);
    socket.send(JSON.stringify({ type: "guess", guess }));
  };

  const clearCanvas = () => {
    if (
      !socket ||
      !isDrawer ||
      !gameState.game_started ||
      gameState.game_paused ||
      socket.readyState !== WebSocket.OPEN
    ) {
      console.log("No se puede limpiar el canvas:", {
        socket: !!socket,
        socketState: socket?.readyState,
        isDrawer,
        gameStarted: gameState.game_started,
        gamePaused: gameState.game_paused,
      });
      return;
    }
    console.log("Limpiando canvas");
    socket.send(JSON.stringify({ type: "clear" }));
  };

  return (
    <GameContext.Provider
      value={{
        gameState,
        isDrawer,
        word: isDrawer ? gameState.current_word : null,
        playerName,
        socket,
        sendGuess,
        clearCanvas,
        isGameStarted: gameState.game_started && !gameState.game_paused,
        connectionStatus,
        lastError,
      }}
    >
      {children}
    </GameContext.Provider>
  );
}

export function useGame() {
  const context = useContext(GameContext);
  if (context === undefined) {
    throw new Error("useGame debe ser usado dentro de un GameProvider");
  }
  return context;
}
