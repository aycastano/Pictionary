import React from "react";
import { GameProvider, useGame } from "./context/GameContext";
import DrawingCanvas from "./components/DrawingCanvas";
import GuessBox from "./components/GuessBox";
import PlayerList from "./components/PlayerList";

function Game() {
  const {
    gameState,
    isDrawer,
    word,
    playerName,
    socket,
    connectionStatus,
    lastError,
  } = useGame();

  const getConnectionStatusMessage = () => {
    switch (connectionStatus) {
      case "connecting":
        return "Conectando al servidor...";
      case "connected":
        return "Conectado";
      case "disconnected":
        return "Desconectado - Intentando reconectar...";
    }
  };

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case "connecting":
        return "bg-yellow-500";
      case "connected":
        return "bg-green-500";
      case "disconnected":
        return "bg-red-500";
    }
  };

  return (
    <div className="flex flex-col items-center p-4 gap-4">
      <div className="flex items-center gap-4">
        <h1 className="text-3xl font-bold">🎨 Pictionary</h1>
        <div
          className={`px-2 py-1 rounded ${getConnectionStatusColor()} text-white`}
        >
          {getConnectionStatusMessage()}
        </div>
      </div>

      {lastError && (
        <div className="bg-red-100 border-l-4 border-red-500 p-4 w-full max-w-2xl">
          <p className="text-red-700">Error: {lastError}</p>
        </div>
      )}

      {connectionStatus !== "connected" && !lastError && (
        <div className="bg-yellow-100 border-l-4 border-yellow-500 p-4 w-full max-w-2xl">
          <p className="text-yellow-700">
            {connectionStatus === "connecting"
              ? "Estableciendo conexión con el servidor..."
              : "No se pudo conectar al servidor. Verifica que el servidor esté en ejecución."}
          </p>
        </div>
      )}

      {connectionStatus === "connected" && (
        <>
          {isDrawer && (
            <div className="bg-green-100 border-l-4 border-green-500 p-4 w-full max-w-2xl">
              <p className="text-green-700">
                Tu palabra: <span className="font-bold">{word}</span>
              </p>
            </div>
          )}

          {!isDrawer && <GuessBox />}

          <DrawingCanvas isDrawer={isDrawer} />
          <PlayerList />
        </>
      )}
    </div>
  );
}

export default function App() {
  return (
    <GameProvider>
      <Game />
    </GameProvider>
  );
}
